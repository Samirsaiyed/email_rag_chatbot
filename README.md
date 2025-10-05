# Email RAG Chatbot with Thread Memory

A Retrieval-Augmented Generation (RAG) chatbot for searching and conversing over email threads with thread-scoped context, entity memory, query rewriting, and grounded citations.

---

## Features

- **Thread-Scoped Search:** Focus queries within specific email threads  
- **Hybrid Retrieval:** Combines BM25 (keyword) and FAISS (semantic) search  
- **Multi-Format Attachments:** Supports PDF, DOCX, and TXT with page-level citations  
- **Conversation Memory:** Tracks entities and resolves pronouns across turns  
- **Query Rewriting:** LLM-powered reformulation for improved retrieval  
- **Grounded Answers:** Every factual claim is cited (message ID + page number)  
- **Trace Logging:** Transparent JSONL logs for debugging and evaluation  

---

## Quick Start

### Prerequisites
- Python 3.8+
- Minimum 4GB RAM
- (Optional) [Ollama](https://ollama.ai) for local LLM inference

---

### Installation

```bash
# Clone repository
git clone https://github.com/Samirsaiyed/email_rag_chatbot.git
cd email_rag_chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

### Setup

#### Option A: OpenAI (recommended for demo)

```bash
# Create .env file
echo "OPENAI_API_KEY=your-key-here" > .env
```

In `src/config.py`, set:
```python
use_ollama = False
```

#### Option B: Ollama (local and free)

```bash
# Install Ollama
https://ollama.ai/download

# Pull a model
ollama pull gemma3:1b
```

In `src/config.py`, set:
```python
use_ollama = True
```

---

### Index the Data

```bash
python scripts/ingest.py
```

*(Skip if using preindexed sample data.)*

---

### Running the System

**Terminal 1 – Start API**
```bash
python scripts/run_api.py
```

**Terminal 2 – Start UI**
```bash
python ui/app.py
```

Then open [http://localhost:7860](http://localhost:7860)

---

## Usage

1. Select a thread from the dropdown (e.g., `T-58ae003b`)  
2. Click **Start Session**  
3. Ask questions such as:
   - "What is the budget amount?"
   - "Who approved it?" (tests pronoun resolution)
   - "What are the technical specifications?"

---

## System Architecture

```text
User Query
    ↓
Query Rewriter (LLM) → Resolve pronouns using memory
    ↓
Hybrid Retriever → BM25 + Vector Search (FAISS)
    ↓
QA Chain (LLM) → Generate answer with citations
    ↓
Response → [msg: M-xxx, page: N]
```

---

## Key Components

| Component | Description |
|------------|-------------|
| **Ingestion** | Email parsing, attachment extraction, thread building |
| **Retrieval** | BM25 + FAISS hybrid with fusion |
| **Memory** | Entity tracking + 5-turn context buffer |
| **Graph** | Query rewriting using LangGraph |
| **QA** | LLM-based answer generation with citation injection |
| **API/UI** | FastAPI backend and Gradio frontend |

---

## API Endpoints

### Start Session
```bash
POST /api/v1/start_session
{
  "thread_id": "T-58ae003b"
}
```

### Ask Question
```bash
POST /api/v1/ask
{
  "session_id": "abc123",
  "question": "What is the budget?",
  "top_k": 5
}
```

### Reset Session
```bash
POST /api/v1/reset_session?session_id=abc123
```

---

## Dataset

- **Source:** Enron Email Dataset (Kaggle)  
- **Threads:** 12  
- **Emails:** 240  
- **Attachments:** 16 (11 PDF, 3 DOCX, 2 TXT)  
- **Date Range:** January – June 2001  

See `docs/DATASET.md` for more details.

---

## Testing

```bash
# Test retrieval pipeline
python scripts/test_retrieval.py

# Test QA chain
python scripts/test_qa_chain.py

# Test query rewriter
python scripts/test_query_rewriter.py
```

---

## Docker Deployment

```bash
docker-compose up
```

- UI available at: http://localhost:7860  
- API available at: http://localhost:8000

---

## Configuration

Edit `src/config.py` to customize:

| Parameter | Description | Default |
|------------|-------------|----------|
| `use_ollama` | Toggle between Ollama/OpenAI | `False` |
| `chunk_size` | Text chunk size | `400` |
| `bm25_weight` | Keyword retrieval weight | `0.5` |
| `vector_weight` | Semantic retrieval weight | `0.5` |
| `max_turns` | Memory context length | `5` |

---

## Project Structure

```text
email-rag-chatbot/
├── data/
│   ├── raw/              # Original emails
│   ├── processed/        # Parsed emails and attachments
│   └── indexes/          # BM25 and FAISS indexes
├── src/
│   ├── ingestion/        # Email parsing and indexing
│   ├── retrieval/        # Hybrid retrieval logic
│   ├── memory/           # Conversation memory
│   ├── graph/            # Query rewriting (LangGraph)
│   ├── qa/               # Answer generation
│   ├── session/          # Thread session manager
│   ├── api/              # FastAPI endpoints
│   └── utils/            # Helpers and logging
├── ui/                   # Gradio interface
├── scripts/              # Ingestion and testing scripts
├── runs/                 # JSONL trace logs
└── docs/                 # Documentation
```

---

## Performance

| Provider | Model | Avg. Response | Cost |
|-----------|--------|----------------|------|
| OpenAI | gpt-3.5-turbo | 1–2 seconds | ~$0.001/query |
| Ollama | gemma3:1b | 15–30 seconds | Free (local) |

---

## Trace Logging Example

```json
{"timestamp": "2025-10-05T15:57:07", "event_type": "query_received", "question": "What is the budget?"}
{"timestamp": "2025-10-05T15:57:08", "event_type": "query_rewritten", "rewritten_query": "What is the specific budget amount?"}
{"timestamp": "2025-10-05T15:57:08", "event_type": "retrieval_complete", "num_docs_retrieved": 5}
{"timestamp": "2025-10-05T15:57:09", "event_type": "answer_generated", "num_citations": 3}
```

---

## Known Limitations

- Ollama inference is slower (15–30 seconds per query)
- Limited dataset (demo includes 16 attachments)
- Citation extraction may occasionally use filenames instead of message IDs
- Thread reconstruction uses heuristics and may not always be perfect

---

## Demo

See `demo_video.mp4` for a walkthrough demonstrating:
[Watch Demo Video](./Demo_video/demo_video.mp4)
- Thread selection and session start  
- Q&A with citations  
- Pronoun resolution ("Who approved it?")  
- Multi-document grounding  

---

## License

MIT License — See `LICENSE`

---

## Acknowledgments

- **Dataset:** Enron Email Dataset (FERC / Kaggle)  
- **Frameworks:** LangChain, FAISS, FastAPI, Gradio  
- **Models:** OpenAI GPT series and Ollama local models

---

> "RAG systems are only as smart as the context you give them."
