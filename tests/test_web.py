import http.client
import json
import threading
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from engineering_os.config import ProjectPaths
from engineering_os.knowledge import KnowledgeChunk
from engineering_os.rag import INSUFFICIENT_EVIDENCE, RAGResponse, RetrievedContext
from engineering_os.web import (
    MAX_REQUEST_BODY_BYTES,
    MAX_QUERY_CHARACTERS,
    DEFAULT_HOST,
    create_server,
)


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

    def test_stylesheet_is_served(self) -> None:
        status, body, content_type = self._raw_request("GET", "/style.css")

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/css; charset=utf-8")
        self.assertIn(b"textarea", body)

    def test_unknown_static_asset_is_json_404(self) -> None:
        status, payload, content_type = self._request("GET", "/missing.js")

        self.assertEqual(status, 404)
        self.assertEqual(payload["error"]["code"], "not_found")
        self.assertEqual(content_type, "application/json; charset=utf-8")

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
            },
        )
        query_service.assert_called_once_with(self.paths, "What is the design decision?")
        for key in ("retrieved", "chunks", "embeddings", "prompts", "config", "paths"):
            self.assertNotIn(key, payload)
        self.assertNotIn("Raw retrieved content", json.dumps(payload))

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
