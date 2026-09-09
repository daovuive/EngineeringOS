"""Local HTTP adapter for grounded EngineeringOS knowledge queries."""

from __future__ import annotations

import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from engineering_os.config import ProjectPaths, load_runtime_config
from engineering_os.llm import get_default_runtime_definition
from engineering_os.query import query_knowledge
from engineering_os.rag import INSUFFICIENT_EVIDENCE, RAGResponse


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8081
MAX_REQUEST_BODY_BYTES = 16 * 1024
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
        path = urlsplit(self.path).path
        if path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        static_asset = STATIC_ASSETS.get(path)
        if static_asset is not None:
            self._send_static_asset(*static_asset)
            return
        self._send_error(404, "not_found", "Endpoint not found.")

    def do_POST(self) -> None:  # noqa: N802
        if urlsplit(self.path).path != "/api/v1/query":
            self._send_error(404, "not_found", "Endpoint not found.")
            return

        request = self._read_query_request()
        if request is None:
            return

        try:
            semaphore = self.server.query_semaphore
            if semaphore is None:
                response = query_knowledge(self.server.paths, request)
            else:
                with semaphore:
                    response = query_knowledge(self.server.paths, request)
        except Exception:
            self._send_error(500, "internal_error", "Unable to process query.")
            return

        self._send_json(200, _serialize_response(response))

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

    def _read_query_request(self) -> str | None:
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
        if body_length > MAX_REQUEST_BODY_BYTES:
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
        if not isinstance(payload, dict) or set(payload) != {"query"}:
            self._send_error(
                400,
                "invalid_request",
                "Request body must contain only a query field.",
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
        return query

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
    }


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
