import http.client
import json
import threading
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from engineering_os.config import ProjectPaths
from engineering_os.ingestion import IngestionResult, KnowledgeIngestionError
from engineering_os.knowledge import KnowledgeChunk
from engineering_os.rag import INSUFFICIENT_EVIDENCE, RAGResponse, RetrievedContext
from engineering_os.web import (
    MAX_REQUEST_BODY_BYTES,
    MAX_INGESTION_BODY_BYTES,
    MAX_QUERY_CHARACTERS,
    DEFAULT_HOST,
    create_server,
)
from engineering_os.workflows import WorkflowError, WorkflowResponse


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class LocalWebTests(TestCase):
    def setUp(self) -> None:
        self.paths = ProjectPaths(root=PROJECT_ROOT)
        self.server = create_server(self.paths, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self._stop_server)

    def _stop_server(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def _request(
        self,
        method: str,
        path: str,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, dict[str, object], str]:
        status, body, content_type = self._raw_request(method, path, body, headers)
        return status, json.loads(body.decode("utf-8")), content_type

    def _raw_request(
        self,
        method: str,
        path: str,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, bytes, str]:
        connection = http.client.HTTPConnection(
            DEFAULT_HOST,
            self.server.server_address[1],
            timeout=2,
        )
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        response_body = response.read()
        connection.close()
        return response.status, response_body, response.getheader("Content-Type")

    @staticmethod
    def _json_body(payload: object) -> bytes:
        return json.dumps(payload).encode("utf-8")

    def test_health_returns_ok_on_loopback(self) -> None:
        status, payload, content_type = self._request("GET", "/health")

        self.assertEqual(self.server.server_address[0], DEFAULT_HOST)
        self.assertEqual(status, 200)
        self.assertEqual(payload, {"status": "ok"})
        self.assertEqual(content_type, "application/json; charset=utf-8")

    def test_root_serves_local_html_interface(self) -> None:
        status, body, content_type = self._raw_request("GET", "/")

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/html; charset=utf-8")
        self.assertIn(b"<title>EngineeringOS</title>", body)
        self.assertIn(b'href="/style.css"', body)
        self.assertIn(b'src="/app.js"', body)

    def test_app_javascript_is_served(self) -> None:
        status, body, content_type = self._raw_request("GET", "/app.js")

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/javascript; charset=utf-8")
        self.assertIn(b"textContent", body)
        self.assertNotIn(b"innerHTML", body)
        self.assertIn(b'credentials: "same-origin"', body)
        self.assertIn(b"/api/v1/workflows/", body)
        self.assertIn(b"/api/v1/knowledge/ingest", body)
        self.assertIn(b"/api/v1/knowledge/retry-index", body)
        self.assertIn(b"/api/v1/knowledge/documents", body)
        self.assertIn(b"/api/v1/actions", body)
        self.assertIn(b"localStorage", body)
        self.assertNotIn(b"DEMO DATA", body)
        self.assertNotIn(b'get("demo")', body)

    def test_stylesheet_is_served(self) -> None:
        status, body, content_type = self._raw_request("GET", "/style.css")

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/css; charset=utf-8")
        self.assertIn(b"textarea", body)

    def test_root_exposes_file_and_text_ingestion_controls(self) -> None:
        status, body, _ = self._raw_request("GET", "/")

        self.assertEqual(status, 200)
        self.assertIn(b'id="ingest-file"', body)
        self.assertIn(b'id="ingest-text"', body)
        self.assertIn(b'id="auto-index"', body)
        self.assertIn(b'id="retry-index"', body)
        self.assertIn(b'id="open-document"', body)
        self.assertIn(b'id="screen-knowledge"', body)
        self.assertIn(b'id="screen-ask"', body)
        self.assertIn(b'id="screen-engineering"', body)
        self.assertIn(b'id="screen-models"', body)
        self.assertIn(b'id="screen-project"', body)
        self.assertIn(b'id="confirm-dialog"', body)
        self.assertIn(b'id="knowledge-drawer"', body)
        self.assertIn(b'id="activity-drawer"', body)
        self.assertIn(b'id="ask-source-preview"', body)
        self.assertIn(b'id="workflow-download"', body)

    def test_unknown_static_asset_is_json_404(self) -> None:
        status, payload, content_type = self._request("GET", "/missing.js")

        self.assertEqual(status, 404)
        self.assertEqual(payload["error"]["code"], "not_found")
        self.assertEqual(content_type, "application/json; charset=utf-8")

    def test_action_catalog_and_explicit_action_endpoint(self) -> None:
        status, payload, _ = self._request("GET", "/api/v1/actions")
        self.assertEqual(status, 200)
        identifiers = {item["id"] for item in payload["actions"]}
        self.assertIn("project.validate", identifiers)
        self.assertIn("knowledge.ask", identifiers)

        with patch("engineering_os.web.execute_action", return_value={"version": "1.0.0"}) as action:
            status, payload, _ = self._request(
                "POST",
                "/api/v1/actions/project.version",
                self._json_body({"values": {}}),
                {"Content-Type": "application/json"},
            )
        self.assertEqual(status, 200)
        self.assertEqual(payload["result"]["version"], "1.0.0")
        action.assert_called_once_with(self.paths, "project.version", {})

    def test_action_endpoint_validates_origin_body_and_hides_failures(self) -> None:
        status, payload, _ = self._request(
            "POST",
            "/api/v1/actions/project.version",
            self._json_body({"values": {}}),
            {"Content-Type": "application/json", "Origin": "https://evil.example"},
        )
        self.assertEqual(status, 403)
        self.assertEqual(payload["error"]["code"], "forbidden_origin")

        status, payload, _ = self._request(
            "POST",
            "/api/v1/actions/project.version",
            self._json_body({}),
            {"Content-Type": "application/json"},
        )
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"]["code"], "invalid_request")

        with patch("engineering_os.web.execute_action", side_effect=RuntimeError("secret")):
            status, payload, _ = self._request(
                "POST",
                "/api/v1/actions/project.version",
                self._json_body({"values": {}}),
                {"Content-Type": "application/json"},
            )
        self.assertEqual(status, 422)
        self.assertEqual(payload["error"]["code"], "action_failed")
        self.assertNotIn("secret", json.dumps(payload))

    def test_static_routing_does_not_allow_arbitrary_files(self) -> None:
        for path in ("/web_static/index.html", "/configs/settings.json"):
            with self.subTest(path=path):
                status, payload, _ = self._request("GET", path)
                self.assertEqual(status, 404)
                self.assertEqual(payload["error"]["code"], "not_found")

    def test_valid_query_uses_shared_service_and_exposes_only_safe_result(self) -> None:
        retrieved = RetrievedContext(
            1.0,
            KnowledgeChunk(
                "knowledge/design.md",
                "Decision",
                "Raw retrieved content must not be returned by the HTTP adapter.",
                [1.0, 0.0],
            ),
        )
        response = RAGResponse(
            "The authoritative design decision. [Source: knowledge/design.md#Decision]",
            ("knowledge/design.md#Decision",),
            (retrieved,),
        )
        body = self._json_body({"query": "What is the design decision?"})
        with patch("engineering_os.web.query_knowledge", return_value=response) as query_service:
            status, payload, _ = self._request(
                "POST",
                "/api/v1/query",
                body,
                {"Content-Type": "application/json"},
            )

        self.assertEqual(status, 200)
        self.assertEqual(
            payload,
            {
                "status": "ok",
                "answer_status": "answered",
                "answer": response.answer,
                "sources": ["knowledge/design.md#Decision"],
                "source_details": [
                    {
                        "source": "knowledge/design.md#Decision",
                        "path": "knowledge/design.md",
                        "heading": "Decision",
                        "score": 1.0,
                        "excerpt": "Raw retrieved content must not be returned by the HTTP adapter.",
                        "open_url": "/api/v1/knowledge/document?path=knowledge%2Fdesign.md",
                    }
                ],
            },
        )
        query_service.assert_called_once_with(self.paths, "What is the design decision?")
        for key in ("retrieved", "chunks", "embeddings", "prompts", "config", "paths"):
            self.assertNotIn(key, payload)
        self.assertLessEqual(len(payload["source_details"][0]["excerpt"]), 800)

    def test_insufficient_evidence_is_exposed_without_internal_details(self) -> None:
        response = RAGResponse(INSUFFICIENT_EVIDENCE, (), ())
        with patch("engineering_os.web.query_knowledge", return_value=response):
            status, payload, _ = self._request(
                "POST",
                "/api/v1/query",
                self._json_body({"query": "Question"}),
                {"Content-Type": "application/json"},
            )

        self.assertEqual(status, 200)
        self.assertEqual(payload["answer_status"], "insufficient_evidence")
        self.assertEqual(payload["sources"], [])
        self.assertEqual(payload["source_details"], [])

    def test_query_accepts_server_validated_retrieval_controls(self) -> None:
        response = RAGResponse("Answer", (), ())
        with patch("engineering_os.web.query_knowledge", return_value=response) as service:
            status, _, _ = self._request(
                "POST",
                "/api/v1/query",
                self._json_body(
                    {
                        "query": "Question",
                        "limit": 5,
                        "confidence_threshold": 0.7,
                        "include_memory": False,
                        "role": "reasoning",
                    }
                ),
                {"Content-Type": "application/json"},
            )

        self.assertEqual(status, 200)
        service.assert_called_once_with(
            self.paths,
            "Question",
            limit=5,
            confidence_threshold=0.7,
            include_memory=False,
            role="reasoning",
        )

        status, payload, _ = self._request(
            "POST",
            "/api/v1/query",
            self._json_body({"query": "Question", "role": "shell"}),
            {"Content-Type": "application/json"},
        )
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"]["code"], "invalid_query")

    def test_malformed_json_is_rejected(self) -> None:
        status, payload, _ = self._request(
            "POST",
            "/api/v1/query",
            b"{",
            {"Content-Type": "application/json"},
        )

        self.assertEqual(status, 400)
        self.assertEqual(payload["error"], {"code": "invalid_json", "message": "Request body must be valid JSON."})

    def test_missing_query_is_rejected(self) -> None:
        status, payload, _ = self._request(
            "POST",
            "/api/v1/query",
            self._json_body({}),
            {"Content-Type": "application/json"},
        )

        self.assertEqual(status, 400)
        self.assertEqual(payload["error"]["code"], "invalid_request")

    def test_empty_query_is_rejected(self) -> None:
        status, payload, _ = self._request(
            "POST",
            "/api/v1/query",
            self._json_body({"query": " \n\t "}),
            {"Content-Type": "application/json"},
        )

        self.assertEqual(status, 400)
        self.assertEqual(payload["error"]["code"], "invalid_query")

    def test_non_string_query_is_rejected(self) -> None:
        status, payload, _ = self._request(
            "POST",
            "/api/v1/query",
            self._json_body({"query": 42}),
            {"Content-Type": "application/json"},
        )

        self.assertEqual(status, 400)
        self.assertEqual(payload["error"]["code"], "invalid_query")

    def test_oversized_request_is_rejected(self) -> None:
        status, payload, _ = self._request(
            "POST",
            "/api/v1/query",
            b"x" * (MAX_REQUEST_BODY_BYTES + 1),
            {"Content-Type": "application/json"},
        )

        self.assertEqual(status, 413)
        self.assertEqual(payload["error"]["code"], "request_too_large")

    def test_oversized_query_is_rejected(self) -> None:
        status, payload, _ = self._request(
            "POST",
            "/api/v1/query",
            self._json_body({"query": "x" * (MAX_QUERY_CHARACTERS + 1)}),
            {"Content-Type": "application/json"},
        )

        self.assertEqual(status, 413)
        self.assertEqual(payload["error"]["code"], "query_too_large")

    def test_wrong_content_type_is_rejected(self) -> None:
        status, payload, _ = self._request(
            "POST",
            "/api/v1/query",
            self._json_body({"query": "Question"}),
            {"Content-Type": "text/plain"},
        )

        self.assertEqual(status, 415)
        self.assertEqual(payload["error"]["code"], "unsupported_media_type")

    def test_internal_error_does_not_leak_exception_details(self) -> None:
        secret = "/project/configs/ai/providers.json provider password"
        with patch("engineering_os.web.query_knowledge", side_effect=RuntimeError(secret)):
            status, payload, _ = self._request(
                "POST",
                "/api/v1/query",
                self._json_body({"query": "Question"}),
                {"Content-Type": "application/json"},
            )

        self.assertEqual(status, 500)
        self.assertEqual(
            payload,
            {
                "error": {
                    "code": "internal_error",
                    "message": "Unable to process query.",
                }
            },
        )
        self.assertNotIn(secret, json.dumps(payload))

    def test_workflow_endpoint_uses_shared_service(self) -> None:
        response = WorkflowResponse(
            "code-review",
            "# Code Review\n## Findings\nNo critical findings.",
            ("knowledge/review.md#Checks",),
            "retrieved",
        )
        with patch("engineering_os.web.run_workflow", return_value=response) as service:
            status, payload, _ = self._request(
                "POST",
                "/api/v1/workflows/code-review",
                self._json_body(
                    {
                        "input": "diff --git a/a.py b/a.py",
                        "source_name": "change.diff",
                        "with_knowledge": True,
                    }
                ),
                {"Content-Type": "application/json"},
            )

        self.assertEqual(status, 200)
        self.assertEqual(payload["workflow"], "code-review")
        self.assertEqual(payload["retrieval_status"], "retrieved")
        self.assertEqual(payload["sources"], ["knowledge/review.md#Checks"])
        paths, workflow_id, documents = service.call_args.args
        self.assertEqual(paths, self.paths)
        self.assertEqual(workflow_id, "code-review")
        self.assertEqual(documents[0].name, "change.diff")
        self.assertTrue(service.call_args.kwargs["with_knowledge"])

    def test_workflow_rejects_invalid_input_and_hides_internal_errors(self) -> None:
        status, payload, _ = self._request(
            "POST",
            "/api/v1/workflows/requirement-review",
            self._json_body({"input": ""}),
            {"Content-Type": "application/json"},
        )
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"]["code"], "invalid_input")

        with patch(
            "engineering_os.web.run_workflow",
            side_effect=WorkflowError("secret local path"),
        ):
            status, payload, _ = self._request(
                "POST",
                "/api/v1/workflows/adr-assistant",
                self._json_body({"input": "Context and options"}),
                {"Content-Type": "application/json"},
            )
        self.assertEqual(status, 422)
        self.assertEqual(payload["error"]["code"], "workflow_failed")

    def test_file_upload_and_pasted_text_use_shared_ingestion_service(self) -> None:
        result = IngestionResult(
            "knowledge/inbox/demo.md", "saved", "indexed", 2, True
        )
        with patch("engineering_os.web.ingest_bytes", return_value=result) as file_service:
            status, payload, _ = self._request(
                "POST",
                "/api/v1/knowledge/ingest",
                self._json_body(
                    {
                        "content": "# Demo\n\nDistinct fact.",
                        "filename": "Tài liệu demo.md",
                        "auto_index": True,
                    }
                ),
                {"Content-Type": "application/json"},
            )

        self.assertEqual(status, 200)
        self.assertTrue(payload["ready_for_rag"])
        self.assertEqual(payload["chunk_count"], 2)
        file_service.assert_called_once_with(
            self.paths,
            "# Demo\n\nDistinct fact.".encode("utf-8"),
            source_name="Tài liệu demo.md",
            title=None,
            auto_index=True,
        )

        with patch("engineering_os.web.ingest_text", return_value=result) as text_service:
            status, _, _ = self._request(
                "POST",
                "/api/v1/knowledge/ingest",
                self._json_body(
                    {"content": "Pasted fact", "title": "Pasted note", "auto_index": False}
                ),
                {"Content-Type": "application/json"},
            )
        self.assertEqual(status, 200)
        text_service.assert_called_once_with(
            self.paths, "Pasted fact", title="Pasted note", auto_index=False
        )

    def test_ingestion_failure_is_partial_and_retry_is_available(self) -> None:
        failed = IngestionResult(
            "knowledge/inbox/demo.md",
            "saved",
            "failed",
            None,
            None,
            "embedding unavailable",
        )
        with patch("engineering_os.web.ingest_text", return_value=failed):
            status, payload, _ = self._request(
                "POST",
                "/api/v1/knowledge/ingest",
                self._json_body({"content": "Saved content"}),
                {"Content-Type": "application/json"},
            )

        self.assertEqual(status, 207)
        self.assertEqual(payload["status"], "partial")
        self.assertFalse(payload["ready_for_rag"])
        self.assertTrue(payload["retry_available"])

        indexed = IngestionResult(
            "knowledge/inbox/demo.md", "existing", "indexed", 1, True
        )
        with patch("engineering_os.web.retry_document_index", return_value=indexed) as retry:
            status, payload, _ = self._request(
                "POST",
                "/api/v1/knowledge/retry-index",
                self._json_body({"document_path": "knowledge/inbox/README.md"}),
                {"Content-Type": "application/json"},
            )
        self.assertEqual(status, 200)
        self.assertTrue(payload["ready_for_rag"])
        retry.assert_called_once()

    def test_ingestion_rejects_unsafe_inputs_cross_origin_and_large_body(self) -> None:
        for payload in (
            {},
            {"content": ""},
            {"content": "x", "filename": "../escape.md"},
            {"content": "x", "auto_index": "yes"},
        ):
            with self.subTest(payload=payload):
                status, _, _ = self._request(
                    "POST",
                    "/api/v1/knowledge/ingest",
                    self._json_body(payload),
                    {"Content-Type": "application/json"},
                )
                self.assertEqual(status, 400)

        status, payload, _ = self._request(
            "POST",
            "/api/v1/knowledge/ingest",
            self._json_body({"content": "x"}),
            {"Content-Type": "application/json", "Origin": "https://evil.example"},
        )
        self.assertEqual(status, 403)
        self.assertEqual(payload["error"]["code"], "forbidden_origin")

        connection = http.client.HTTPConnection(
            DEFAULT_HOST, self.server.server_address[1], timeout=2
        )
        connection.putrequest("POST", "/api/v1/knowledge/ingest")
        connection.putheader("Content-Type", "application/json")
        connection.putheader("Content-Length", str(MAX_INGESTION_BODY_BYTES + 1))
        connection.endheaders()
        response = connection.getresponse()
        oversized_payload = json.loads(response.read().decode("utf-8"))
        connection.close()
        self.assertEqual(response.status, 413)
        self.assertEqual(oversized_payload["error"]["code"], "request_too_large")

        with patch(
            "engineering_os.web.ingest_text",
            side_effect=KnowledgeIngestionError("unsupported"),
        ):
            status, payload, _ = self._request(
                "POST",
                "/api/v1/knowledge/ingest",
                self._json_body({"content": "x"}),
                {"Content-Type": "application/json"},
            )
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"]["code"], "invalid_ingestion")

    def test_open_document_and_library_are_limited_to_governed_knowledge(self) -> None:
        status, payload, _ = self._request("GET", "/api/v1/knowledge/documents")
        self.assertEqual(status, 200)
        self.assertIn("documents", payload)
        self.assertIn("summary", payload)

        status, body, content_type = self._raw_request(
            "GET", "/api/v1/knowledge/document?path=knowledge%2Finbox%2FREADME.md"
        )
        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/markdown; charset=utf-8")
        self.assertIn(b"knowledge/inbox", body)

        status, payload, _ = self._request(
            "GET", "/api/v1/knowledge/document?path=configs%2Fsettings.json"
        )
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"]["code"], "invalid_document")
        self.assertNotIn("secret", json.dumps(payload))

    def test_unsupported_endpoint_is_json_404(self) -> None:
        status, payload, content_type = self._request("GET", "/api/v1/maintenance")

        self.assertEqual(status, 404)
        self.assertEqual(payload["error"]["code"], "not_found")
        self.assertEqual(content_type, "application/json; charset=utf-8")

    def test_configured_concurrency_limit_is_enforced(self) -> None:
        semaphore = self.server.query_semaphore

        self.assertIsNotNone(semaphore)
        assert semaphore is not None
        self.assertTrue(semaphore.acquire(blocking=False))
        self.assertTrue(semaphore.acquire(blocking=False))
        self.assertFalse(semaphore.acquire(blocking=False))
        semaphore.release()
        semaphore.release()
