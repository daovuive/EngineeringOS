import json
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from engineering_os.config import ProjectPaths, load_runtime_config
from engineering_os.ingestion import ingest_bytes
from engineering_os.knowledge import load_index
from engineering_os.llm import get_embedding_contract
from engineering_os.pdf import PDFExtractionError, read_pdf_chunk_drafts
from engineering_os.retrieval import citation_source


class FakeRuntime:
    def embed(self, text: str) -> list[float]:
        return [float(len(text)), 1.0]


def pdf_bytes(*pages: str | None) -> bytes:
    writer = PdfWriter()
    writer.add_metadata({"/Title": "Vehicle Design", "/Author": "EngineeringOS"})
    for text in pages:
        page = writer.add_blank_page(width=612, height=792)
        if text is None:
            continue
        font = DictionaryObject(
            {
                NameObject("/F1"): DictionaryObject(
                    {
                        NameObject("/Type"): NameObject("/Font"),
                        NameObject("/Subtype"): NameObject("/Type1"),
                        NameObject("/BaseFont"): NameObject("/Helvetica"),
                    }
                )
            }
        )
        page[NameObject("/Resources")] = DictionaryObject(
            {NameObject("/Font"): font}
        )
        stream = DecodedStreamObject()
        safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream.set_data(f"BT /F1 12 Tf 72 720 Td ({safe}) Tj ET".encode("latin-1"))
        page[NameObject("/Contents")] = stream
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def encrypted_pdf_bytes(user_password: str) -> bytes:
    reader = PdfReader(BytesIO(pdf_bytes("Encrypted vehicle evidence")))
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    writer.encrypt(user_password=user_password, owner_password="owner-secret")
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


class PDFIngestionTests(TestCase):
    def _project(self, temporary: str) -> ProjectPaths:
        root = Path(temporary)
        (root / "knowledge/inbox").mkdir(parents=True)
        (root / "runtime/index").mkdir(parents=True)
        (root / "configs/ai").mkdir(parents=True)
        (root / "configs/settings.json").write_text(
            json.dumps(
                {
                    "project": {"language": "en"},
                    "knowledge": {
                        "root": "knowledge",
                        "index": "runtime/index/knowledge.json",
                        "ingestion": {
                            "directory": "knowledge/inbox",
                            "maxBytes": 4096,
                        },
                        "pdf": {"enabled": True, "ocrEnabled": False},
                    },
                }
            ),
            encoding="utf-8",
        )
        (root / "configs/ai/providers.json").write_text(
            json.dumps(
                {"providers": {"fake": {"type": "ollama", "endpoint": "http://localhost:1"}}}
            ),
            encoding="utf-8",
        )
        (root / "configs/ai/models.json").write_text(
            json.dumps(
                {"models": {"embedding": {"provider": "fake", "model": "fake", "dimensions": 2}}}
            ),
            encoding="utf-8",
        )
        (root / "configs/ai/runtime.json").write_text(
            json.dumps({"defaultProvider": "fake", "options": {}}),
            encoding="utf-8",
        )
        return ProjectPaths(root=root)

    def test_text_pdf_is_preserved_indexed_and_cited_by_page(self) -> None:
        with TemporaryDirectory() as temporary:
            paths = self._project(temporary)
            original = pdf_bytes("REQ-SDV-0012 vehicle status", "Second page evidence")
            result = ingest_bytes(
                paths,
                original,
                source_name="vehicle-design.pdf",
                runtime=FakeRuntime(),
            )
            self.assertEqual(result.indexing_state, "indexed")
            self.assertEqual((paths.root / result.document_path).read_bytes(), original)
            contract = get_embedding_contract(load_runtime_config(paths))
            chunks = load_index(
                paths.root / "runtime/index/knowledge.json",
                embedding_contract=contract,
            )
            self.assertEqual([chunk.page_start for chunk in chunks], [1, 2])
            self.assertTrue(all(chunk.document_type == "pdf" for chunk in chunks))
            self.assertEqual(chunks[0].document_title, "Vehicle Design")
            self.assertEqual(chunks[0].document_author, "EngineeringOS")
            self.assertEqual(
                citation_source(chunks[0]),
                "inbox/vehicle-design.pdf#page=1",
            )

    def test_blank_scanned_pdf_fails_without_indexing_garbage(self) -> None:
        with TemporaryDirectory() as temporary:
            paths = self._project(temporary)
            result = ingest_bytes(
                paths,
                pdf_bytes(None),
                source_name="scan.pdf",
                runtime=FakeRuntime(),
            )
            self.assertEqual(result.indexing_state, "failed")
            self.assertIn("OCR is required", result.error or "")
            self.assertFalse((paths.root / "runtime/index/knowledge.json").exists())

    def test_malformed_pdf_fails_gracefully(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "broken.pdf"
            path.write_bytes(b"%PDF-not-a-real-document")
            with self.assertRaisesRegex(PDFExtractionError, "malformed|unreadable"):
                read_pdf_chunk_drafts(path, root)

    def test_empty_password_encrypted_pdf_is_readable(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "empty-password.pdf"
            path.write_bytes(encrypted_pdf_bytes(""))
            drafts = read_pdf_chunk_drafts(path, root)
            self.assertEqual([draft.text for draft in drafts], ["Encrypted vehicle evidence"])

    def test_password_protected_pdf_fails_gracefully(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "password-protected.pdf"
            path.write_bytes(encrypted_pdf_bytes("secret"))
            with self.assertRaisesRegex(PDFExtractionError, "Password-protected"):
                read_pdf_chunk_drafts(path, root)
