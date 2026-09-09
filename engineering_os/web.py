"""Local HTTP adapter for grounded EngineeringOS knowledge queries."""

from __future__ import annotations

import argparse
import json
import threading
from contextlib import nullcontext
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlsplit

from engineering_os.actions import ActionError, action_catalog, execute_action
from engineering_os.config import ProjectPaths, load_runtime_config, load_settings
from engineering_os.ingestion import (
    IngestionResult,
    KnowledgeIngestionError,
    ingest_bytes,
    ingest_text,
    retry_document_index,
)
from engineering_os.llm import get_default_runtime_definition
from engineering_os.library import (
    KnowledgeLibraryError,
    list_knowledge_documents,
    read_knowledge_document,
)
from engineering_os.query import query_knowledge
from engineering_os.rag import INSUFFICIENT_EVIDENCE, RAGResponse
from engineering_os.workflows import (
    WorkflowDocument,
    WorkflowError,
    run_workflow,
    workflow_ids,
)


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8081
MAX_REQUEST_BODY_BYTES = 16 * 1024
MAX_INGESTION_BODY_BYTES = 2 * 1024 * 1024 + 64 * 1024
MAX_QUERY_CHARACTERS = 4_000
STATIC_DIRECTORY = Path(__file__).with_name("web_static")
STATIC_ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}


class LocalQueryServer(ThreadingHTTPServer):
    """Threaded local server with a fixed project root and optional query limit."""

    daemon_threads = True

    def __init__(
        self,
        server_address: tuple[str, int],
        paths: ProjectPaths,
        query_semaphore: threading.BoundedSemaphore | None,
    ) -> None:
        super().__init__(server_address, LocalQueryHandler)
        self.paths = paths
        self.query_semaphore = query_semaphore


class LocalQueryHandler(BaseHTTPRequestHandler):
    """Serve the local interface, health checks, and grounded knowledge queries."""

    server: LocalQueryServer

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        path = parsed.path
        if path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        if path == "/api/v1/knowledge/document":
            self._handle_open_document(parse_qs(parsed.query))
            return
        if path == "/api/v1/knowledge/documents":
            self._handle_list_documents(parse_qs(parsed.query))
            return
        if path == "/api/v1/actions":
            self._send_json(200, {"status": "ok", "actions": action_catalog()})
            return
        static_asset = STATIC_ASSETS.get(path)
        if static_asset is not None:
            self._send_static_asset(*static_asset)
            return
        self._send_error(404, "not_found", "Endpoint not found.")

    def do_POST(self) -> None:  # noqa: N802
        path = urlsplit(self.path).path
        if path == "/api/v1/query":
            self._handle_query()
            return
        if path == "/api/v1/knowledge/ingest":
            self._handle_ingestion()
            return
        if path == "/api/v1/knowledge/retry-index":
            self._handle_retry_index()
            return
        action_prefix = "/api/v1/actions/"
        if path.startswith(action_prefix):
            self._handle_action(path.removeprefix(action_prefix))
            return
        workflow_prefix = "/api/v1/workflows/"
        if path.startswith(workflow_prefix):
            workflow_id = path.removeprefix(workflow_prefix)
            if workflow_id not in workflow_ids():
                self._send_error(404, "not_found", "Workflow not found.")
                return
            self._handle_workflow(workflow_id)
            return
        self._send_error(404, "not_found", "Endpoint not found.")

    def _handle_action(self, action_id: str) -> None:
        if not self._same_origin_mutation():
            return
        payload = self._read_json_request()
        if payload is None:
            return
        if set(payload) != {"values"} or not isinstance(payload.get("values"), dict):
            self._send_error(400, "invalid_request", "Action request requires a values object.")
            return
        try:
            semaphore = self.server.query_semaphore
            with semaphore if semaphore is not None else nullcontext():
                result = execute_action(self.server.paths, action_id, payload["values"])
        except ActionError as error:
            self._send_error(400, "invalid_action", str(error))
            return
        except Exception:
            self._send_error(422, "action_failed", "EOS action could not complete.")
            return
        self._send_json(200, {"status": "ok", "action": action_id, "result": result})

    def _handle_ingestion(self) -> None:
        if not self._same_origin_mutation():
            return
        payload = self._read_json_request(max_bytes=MAX_INGESTION_BODY_BYTES)
        if payload is None:
            return
        allowed = {"content", "filename", "title", "auto_index"}
        if "content" not in payload or not set(payload).issubset(allowed):
            self._send_error(
                400,
                "invalid_request",
                "Ingestion requires content and supports filename, title, and auto_index.",
            )
            return
        content = payload["content"]
        filename = payload.get("filename")
        title = payload.get("title")
        auto_index = payload.get("auto_index", True)
        if not isinstance(content, str) or not content.strip():
            self._send_error(400, "invalid_input", "Content must be non-empty UTF-8 text.")
            return
        if filename is not None and (
            not isinstance(filename, str) or not filename.strip() or Path(filename).name != filename
        ):
            self._send_error(400, "invalid_input", "Filename must be a plain file name.")
            return
        if title is not None and (not isinstance(title, str) or not title.strip()):
            self._send_error(400, "invalid_input", "Title must be non-empty text.")
            return
        if not isinstance(auto_index, bool):
            self._send_error(400, "invalid_input", "auto_index must be a boolean.")
            return
        try:
            semaphore = self.server.query_semaphore
            with semaphore if semaphore is not None else nullcontext():
                if filename is None:
                    result = ingest_text(
                        self.server.paths,
                        content,
                        title=title,
                        auto_index=auto_index,
                    )
                else:
                    result = ingest_bytes(
                        self.server.paths,
                        content.encode("utf-8"),
                        source_name=filename,
                        title=title,
                        auto_index=auto_index,
                    )
        except KnowledgeIngestionError as error:
            self._send_error(400, "invalid_ingestion", str(error))
            return
        except Exception:
            self._send_error(500, "internal_error", "Unable to import knowledge.")
            return
        self._send_json(207 if result.indexing_state == "failed" else 200, _serialize_ingestion(result))

    def _handle_retry_index(self) -> None:
        if not self._same_origin_mutation():
            return
        payload = self._read_json_request()
        if payload is None:
            return
        if set(payload) != {"document_path"} or not isinstance(
            payload.get("document_path"), str
        ):
            self._send_error(400, "invalid_request", "A document_path string is required.")
            return
        try:
            document = _resolve_ingested_document(
                self.server.paths, payload["document_path"]
            )
            semaphore = self.server.query_semaphore
            with semaphore if semaphore is not None else nullcontext():
                result = retry_document_index(
                    self.server.paths,
                    document.relative_to(self.server.paths.root.resolve()).as_posix(),
                )
        except KnowledgeIngestionError as error:
            self._send_error(400, "invalid_ingestion", str(error))
            return
        except Exception:
            self._send_error(500, "internal_error", "Unable to retry knowledge indexing.")
            return
        self._send_json(207 if result.indexing_state == "failed" else 200, _serialize_ingestion(result))

    def _handle_open_document(self, query: dict[str, list[str]]) -> None:
        values = query.get("path")
        if set(query) != {"path"} or values is None or len(values) != 1:
            self._send_error(400, "invalid_request", "One document path is required.")
            return
        try:
            result = read_knowledge_document(self.server.paths, values[0])
            body = result["content"].encode("utf-8")
            filename = result["name"]
        except KnowledgeLibraryError as error:
            self._send_error(400, "invalid_document", str(error))
            return
        except OSError:
            self._send_error(500, "internal_error", "Unable to open knowledge document.")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/markdown; charset=utf-8")
        self.send_header("Content-Disposition", f'inline; filename="{filename}"')
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_list_documents(self, query: dict[str, list[str]]) -> None:
        if not set(query).issubset({"query", "folder"}) or any(
            len(values) != 1 for values in query.values()
        ):
            self._send_error(400, "invalid_request", "Invalid document filters.")
            return
        query_value = query.get("query", [""])[0]
        folder_value = query.get("folder", [""])[0]
        if len(query_value) > 200 or len(folder_value) > 300:
            self._send_error(400, "invalid_request", "Document filter is too long.")
            return
        try:
            result = list_knowledge_documents(
                self.server.paths,
                query=query_value,
                folder=folder_value,
            )
        except KnowledgeLibraryError:
            self._send_error(500, "internal_error", "Unable to list knowledge documents.")
            return
        self._send_json(200, {"status": "ok", **result})

    def _handle_query(self) -> None:
        request = self._read_query_request()
        if request is None:
            return

        query, options = request

        try:
            semaphore = self.server.query_semaphore
            if semaphore is None:
                response = query_knowledge(self.server.paths, query, **options)
            else:
                with semaphore:
                    response = query_knowledge(self.server.paths, query, **options)
        except Exception:
            self._send_error(500, "internal_error", "Unable to process query.")
            return

        self._send_json(200, _serialize_response(response))

    def _handle_workflow(self, workflow_id: str) -> None:
        payload = self._read_json_request()
        if payload is None:
            return
        allowed = {"input", "source_name", "with_knowledge", "knowledge_query"}
        if "input" not in payload or not set(payload).issubset(allowed):
            self._send_error(
                400,
                "invalid_request",
                "Workflow request requires input and supports source_name, "
                "with_knowledge, and knowledge_query.",
            )
            return
        content = payload["input"]
        source_name = payload.get("source_name", "web-input")
        with_knowledge = payload.get("with_knowledge", False)
        knowledge_query = payload.get("knowledge_query")
        if not isinstance(content, str) or not content.strip():
            self._send_error(400, "invalid_input", "Workflow input must be non-empty text.")
            return
        if not isinstance(source_name, str) or not source_name.strip():
            self._send_error(400, "invalid_input", "source_name must be non-empty text.")
            return
        if not isinstance(with_knowledge, bool):
            self._send_error(400, "invalid_input", "with_knowledge must be a boolean.")
            return
        if knowledge_query is not None and (
            not isinstance(knowledge_query, str) or not knowledge_query.strip()
        ):
            self._send_error(400, "invalid_input", "knowledge_query must be non-empty text.")
            return
        try:
            semaphore = self.server.query_semaphore
            if semaphore is None:
                response = run_workflow(
                    self.server.paths,
                    workflow_id,
                    (WorkflowDocument(source_name, content),),
                    with_knowledge=with_knowledge,
                    knowledge_query=knowledge_query,
                )
            else:
                with semaphore:
                    response = run_workflow(
                        self.server.paths,
                        workflow_id,
                        (WorkflowDocument(source_name, content),),
                        with_knowledge=with_knowledge,
                        knowledge_query=knowledge_query,
                    )
        except WorkflowError:
            self._send_error(
                422,
                "workflow_failed",
                "Workflow could not complete with the available input, knowledge, and local model.",
            )
            return
        except Exception:
            self._send_error(500, "internal_error", "Unable to process workflow.")
            return
        self._send_json(
            200,
            {
                "status": "ok",
                "workflow": response.workflow,
                "result": response.result,
                "sources": list(response.sources),
                "retrieval_status": response.retrieval_status,
            },
        )

    def do_DELETE(self) -> None:  # noqa: N802
        self._send_error(404, "not_found", "Endpoint not found.")

    def do_CONNECT(self) -> None:  # noqa: N802
        self._send_error(404, "not_found", "Endpoint not found.")

    def do_HEAD(self) -> None:  # noqa: N802
        self._send_error(404, "not_found", "Endpoint not found.")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send_error(404, "not_found", "Endpoint not found.")

    def do_PATCH(self) -> None:  # noqa: N802
        self._send_error(404, "not_found", "Endpoint not found.")

    def do_PUT(self) -> None:  # noqa: N802
        self._send_error(404, "not_found", "Endpoint not found.")

    def do_TRACE(self) -> None:  # noqa: N802
        self._send_error(404, "not_found", "Endpoint not found.")

    def log_message(self, format: str, *args: object) -> None:
        """Avoid writing user query data to the default HTTP access log."""

    def _read_query_request(self) -> tuple[str, dict[str, Any]] | None:
        payload = self._read_json_request()
        if payload is None:
            return None
        allowed = {
            "query",
            "limit",
            "min_score",
            "confidence_threshold",
            "include_memory",
            "role",
        }
        if "query" not in payload or not set(payload).issubset(allowed):
            self._send_error(
                400,
                "invalid_request",
                "Request body contains unsupported query fields.",
            )
            return None
        query = payload["query"]
        if not isinstance(query, str):
            self._send_error(400, "invalid_query", "Query must be a string.")
            return None
        if not query.strip():
            self._send_error(400, "invalid_query", "Query must not be empty.")
            return None
        if len(query) > MAX_QUERY_CHARACTERS:
            self._send_error(413, "query_too_large", "Query is too large.")
            return None
        options: dict[str, Any] = {}
        limit = payload.get("limit")
        if limit is not None:
            if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 10:
                self._send_error(400, "invalid_query", "limit must be an integer from 1 to 10.")
                return None
            options["limit"] = limit
        for name in ("min_score", "confidence_threshold"):
            value = payload.get(name)
            if value is not None:
                if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
                    self._send_error(400, "invalid_query", f"{name} must be between 0 and 1.")
                    return None
                options[name] = float(value)
        include_memory = payload.get("include_memory")
        if include_memory is not None:
            if not isinstance(include_memory, bool):
                self._send_error(400, "invalid_query", "include_memory must be a boolean.")
                return None
            options["include_memory"] = include_memory
        role = payload.get("role")
        if role is not None:
            if role not in {"rag", "reasoning"}:
                self._send_error(400, "invalid_query", "role must be rag or reasoning.")
                return None
            options["role"] = role
        return query, options

    def _read_json_request(
        self, *, max_bytes: int = MAX_REQUEST_BODY_BYTES
    ) -> dict[str, Any] | None:
        if self.headers.get_content_type() != "application/json":
            self._send_error(
                415,
                "unsupported_media_type",
                "Content-Type must be application/json.",
            )
            return None

        content_length = self.headers.get("Content-Length")
        try:
            body_length = int(content_length) if content_length is not None else -1
        except ValueError:
            body_length = -1
        if body_length < 0:
            self._send_error(400, "invalid_request", "Content-Length is required.")
            return None
        if body_length > max_bytes:
            self._send_error(413, "request_too_large", "Request body is too large.")
            return None

        body = self.rfile.read(body_length)
        if len(body) != body_length:
            self._send_error(400, "invalid_request", "Request body is incomplete.")
            return None
        try:
            payload: Any = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_error(400, "invalid_json", "Request body must be valid JSON.")
            return None
        if not isinstance(payload, dict):
            self._send_error(
                400,
                "invalid_request",
                "Request body must be a JSON object.",
            )
            return None
        return payload

    def _same_origin_mutation(self) -> bool:
        origin = self.headers.get("Origin")
        host = self.headers.get("Host")
        if origin is not None and (not host or urlsplit(origin).netloc != host):
            self._send_error(403, "forbidden_origin", "Mutation requires a same-origin request.")
            return False
        return True

    def _send_error(self, status: int, code: str, message: str) -> None:
        self._send_json(status, {"error": {"code": code, "message": message}})

    def _send_static_asset(self, filename: str, content_type: str) -> None:
        """Serve an explicitly mapped local asset without request path access."""
        try:
            body = (STATIC_DIRECTORY / filename).read_bytes()
        except OSError:
            self._send_error(500, "internal_error", "Unable to load local interface.")
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _serialize_response(response: RAGResponse) -> dict[str, Any]:
    answer_status = (
        "insufficient_evidence"
        if response.answer == INSUFFICIENT_EVIDENCE
        else "answered"
    )
    return {
        "status": "ok",
        "answer_status": answer_status,
        "answer": response.answer,
        "sources": list(response.sources),
        "source_details": [
            {
                "source": f"{item.chunk.path}#{item.chunk.heading}",
                "path": item.chunk.path,
                "heading": item.chunk.heading,
                "score": round(item.score, 4),
                "excerpt": item.chunk.text[:800],
                "open_url": "/api/v1/knowledge/document?"
                + urlencode({"path": item.chunk.path}),
            }
            for item in response.retrieved
            if item.chunk.source_type == "knowledge"
        ],
    }


def _serialize_ingestion(result: IngestionResult) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": "partial" if result.indexing_state == "failed" else "ok",
        "document_path": result.document_path,
        "import_outcome": result.import_outcome,
        "indexing_state": result.indexing_state,
        "chunk_count": result.chunk_count,
        "ready_for_rag": result.ready_for_rag,
        "open_url": "/api/v1/knowledge/document?" + urlencode({"path": result.document_path}),
    }
    if result.error is not None:
        payload["error"] = result.error
        payload["retry_available"] = True
    return payload


def _resolve_ingested_document(paths: ProjectPaths, value: str) -> Path:
    settings = load_settings(paths)
    knowledge = settings.get("knowledge", {})
    ingestion = knowledge.get("ingestion", {}) if isinstance(knowledge, dict) else {}
    inbox = paths.resolve(ingestion.get("directory", "knowledge/inbox")).resolve()
    candidate = paths.resolve(value).resolve()
    try:
        candidate.relative_to(inbox)
    except ValueError as error:
        raise KnowledgeIngestionError("Document path must be inside the ingestion directory.") from error
    if candidate.suffix.lower() != ".md" or not candidate.is_file() or candidate.is_symlink():
        raise KnowledgeIngestionError("Document path must name an imported Markdown file.")
    return candidate


def create_server(
    paths: ProjectPaths,
    *,
    port: int = DEFAULT_PORT,
) -> LocalQueryServer:
    """Create a server bound only to the local loopback address."""
    if not 0 <= port <= 65_535:
        raise ValueError("Port must be between 0 and 65535.")

    runtime_config = load_runtime_config(paths)
    definition = get_default_runtime_definition(runtime_config)
    maximum = definition.provider.max_concurrent_requests
    semaphore = threading.BoundedSemaphore(maximum) if maximum is not None else None
    return LocalQueryServer((DEFAULT_HOST, port), paths, semaphore)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m engineering_os.web",
        description="Local EngineeringOS knowledge query API",
    )
    parser.add_argument("--root", default=".", help="Fixed project root directory.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Local port.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = ProjectPaths(root=Path(args.root).resolve())
    server = create_server(paths, port=args.port)
    host, port = server.server_address
    print(f"EngineeringOS local API listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
