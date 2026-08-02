# Tech Stack & Design Decisions

## Tech Stack

| Component | Tool / Library | Why This Choice |
|---|---|---|
| Language | Python 3.11+ | Ecosystem standard for ML/AI tooling |
| Embeddings | OpenAI `text-embedding-3-small` | Cost-effective, high quality, fast |
| Vector store | ChromaDB | File-based, no server to run for a portfolio project |
| Sparse search | BM25 via `rank_bm25` | Exact keyword matching for IDs, error codes, config keys |
| LLM | GPT-4o / GPT-4o-mini | Strong grounding and instruction-following for citations |
| Chunking | Custom fixed / section / semantic splitters | Full control to compare strategies for the eval report |
| API | FastAPI | Async-native, typed, production-grade |
| Dashboard | Streamlit | Fast to build a retrieval/citation debugging UI |
| Evaluation | Custom harness (+ optional RAGAS) | Full control over faithfulness/citation-specific metrics |
| Packaging | Docker + Docker Compose | Reproducible local deployment (added in Phase 5) |
| Version control | Git + GitHub, daily commits | Visible build history for the portfolio story |

## Key Decisions

### Why hybrid search instead of dense-only
Internal documentation mixes prose explanations with exact technical identifiers
(error codes, function names, config keys). Dense embeddings are strong at matching
meaning ("rotate my access token" → "regenerate an API key") but weak at surfacing
an exact string like `AUTH_403_EXPIRED`, which may not be well represented in
embedding space. BM25 catches the exact match every time. Fusing both gives
strictly better recall than either alone, at the cost of one extra retrieval call
per query.

### Why Reciprocal Rank Fusion (RRF) over a raw weighted score merge
Dense (cosine similarity) and sparse (BM25) scores live on different, incompatible
scales, so averaging them directly is meaningless without careful normalization.
RRF sidesteps that by fusing on **rank position** instead of raw score
(`score = sum(1 / (k + rank))` across both lists), which is simple, has one
well-understood tuning knob (`k`), and is the standard approach used by production
hybrid search systems.

### Why a separate reranking pass
RRF fusion is cheap but coarse — it's a good way to narrow ~20 candidates down from
the full corpus, not to pick the best 5. A reranker (cross-encoder or LLM-as-judge)
scores each fused candidate directly against the actual question text, which is
more expensive per-candidate but far more precise, so it's only run on the fused
shortlist rather than the whole corpus.

### Why citation verification instead of trusting the LLM's citations
LLMs will confidently attach a citation marker to a claim it doesn't actually
support. Verifying each `[n]` citation against its source chunk (a second,
narrowly-scoped LLM call: "does this chunk support this specific claim?") is what
turns "the model said it's grounded" into "we checked that it's grounded" — the
difference between a demo and a system a compliance-minded team would trust.

### Why a confidence score and an explicit "I don't know" path
A RAG system that always answers is a RAG system that sometimes hallucinates
fluently. Combining retrieval confidence, citation coverage, and verification
results into one score — and returning a structured "here's what I found, here's
what I couldn't find" response below threshold — is a deliberate tradeoff: fewer
confident-sounding wrong answers, at the cost of occasionally deferring on a
question the system could plausibly have answered.

### Why keep dense and sparse indexes on identical chunk IDs
If the two indexes were built from different chunkings, a citation from one
retriever couldn't be reliably cross-checked against the other, and reranking
would be comparing apples to oranges. Both indexes are always rebuilt together
from the same chunk corpus.
