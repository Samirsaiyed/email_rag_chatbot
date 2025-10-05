# Dataset Documentation

## Source

**Dataset Name:** Enron Email Dataset  
**Source:** Kaggle  
**Link:** https://www.kaggle.com/datasets/wcukierski/enron-email-dataset  
**License:** Public Domain

## Dataset Description

The Enron Email Dataset contains approximately 500,000 emails from about 150 users, primarily senior management of Enron Corporation. This dataset was made public by the Federal Energy Regulatory Commission during its investigation of Enron's collapse.

## Selection Criteria

### Date Range
- **Start Date:** January 1, 2001
- **End Date:** June 30, 2001
- **Duration:** 6 months
- **Rationale:** This period captures active business communication with coherent email threads

### Thread Selection
We built email threads by grouping messages with:
- Same or similar subject lines (ignoring Re:, Fwd: prefixes)
- Related sender/recipient patterns
- Temporal proximity (within the date range)

### Final Selection
- **Threads:** 12
- **Emails:** 240 (20 emails per thread on average)
- **Attachments:** 16 files across 4 threads
  - 11 PDFs
  - 3 DOCX files
  - 2 TXT files

## Thread Distribution

| Thread ID | Subject | Emails | Attachments |
|-----------|---------|--------|-------------|
| T-58ae003b | PIRA Global Oil / Storage Upgrade | 20 | 6 (5 PDF, 1 DOCX) |
| T-3df8a268 | Axia Energy Partnership | 20 | 4 (2 PDF, 1 DOCX, 1 TXT) |
| T-8b62a250 | El Paso Electric | 20 | 3 (2 PDF, 1 TXT) |
| T-a5f23567 | PG&E California Crisis | 20 | 3 (2 PDF, 1 DOCX) |
| T-b7936ec5 | Enron Metals | 20 | 0 |
| T-46082fd4 | (Various) | 20 | 0 |
| T-fbceeaf4 | (Various) | 20 | 0 |
| T-c797fbf2 | (Various) | 20 | 0 |
| T-95f11b58 | (Various) | 20 | 0 |
| T-9af80adb | (Various) | 20 | 0 |
| T-a7b53a59 | (Various) | 20 | 0 |
| T-f22ca434 | (Various) | 20 | 0 |

## Attachments

Since the original Enron CSV dataset does not include actual attachment files, we created 16 realistic sample attachments based on email content to demonstrate the system's multi-format handling capabilities.

**Attachment Types:**
- **PDF files (11):** Formal documents like contracts, proposals, technical specifications
- **DOCX files (3):** Draft documents, meeting notes, internal memos
- **TXT files (2):** Email forwards, quick notes

**Content Creation:**
All attachments contain realistic business content that aligns with the email thread topics:
- Budget proposals with financial details
- Technical specifications for equipment
- Meeting minutes and action items
- Partnership agreements and credit analyses
- Crisis management memos and risk strategies

## Data Statistics

**Indexed Content:**
- Total emails: 240
- Total attachments: 16
- Total chunks (indexed): ~141 chunks across 4 threads with attachments
- Average chunk size: 300-400 tokens
- Estimated total text: ~50 MB

**Chunk Distribution by Thread:**
- T-58ae003b: 42 chunks (20 emails + 6 attachments)
- T-3df8a268: 35 chunks (20 emails + 4 attachments)
- T-8b62a250: 27 chunks (20 emails + 3 attachments)
- T-a5f23567: 37 chunks (20 emails + 3 attachments)

## Preprocessing

### Email Processing
1. Parse email headers (message_id, from, to, subject, date)
2. Extract plain text body
3. Remove forwarding headers and email signatures
4. Generate unique message IDs (M-xxxxxxxx format)
5. Build thread IDs (T-xxxxxxxx format) based on subject similarity

### Attachment Processing
1. Extract text from PDF files using PyMuPDF
2. Extract text from DOCX files using python-docx
3. Read TXT files directly
4. Preserve page numbers for PDF files
5. Chunk documents into 300-400 token segments with 50 token overlap

### Metadata Storage
Each chunk includes:
- `chunk_id`: Unique identifier
- `thread_id`: Thread membership
- `message_id`: Source email or attachment
- `doc_type`: email, pdf, docx, or txt
- `page_no`: Page number (for PDFs)
- `filename`: Attachment filename (if applicable)

## Known Limitations

1. **Attachment Authenticity:** Sample attachments are created based on email content, not original files
2. **Thread Reconstruction:** Thread grouping is heuristic-based, may not perfectly match original conversation flows
3. **Date Range:** Limited to 6-month window for coherent threads
4. **Scale:** Small subset of full Enron dataset (240 emails vs 500,000+ in complete dataset)

## License & Attribution

The Enron Email Dataset is in the public domain and was released by the Federal Energy Regulatory Commission (FERC).

**Original Source:** FERC  
**Distribution:** Available through multiple academic and public sources  
**Our Use:** Educational/demonstration purposes for RAG system development