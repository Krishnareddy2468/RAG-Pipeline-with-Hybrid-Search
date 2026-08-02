# Pipeline Stages

Each stage below maps to a module under `src/rag_pipeline/`. Modules are currently
scaffolded (empty) and are filled in day by day per the build plan.

## 1. Ingestion — `ingestion/`

| | |
|---|---|
| **In** | Raw files in `data/raw/` (`.md`, `.txt`, `.html`, `.pdf`) |
| **Out** | Normalized `Document` objects with metadata |
| **Modules** | `loaders.py`, `normalizer.py`, `models.py` |

- `loaders.py` — one loader per format, returns raw text + basic metadata (file path,
  page number for PDFs).
- `normalizer.py` — collapses every format into clean plaintext with a consistent
  `Document` shape.
- `models.py` — the `Document` Pydantic model: `source`, `doc_type`, `text`,
  `section_heading`, `page_number`.
- Raw and processed documents are both persisted (`data/raw/`, `data/processed/`) so
  re-indexing never requires re-uploading source files.

## 2. Chunking — `chunking/`

| | |
|---|---|
| **In** | Normalized `Document` objects |
| **Out** | `Chunk` objects (text + metadata) |
| **Modules** | `fixed.py`, `section.py`, `semantic.py` |

Three interchangeable strategies, selected via `CHUNKING_STRATEGY` in `.env`:

- **`fixed.py`** — fixed-size windows with configurable overlap. Baseline.
- **`section.py`** — splits on document structure (markdown headers, HTML tags).
  Structure-aware.
- **`semantic.py`** — splits on topic boundaries using embedding similarity between
  adjacent sentences/paragraphs.

Every chunk records which strategy produced it, so the evaluation framework can
compare strategies head-to-head on the same golden Q&A set (see
[Phase 4 in the build plan](../README.md)).

## 3. Indexing — `indexing/`

| | |
|---|---|
| **In** | `Chunk` objects |
| **Out** | Populated vector store + BM25 index |
| **Modules** | `embeddings.py`, `vector_store.py`, `bm25_store.py`, `dedupe.py` |

- `embeddings.py` — calls the embedding provider (`EMBEDDING_MODEL` in `.env`) per
  chunk.
- `vector_store.py` — persists chunk text, embedding, and metadata to ChromaDB.
- `bm25_store.py` — builds a BM25 index over the *same* chunk corpus, keyed by the
  same chunk IDs as the vector store.
- `dedupe.py` — before inserting a chunk, checks cosine similarity against existing
  chunks; skips/flags near-duplicates above a configurable threshold (default
  `0.95`), so the retriever never wastes a context slot on redundant content.

**Invariant:** dense and sparse indexes must always be built from the identical
chunk set. Re-indexing rebuilds both together, never one in isolation.

## 4. Hybrid Retrieval — `retrieval/`

| | |
|---|---|
| **In** | User question |
| **Out** | Ranked, reranked list of `RetrievalResult` |
| **Modules** | `dense.py`, `sparse.py`, `hybrid.py`, `reranker.py`, `models.py` |

1. `dense.py` — embeds the question, queries the vector store, returns top-k by
   cosine similarity (default `k=10`).
2. `sparse.py` — runs the question through BM25, returns top-k by BM25 score
   (default `k=10`).
3. `hybrid.py` — merges both ranked lists with **Reciprocal Rank Fusion (RRF)**.
   Weighting between dense and sparse is configurable (default `0.7 / 0.3`).
4. `reranker.py` — takes the top ~20 fused candidates and rescoring them against the
   actual question (cross-encoder or LLM-as-judge), keeping the final top 5.

Every result carries: chunk id, text, source, dense rank, sparse rank, fused score,
rerank score, and final rank — enough to debug *why* a chunk was or wasn't
retrieved.

## 5. Generation & Citations — `generation/`

| | |
|---|---|
| **In** | Question + top 5 reranked chunks |
| **Out** | Answer with inline citations + confidence score |
| **Modules** | `prompts.py`, `answer.py`, `citations.py`, `confidence.py` |

- `prompts.py` — the grounded-generation system prompt: answer only from provided
  context, cite chunks as `[1]`, `[2]`, say explicitly when context is
  insufficient.
- `answer.py` — calls the LLM (`LLM_MODEL` in `.env`) with numbered context blocks,
  parses the structured response.
- `citations.py` — verifies each citation actually supports the claim it's attached
  to; flags unsupported citations.
- `confidence.py` — combines retrieval confidence, citation coverage, and citation
  verification results into one composite score. Below threshold, the system
  returns a structured "not found" response instead of guessing.

## 6. Evaluation — `evaluation/`

| | |
|---|---|
| **In** | Golden Q&A set (`data/eval/`) + any pipeline configuration |
| **Out** | Scored report per metric, per chunking strategy |
| **Modules** | `dataset.py`, `metrics.py`, `runner.py` |

- `dataset.py` — loads/validates the hand-written golden Q&A set (simple lookups,
  multi-hop, ambiguous, and unanswerable questions).
- `metrics.py` — answer correctness (LLM-as-judge), faithfulness, retrieval
  relevance, citation accuracy.
- `runner.py` — runs the full suite against the current pipeline config and
  produces a comparison report (e.g. fixed vs. section vs. semantic chunking).

## 7. API & Dashboard — `api/`, `dashboard/`

| | |
|---|---|
| **In** | HTTP requests / dashboard interactions |
| **Out** | JSON responses / rendered UI |
| **Modules** | `api/main.py`, `api/routes.py`, `api/schemas.py`, `dashboard/app.py` |

- `POST /v1/ask` — question in, answer + citations + confidence out.
- `POST /v1/ingest` — index new documents.
- `GET /v1/documents` — list indexed documents.
- `GET /v1/health` — liveness check.
- The Streamlit dashboard wraps the same API: ask a question, see the answer with
  clickable citations, inspect retrieved chunks and their scores, and toggle
  hybrid vs. dense-only retrieval side by side.
