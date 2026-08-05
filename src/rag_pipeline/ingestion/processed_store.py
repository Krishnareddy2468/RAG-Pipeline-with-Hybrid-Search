from pathlib import Path

from rag_pipeline.ingestion.models import Document

DEFAULT_PROCESSED_DIR = Path("data/processed")


def save_processed_document(doc: Document, output_dir: Path = DEFAULT_PROCESSED_DIR) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{Path(doc.source_name).stem}.json"
    output_path.write_text(doc.model_dump_json(indent=2), encoding="utf-8")

    return output_path
