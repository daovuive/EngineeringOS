from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from engineering_os.chunking import (
    ChunkingConfig,
    estimate_tokens,
    read_markdown_chunk_drafts,
)


class TokenAwareChunkingTests(TestCase):
    def test_long_section_splits_with_overlap_and_stable_ids(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            document = root / "design.md"
            document.write_text(
                "# Architecture\n\n"
                + " ".join(f"alpha{i}" for i in range(20))
                + "\n\n"
                + " ".join(f"beta{i}" for i in range(20)),
                encoding="utf-8",
            )
            config = ChunkingConfig(max_tokens=30, overlap_tokens=5, min_tokens=1)

            first = read_markdown_chunk_drafts(document, root, config=config)
            second = read_markdown_chunk_drafts(document, root, config=config)

            self.assertEqual(len(first), 2)
            overlap = set(first[0].text.split()) & set(first[1].text.split())
            self.assertGreaterEqual(len(overlap), 5)
            self.assertEqual([item.chunk_id for item in first], [item.chunk_id for item in second])
            self.assertTrue(all(estimate_tokens(item.text) <= 30 for item in first))

    def test_heading_hierarchy_and_frontmatter_metadata_survive(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            document = root / "projects/eos/architecture.md"
            document.parent.mkdir(parents=True)
            document.write_text(
                "---\n"
                "language: en\n"
                "project: EngineeringOS\n"
                "version: 2.0\n"
                "tags: [rag, hybrid]\n"
                "document_type: architecture\n"
                "---\n"
                "# Platform\n\n## Retrieval\n\nExact identifier REQ-SDV-0012.",
                encoding="utf-8",
            )

            chunks = read_markdown_chunk_drafts(document, root)

            self.assertEqual(len(chunks), 1)
            chunk = chunks[0]
            self.assertEqual(chunk.heading, "Retrieval")
            self.assertEqual(chunk.heading_path, ("Platform", "Retrieval"))
            self.assertEqual(chunk.document_type, "architecture")
            self.assertEqual(chunk.language, "en")
            self.assertEqual(chunk.project, "EngineeringOS")
            self.assertEqual(chunk.version, "2.0")
            self.assertEqual(chunk.tags, ("rag", "hybrid"))
            self.assertEqual(chunk.chunk_index, 0)
            self.assertTrue(chunk.document_id)
            self.assertTrue(chunk.chunk_id)

    def test_small_section_and_code_block_remain_intact(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            document = root / "code.md"
            body = "Use this code:\n\n```python\ndef search_index():\n    return []\n```"
            document.write_text(f"# API\n\n{body}", encoding="utf-8")

            chunks = read_markdown_chunk_drafts(document, root)

            self.assertEqual(len(chunks), 1)
            self.assertEqual(chunks[0].text, body)

    def test_invalid_chunking_configuration_is_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "overlap"):
            ChunkingConfig.from_settings(
                {"knowledge": {"chunking": {"maxTokens": 10, "overlapTokens": 10}}}
            )
