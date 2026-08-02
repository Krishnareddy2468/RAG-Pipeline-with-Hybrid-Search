# RAG Pipeline with Hybrid Search

Building a RAG system over internal docs that uses dense vector search and BM25
keyword search together, fuses the results, and generates answers with citations
it actually checks against the source instead of just trusting the model.

10-day build, a couple hours a day, split between writing the code myself and
using AI to review architecture, explain concepts, and sanity-check decisions.
Right now it's just repo setup and architecture, no real logic yet.

## Why hybrid search

Dense embeddings are good at matching meaning, not so good at matching exact
strings like error codes or config keys. BM25 is the opposite. Combining both
with Reciprocal Rank Fusion covers more ground than either one alone. More on
this in [architecture/tech-stack.md](architecture/tech-stack.md).

## Stack

Python 3.11, FastAPI, Streamlit, ChromaDB, BM25 (`rank_bm25`), OpenAI for
embeddings and generation.

## Layout

```text
src/rag_pipeline/
  ingestion/    document loaders + normalization
  chunking/     fixed / section / semantic chunking
  indexing/     embeddings, vector store, BM25 index, dedup
  retrieval/    dense, sparse, hybrid fusion (RRF), reranking
  generation/   grounded answers, citation verification, confidence scoring
  evaluation/   golden Q&A set, metrics, eval runner
  api/          FastAPI service
  dashboard/    Streamlit UI
```

Every module above is scaffolded but empty right now, gets filled in day by day.
[architecture/pipeline.md](architecture/pipeline.md) has notes on what's supposed
to go in each one.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Then fill in `OPENAI_API_KEY` in `.env`.

## Architecture

Diagram, pipeline stages, and the reasoning behind the bigger design decisions
are in [architecture/](architecture/).
