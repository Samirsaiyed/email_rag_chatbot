# System Architecture

## Overview

The Email RAG Chatbot is a retrieval-augmented generation system that combines hybrid search, conversational memory, and LLM-based query rewriting to answer questions about email threads with grounded citations.

## Architecture Diagram
```mermaid
graph TD
    A[User Interface - Gradio] --> B[FastAPI Layer]
    B --> C[ThreadSession Manager]
    C --> D[Memory Manager]
    C --> E[Query Rewriter]
    C --> F[Hybrid Retriever]
    C --> G[QA Chain]
    E --> H[LangGraph Workflow]
    F --> I[BM25 Retriever]
    F --> J[Vector Retriever - FAISS]
    G --> K[OpenAI/Ollama LLM]
    G --> L[Citation Engine]

## Component Details

### 1. Data Ingestion Pipeline

**Location:** `src/ingestion/`

**Components:**
- **EmailParser:** Parses raw email CSV into structured format
- **AttachmentExtractor:** Extracts text from PDF, DOCX, TXT files
- **ThreadBuilder:** Groups emails into conversation threads
- **Indexer:** Builds BM25 and FAISS indexes per thread

**Flow:**
Raw CSV → EmailParser → ThreadBuilder → AttachmentExtractor → Indexer  
↓  
PDFs/DOCX/TXT → Text Chunks  
↓  
BM25 Index + FAISS Index

**Key Design Decisions:**
- Per-thread indexing for focused search
- Preserve page numbers for PDFs during extraction
- Chunk size: 300-400 tokens with 50 token overlap
- Store rich metadata: thread_id, message_id, doc_type, filename, page_no

### 2. Hybrid Retrieval System

**Location:** `src/retrieval/`

**Components:**
- **BM25Retriever:** Keyword-based sparse retrieval
- **VectorRetriever:** FAISS semantic dense retrieval  
- **HybridRetriever:** Combines both with weighted fusion

**Algorithm:**
```python
# Retrieval fusion
bm25_scores = bm25.search(query, top_k=10)
vector_scores = faiss.search(query_embedding, top_k=10)

# Normalize scores to [0, 1]
bm25_norm = normalize(bm25_scores)
vector_norm = normalize(vector_scores)

# Weighted combination (default: 0.5 each)
final_scores = 0.5 * bm25_norm + 0.5 * vector_norm

# Return top-k
return sort_by_score(final_scores)[:top_k]
```
**Why Hybrid?**  
BM25: Good for exact matches, names, IDs  
Vectors: Good for semantic similarity, paraphrasing  
Together: Robust to query variations

### 3. Memory System

**Location:** `src/memory/`

**Components:**
- **ConversationMemory:** LangChain buffer (last 5 turns)
- **EntityMemory:** Extracts people, dates, amounts, filenames
- **MemoryManager:** Combines both for query rewriting

**Entity Extraction:**
```python
# Simple regex-based extraction
people: r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b'  # John Smith
dates: r'\b\d{4}-\d{2}-\d{2}\b'           # 2001-04-15
amounts: r'\$[\d,]+\b'                    # $45,000
files: r'\b\w+\.(?:pdf|docx|txt)\b'      # budget.pdf
```

**Memory Context Format:**
```python
{
  "conversation_history": "User: What is budget?\nAI: $45,000\n...",
  "entities": {
    "people": ["John", "Sarah"],
    "amounts": ["$45,000"],
    "files": ["budget.pdf"]
  },
  "last_mentioned": {
    "person": "John",
    "file": "budget.pdf"
  }
}
```

### 4. Query Rewriting (LangGraph)

**Location:** `src/graph/`

**Workflow:**
User Query  
↓  
Analyze (check for pronouns/references)  
↓  
Need rewrite? ──No──→ Use original query  
↓ Yes  
LLM Rewrite (inject context from memory)  
↓  
Rewritten Query

**Example:**
Memory: {"amounts": ["$45,000"], "files": ["budget.pdf"]}

User: "Who approved it?"  
↓  
Analyze: Found pronoun "it"  
↓  
Rewrite: "Who approved the $45,000 budget in budget.pdf?"

**LLM Used:** OpenAI gpt-3.5-turbo or Ollama gemma3:1b

### 5. QA Chain with Citations

**Location:** `src/qa/`

**Process:**
- Format retrieved docs with source attribution  
- Pass to LLM with citation instructions  
- LLM generates answer with inline [msg: M-xxx, page: N]  
- Extract citations using regex  
- Return answer + citation metadata

**Prompt Engineering:**
```
Context:
[Document 1] Message: M-abc123, File: budget.pdf, Page: 2
The budget is $45,000...

Question: What is the budget?

CRITICAL: Add [msg: MESSAGE_ID, page: PAGE] after EACH fact.

Answer: The budget is $45,000 [msg: M-abc123, page: 2].
```

**Citation Extraction:**
```python
pattern = r'\[msg:\s*([M\-a-f0-9]+)(?:,\s*page:\s*(\d+))?\]'
citations = re.findall(pattern, answer)
```

### 6. Session Management

**Location:** `src/session/`

**ThreadSession** orchestrates:
- Load retriever for specific thread
- Initialize memory manager
- For each user query:
  - Get memory context
  - Rewrite query
  - Retrieve documents
  - Generate answer
  - Update memory
  - Log to trace file

**State Management:**
- Each session has unique ID  
- Sessions stored in-memory (dict)  
- Session contains: thread_id, retriever, memory, rewriter, qa_chain

### 7. API Layer

**Location:** `src/api/`

**Endpoints:**
- POST /start_session - Create ThreadSession for thread_id
- POST /ask - Process question in session
- POST /reset_session - Clear memory
- GET /health - Check status

**FastAPI Benefits:**
- Auto-generated OpenAPI docs
- Type validation with Pydantic
- Async support for future scaling

### 8. Trace Logging

**Location:** `src/utils/logger.py`

**Events Logged:**
- query_received - User question
- query_rewritten - Rewritten version + reasoning
- retrieval_complete - Retrieved chunks + scores
- answer_generated - Answer + citations
- turn_complete - Total latency breakdown

**Format:** JSONL (one JSON per line)  
**Location:** runs/<timestamp>_<session_id>/trace.jsonl

## Data Flow Example

**Question:** "What is the budget amount?"

1. User → UI → API → ThreadSession
2. ThreadSession.ask():
   - Get memory context (empty on first turn)
   - Query Rewriter: "What is the budget amount?" (no change)
   - Hybrid Retriever:
     * BM25 finds: "budget $45,000" in email
     * Vector finds: similar budget discussions
     * Fusion: Top 5 chunks
   - QA Chain:
     * Format context with sources
     * LLM generates: "The budget is $45,000 [msg: M-xxx, page: 1]"
     * Extract citation
   - Update memory: Add "budget" → "$45,000"
   - Log trace

3. Response → API → UI → User

**Follow-up:** "Who approved it?"
1. Memory now has: {"amounts": ["$45,000"]}
2. Query Rewriter:
   - Detects pronoun "it"
   - Rewrites: "Who approved the $45,000 budget?"
3. Retrieval with rewritten query → Better results
4. Answer: "John approved it [msg: M-yyy]"

## Technology Stack

**Core:**
- Python 3.8+
- LangChain (orchestration)
- LangGraph (query rewriting workflow)

**Retrieval:**
- FAISS (vector search)
- rank-bm25 (keyword search)
- sentence-transformers (embeddings)

**LLM:**
- OpenAI API (gpt-3.5-turbo)
- Ollama (gemma3:1b, local)

**API/UI:**
- FastAPI (REST API)
- Gradio (web interface)
- Uvicorn (ASGI server)

**Storage:**
- JSON files (threads, metadata)
- Pickle (BM25 index)
- FAISS index files
- JSONL (trace logs)

## Design Principles

- Thread Isolation: Each thread has own index for focused search
- Grounding: Every fact must have citation
- Transparency: Full logging of decision process
- Modularity: Components loosely coupled via interfaces
- Configurability: Easy to swap LLM providers or tune weights

## Performance Characteristics

**Latency Breakdown (OpenAI):**
- Query rewrite: ~200ms
- Retrieval: ~50ms
- QA generation: ~800ms
- Total: ~1.2s per query

**Latency Breakdown (Ollama gemma3:1b):**
- Query rewrite: ~3s
- Retrieval: ~50ms
- QA generation: ~15s
- Total: ~18s per query

**Scalability:**
- Current: Single-threaded, in-memory
- 12 threads, 240 emails: ~50MB memory
- Could scale to 100+ threads with same architecture

## Known Limitations

- No persistence: Sessions lost on restart
- Memory constraints: Full indexes in RAM
- Single LLM call: No iterative refinement
- Simple entity extraction: Regex-based, not NER model
- Thread scope only: No cross-thread search by default

## Future Enhancements

- Add persistent session storage (Redis/PostgreSQL)
- Implement streaming responses
- Add reranker for better retrieval
- Use proper NER for entity extraction
- Support multi-thread queries
- Add evaluation metrics (RAGAS)
