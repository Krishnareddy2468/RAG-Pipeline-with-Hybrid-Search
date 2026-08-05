import json
from pathlib import Path

import pytest

from rag_pipeline.ingestion.loaders import load_document
from rag_pipeline.ingestion.processed_store import save_processed_document


RAW_DIR = Path("data/raw")


def test_load_text_document() -> None:
    doc = load_document(RAW_DIR / "company_security_policy.txt")

    assert doc.source_name == "company_security_policy.txt"
    assert doc.file_type == "txt"
    assert "Company Security Policy" in doc.text
    assert doc.metadata["size_bytes"] > 0


def test_load_markdown_document() -> None:
    doc = load_document(RAW_DIR / "developer_onboarding.md")

    assert doc.source_name == "developer_onboarding.md"
    assert doc.file_type == "md"
    assert "Developer Onboarding Guide" in doc.text


def test_load_html_document_removes_script_text() -> None:
    doc = load_document(RAW_DIR / "api_reference.html")

    assert doc.source_name == "api_reference.html"
    assert doc.file_type == "html"
    assert "Internal API Reference" in doc.text
    assert "console.log" not in doc.text
    assert "This script should not be included" not in doc.text


def test_load_pdf_document_extracts_text_per_page() -> None:
    doc = load_document(RAW_DIR / "disaster_recovery_plan.pdf")

    assert doc.source_name == "disaster_recovery_plan.pdf"
    assert doc.file_type == "pdf"
    assert "Disaster Recovery Plan" in doc.text
    assert "Failover target RTO is 30 minutes" in doc.text
    assert "[Page 1]" in doc.text


def test_missing_file_raises_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        load_document(RAW_DIR / "missing.txt")


def test_unsupported_file_type_raises_value_error(tmp_path: Path) -> None:
    unsupported_file = tmp_path / "notes.csv"
    unsupported_file.write_text("name,value\nalpha,1\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_document(unsupported_file)


def test_save_processed_document_writes_json_with_metadata(tmp_path: Path) -> None:
    doc = load_document(RAW_DIR / "company_security_policy.txt")

    output_path = save_processed_document(doc, output_dir=tmp_path)

    assert output_path == tmp_path / "company_security_policy.json"
    assert output_path.exists()

    saved = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved["source_name"] == "company_security_policy.txt"
    assert saved["file_type"] == "txt"
    assert saved["metadata"]["size_bytes"] > 0
    assert "Company Security Policy" in saved["text"]
