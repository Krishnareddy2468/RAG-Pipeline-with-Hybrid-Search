
from pathlib import Path
from uuid import uuid4

from bs4 import BeautifulSoup
from pypdf import PdfReader

from rag_pipeline.ingestion.models import Document
from rag_pipeline.ingestion.normalizer import normalize_text


SUPPORTED_EXTENSIONS = {".txt", ".md", ".html", ".htm", ".pdf"}


def load_document(path: str | Path) -> Document:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}")

    if suffix == ".txt":
        text = load_text(path)
    elif suffix == ".md":
        text = load_markdown(path)
    elif suffix in {".html", ".htm"}:
        text = load_html(path)
    elif suffix == ".pdf":
        text = load_pdf(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    return Document(
        id=str(uuid4()),
        text=normalize_text(text),
        source_path=str(path),
        source_name=path.name,
        file_type=suffix.replace(".", ""),
        metadata={
            "size_bytes": path.stat().st_size,
        },
    )


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_html(path: Path) -> str:
    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    return soup.get_text(separator="\n")


def load_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        pages.append(f"\n\n[Page {page_number}]\n{page_text}")

    return "\n".join(pages)