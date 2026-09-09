import os
import subprocess
import tempfile
from pathlib import Path
from unittest import TestCase


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATUS_SCRIPT = PROJECT_ROOT / "scripts" / "eos-status"


class EosStatusScriptTests(TestCase):
    def _run_status(self, *arguments: str) -> tuple[subprocess.CompletedProcess[str], str]:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            fake_bin = temporary_root / "bin"
            fake_bin.mkdir()
            curl_log = temporary_root / "curl.log"
            curl = fake_bin / "curl"
            curl.write_text(
                """#!/usr/bin/env bash
printf '%s\\n' \"$*\" >> \"$EOS_STATUS_TEST_CURL_LOG\"
case \"$*\" in
  *'/api/v1/query'*) printf '%s' '{\"status\":\"ok\",\"answer_status\":\"answered\",\"answer\":\"Grounded answer\",\"sources\":[\"knowledge/design.md#Decision\"]}' ;;
  *'/api/tags'*) printf '%s' '{\"models\":[{\"name\":\"test-model\",\"size\":1073741824}]}' ;;
  *'/api/version'*) printf '%s' '{\"version\":\"test\"}' ;;
  *'/api/ps'*) printf '%s' '{\"models\":[]}' ;;
  *'/health'*) printf '%s' '200 0.001' ;;
esac
""",
                encoding="utf-8",
            )
            curl.chmod(0o755)
            environment = os.environ.copy()
            environment.update(
                {
                    "PATH": f"{fake_bin}:{environment['PATH']}",
                    "EOS_STATUS_TEST_CURL_LOG": str(curl_log),
                    "EOS_STATUS_PROJECT_ROOT": str(PROJECT_ROOT),
                    "EOS_STATUS_LOCAL_URL": "http://local.test:8081",
                    "EOS_STATUS_OLLAMA_URL": "http://ollama.test:11434",
                    "EOS_STATUS_PUBLIC_URL": "https://public.test",
                }
            )
            result = subprocess.run(
                [str(STATUS_SCRIPT), *arguments],
                cwd=PROJECT_ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
                timeout=10,
            )
            curl_calls = curl_log.read_text(encoding="utf-8") if curl_log.exists() else ""
            return result, curl_calls

    def test_fast_mode_never_calls_the_rag_query_endpoint(self) -> None:
        result, curl_log = self._run_status()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Mode: FAST", result.stdout)
        self.assertIn("EOS health", result.stdout)
        self.assertNotIn("/api/v1/query", curl_log)

    def test_deep_mode_calls_the_local_rag_query_endpoint(self) -> None:
        result, curl_log = self._run_status("--deep")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Mode: DEEP", result.stdout)
        self.assertIn("RAG request", result.stdout)
        self.assertIn("Answer status", result.stdout)
        self.assertIn("Source count", result.stdout)
        self.assertIn("/api/v1/query", curl_log)

    def test_unknown_option_returns_usage_error(self) -> None:
        result, _ = self._run_status("--unexpected")

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "Usage: eos-status [--deep]\n")
