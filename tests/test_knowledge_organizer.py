from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from engineering_os.knowledge_organizer import (
    KnowledgeDestination,
    KnowledgeOrganizationError,
    apply_markdown_organization,
    load_destinations,
    organize_markdown,
    preview_markdown_organization,
)


class FakeRuntime:
    def __init__(self, response: dict[str, object]) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def generate_structured(
        self,
        prompt: str,
        schema: dict[str, object],
        *,
        role: str,
        max_tokens: int | None,
    ) -> dict[str, object]:
        self.calls.append(
            {"prompt": prompt, "schema": schema, "role": role, "max_tokens": max_tokens}
        )
        return self.response


DESTINATIONS = (
    KnowledgeDestination("knowledge/architecture/patterns", "Architecture patterns."),
    KnowledgeDestination("knowledge/personal/lessons-learned", "Personal lessons."),
)


class KnowledgeOrganizerTests(TestCase):
    def _root(self, temporary: str) -> Path:
        root = Path(temporary)
        (root / "knowledge/architecture/patterns").mkdir(parents=True)
        (root / "knowledge/personal/lessons-learned").mkdir(parents=True)
        return root

    def test_copies_to_only_an_allowed_existing_destination(self) -> None:
        with TemporaryDirectory() as temporary:
            root = self._root(temporary)
            source = root / "incoming.md"
            source.write_text("# Circuit breaker\n\nProtect a downstream service.", encoding="utf-8")
            runtime = FakeRuntime(
                {
                    "destination": "knowledge/architecture/patterns",
                    "reason": "The document describes a reusable resilience pattern.",
                }
            )

            result = organize_markdown(source, root, runtime, DESTINATIONS)

            target = root / "knowledge/architecture/patterns/incoming.md"
            self.assertEqual(result.destination, target)
            self.assertEqual(result.action, "copied")
            self.assertTrue(source.exists())
            self.assertEqual(target.read_text(encoding="utf-8"), source.read_text(encoding="utf-8"))
            self.assertEqual(runtime.calls[0]["role"], "reasoning")
            self.assertEqual(runtime.calls[0]["max_tokens"], 300)
            self.assertIn("untrusted data", str(runtime.calls[0]["prompt"]))

    def test_move_and_dry_run_do_not_overwrite_or_delete_unexpectedly(self) -> None:
        with TemporaryDirectory() as temporary:
            root = self._root(temporary)
            source = root / "note.md"
            source.write_text("# Lesson\n\nKeep decisions traceable.", encoding="utf-8")
            runtime = FakeRuntime(
                {
                    "destination": "knowledge/personal/lessons-learned",
                    "reason": "The note records a personal engineering lesson.",
                }
            )

            preview = organize_markdown(source, root, runtime, DESTINATIONS, move=True, dry_run=True)

            self.assertEqual(preview.action, "would_move")
            self.assertTrue(source.exists())
            self.assertFalse(preview.destination.exists())

            result = organize_markdown(source, root, runtime, DESTINATIONS, move=True)

            self.assertEqual(result.action, "moved")
            self.assertFalse(source.exists())
            self.assertTrue(result.destination.exists())

    def test_rejects_invalid_decision_and_existing_destination_file(self) -> None:
        with TemporaryDirectory() as temporary:
            root = self._root(temporary)
            source = root / "note.md"
            source.write_text("# Note\n\nContent", encoding="utf-8")
            invalid_runtime = FakeRuntime({"destination": "knowledge/unknown", "reason": "Nope."})

            with self.assertRaisesRegex(KnowledgeOrganizationError, "invalid knowledge destination"):
                organize_markdown(source, root, invalid_runtime, DESTINATIONS)

            target = root / "knowledge/architecture/patterns/note.md"
            target.write_text("existing", encoding="utf-8")
            valid_runtime = FakeRuntime(
                {
                    "destination": "knowledge/architecture/patterns",
                    "reason": "The document describes an architecture pattern.",
                }
            )
            with self.assertRaisesRegex(KnowledgeOrganizationError, "Refusing to overwrite"):
                organize_markdown(source, root, valid_runtime, DESTINATIONS)

    def test_rejects_misconfigured_destinations(self) -> None:
        with self.assertRaisesRegex(KnowledgeOrganizationError, "under knowledge"):
            load_destinations(
                {"organizer": {"destinations": [{"path": "docs", "description": "Wrong"}]}}
            )

    def test_preview_is_bound_to_document_content_and_selected_destination(self) -> None:
        with TemporaryDirectory() as temporary:
            root = self._root(temporary)
            source = root / "note.md"
            source.write_text("# Pattern\n\nOriginal content.", encoding="utf-8")
            runtime = FakeRuntime(
                {
                    "destination": "knowledge/architecture/patterns",
                    "reason": "The note describes a reusable architecture pattern.",
                }
            )
            preview = preview_markdown_organization(source, root, runtime, DESTINATIONS)

            self.assertEqual(preview.collision, "none")
            self.assertIn("knowledge/personal/lessons-learned", preview.allowed_destinations)
            source.write_text("# Pattern\n\nChanged after preview.", encoding="utf-8")
            with self.assertRaisesRegex(KnowledgeOrganizationError, "preview is stale"):
                apply_markdown_organization(
                    source,
                    root,
                    DESTINATIONS,
                    destination_path="knowledge/architecture/patterns",
                    source_sha256=preview.source_sha256,
                    preview_token=preview.preview_token,
                    reason=preview.reason,
                )

    def test_user_selected_destination_gets_a_new_bound_preview(self) -> None:
        with TemporaryDirectory() as temporary:
            root = self._root(temporary)
            source = root / "note.md"
            source.write_text("# Lesson\n\nReview every preview.", encoding="utf-8")
            runtime = FakeRuntime({})

            preview = preview_markdown_organization(
                source,
                root,
                runtime,
                DESTINATIONS,
                destination_path="knowledge/personal/lessons-learned",
            )
            result = apply_markdown_organization(
                source,
                root,
                DESTINATIONS,
                destination_path="knowledge/personal/lessons-learned",
                source_sha256=preview.source_sha256,
                preview_token=preview.preview_token,
                reason=preview.reason,
            )

            self.assertEqual(result.action, "copied")
            self.assertEqual(len(runtime.calls), 0)
