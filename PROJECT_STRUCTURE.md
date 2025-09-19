# SIH25 - Multilingual College Chatbot

## Project Architecture Overview

```
SIH25/
├── README.md                    # Main setup instructions
├── backend/                     # FastAPI server
│   ├── app/
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── models/             # Database models (SQLAlchemy)
│   │   │   ├── conversation.py # Chat logs, feedback
│   │   │   ├── document.py     # PDF metadata, chunks
│   │   │   ├── admin.py        # Admin users, overrides
│   │   │   └── __init__.py
│   │   ├── routes/             # API endpoints
│   │   │   ├── chat.py         # /ask, /feedback, /forward
│   │   │   ├── admin.py        # CRUD for admin panel
│   │   │   ├── docs.py         # PDF upload/processing
│   │   │   └── __init__.py
│   │   ├── services/           # Business logic
│   │   │   ├── translation.py  # Google Translate + Khasi/Marwadi
│   │   │   ├── vector_search.py# FAISS operations
│   │   │   ├── pdf_processor.py# Text extraction, chunking
│   │   │   ├── voice.py        # Whisper STT, TTS handling
│   │   │   └── __init__.py
│   │   ├── database.py         # SQLite/Postgres connection
│   │   └── config.py           # Environment variables
│   ├── requirements.txt        # Python dependencies
│   ├── data/                   # Storage directory
│   │   ├── pdfs/              # Uploaded PDF files
│   │   ├── faiss_index/       # Vector store
│   │   ├── audio/             # Admin voice responses
│   │   └── database.db        # SQLite file (dev)
│   └── tests/                 # Backend tests
├── frontend/                   # Chat widget (React)
│   ├── src/
│   │   ├── App.jsx            # Main chat component
│   │   ├── main.jsx           # React entry
│   │   └── chat.css           # Widget styling
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── admin-panel/                # Admin interface (your teammate)
│   ├── src/                   # React admin dashboard
│   ├── package.json
│   └── [admin-specific files]
└── docs/                      # Documentation
    ├── API.md                 # API documentation
    └── DEPLOYMENT.md          # Hosting instructions
```

## Database Schema

### conversations
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    user_message TEXT,
    bot_response TEXT,
    language_detected TEXT,
    confidence_score REAL,
    feedback INTEGER,           -- -1=thumbs down, 0=no feedback, 1=thumbs up
    forwarded_to_admin BOOLEAN DEFAULT FALSE,
    admin_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### documents
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename TEXT UNIQUE,
    title TEXT,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER,
    chunk_count INTEGER,
    is_active BOOLEAN DEFAULT TRUE
);
```

### document_chunks
```sql
CREATE TABLE document_chunks (
    id INTEGER PRIMARY KEY,
    document_id INTEGER,
    chunk_text TEXT,
    chunk_index INTEGER,
    embedding_vector BLOB,      -- FAISS vector data
    FOREIGN KEY (document_id) REFERENCES documents (id)
);
```

### admin_overrides
```sql
CREATE TABLE admin_overrides (
    id INTEGER PRIMARY KEY,
    question_pattern TEXT,      -- Pattern to match user questions
    override_response TEXT,     -- Custom admin response
    language_code TEXT,         -- Language for this override
    audio_file_path TEXT,       -- Optional voice response file
    created_by TEXT,           -- Admin username
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

## API Endpoints for Admin Panel

Your teammate needs to implement these admin interface screens that call these APIs:

### 1. Authentication
```
POST /admin/login
POST /admin/logout
GET /admin/me
```

### 2. Document Management
```
GET /admin/documents          # List all PDFs
POST /admin/documents         # Upload new PDF
DELETE /admin/documents/{id}  # Remove PDF
PUT /admin/documents/{id}     # Update PDF metadata
POST /admin/documents/{id}/reprocess  # Re-index PDF
```

### 3. Conversation Logs
```
GET /admin/conversations      # Paginated chat logs
GET /admin/conversations/stats # Usage statistics
GET /admin/conversations/feedback # Thumbs up/down summary
GET /admin/conversations/forwarded # Unresolved chats
POST /admin/conversations/{id}/respond # Admin replies to forwarded chat
```

### 4. Response Management
```
GET /admin/overrides          # Custom Q&A pairs
POST /admin/overrides         # Add new override
PUT /admin/overrides/{id}     # Edit override
DELETE /admin/overrides/{id}  # Remove override
POST /admin/overrides/{id}/audio # Upload voice response
```

### 5. Analytics & Reports
```
GET /admin/analytics/daily    # Daily usage stats
GET /admin/analytics/languages # Language breakdown
GET /admin/analytics/popular  # Most asked questions
GET /admin/analytics/failed   # Questions bot couldn't answer
```

## Admin Panel UI Requirements

### Dashboard Overview
- Total conversations today/week/month
- Language distribution pie chart
- Top 5 most asked questions
- Pending forwarded chats count
- Recent feedback scores

### Document Management Page
- Upload area with drag-and-drop
- Table of uploaded PDFs with:
  - Filename, upload date, file size, chunk count
  - Actions: View, Re-process, Delete
- Processing status indicator
- Preview extracted text from PDFs

### Conversation Logs Page
- Filterable table with:
  - Timestamp, user message, bot response, language, feedback
  - Export to CSV option
- Search functionality
- Filter by date range, language, feedback score

### Response Editor Page
- Add/edit custom Q&A pairs
- Pattern matching tester (test if question matches pattern)
- Multi-language support (add same answer in different languages)
- Voice response upload (MP3/WAV files)
- Preview how response will appear in chat

### Forwarded Chats Page
- List of unanswered questions forwarded by users
- Admin can type response or select from templates
- Mark as resolved when answered
- Optionally add to knowledge base

## Data Flow Between Components

```
Chat Widget (your part) ←→ FastAPI Backend (your part) ←→ Admin Panel (teammate)
                                    ↓
                            SQLite Database
                                    ↓
                            FAISS Vector Store
```

## What Your Teammate Needs to Know

### 1. API Response Formats
All admin API responses follow this format:
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional status message",
  "pagination": { "page": 1, "total": 100 } // For paginated endpoints
}
```

### 2. Authentication
- JWT tokens in Authorization header: `Bearer <token>`
- Token expires in 24 hours
- Admin login with username/password

### 3. File Upload Format
```javascript
// PDF upload
const formData = new FormData();
formData.append('file', pdfFile);
formData.append('title', 'Document Title');

// Voice response upload
const audioData = new FormData();
audioData.append('audio', audioFile);
audioData.append('override_id', '123');
```

### 4. Real-time Updates
- WebSocket connection for live chat monitoring: `ws://localhost:8000/admin/ws`
- Receives new conversations, feedback, forwarded chats in real-time

### 5. Environment Variables
```env
ADMIN_SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./data/database.db
UPLOAD_DIR=./data/pdfs
AUDIO_DIR=./data/audio
```

## Your Development Tasks

1. **Complete chat widget** (current frontend)
   - Add voice button, feedback thumbs, forward button
   - Connect to backend APIs

2. **Expand FastAPI backend**
   - Document upload/processing endpoints
   - Translation pipeline
   - FAISS integration
   - Admin CRUD APIs

3. **PDF Processing Pipeline**
   - Text extraction (PyPDF2/pdfplumber)
   - Chunking and embedding generation
   - FAISS indexing

4. **Voice Integration**
   - Whisper API for speech-to-text
   - Admin audio file serving

## Timeline Coordination

**Week 1**: You finish backend APIs, teammate sets up admin UI framework
**Week 2**: You integrate PDF/voice, teammate builds document management
**Week 3**: You add translation, teammate builds analytics dashboard
**Week 4**: Integration testing and deployment

## Questions for Your Teammate

1. **UI Framework**: React + what UI library? (Material-UI, Ant Design, Chakra UI?)
2. **State Management**: Redux, Zustand, or React Context?
3. **Authentication UI**: Custom login or use a service?
4. **Real-time Updates**: Should admin see live chat conversations as they happen?
5. **Mobile Responsive**: Does admin panel need mobile support?

## Deployment Strategy

- **Frontend Widget**: Vercel/Netlify (can be embedded in any website)
- **Admin Panel**: Same hosting or separate
- **Backend**: Render/Railway (with persistent storage)
- **Database**: Start with SQLite, upgrade to PostgreSQL for production

This structure keeps your chat widget independent while providing all the admin functionality your teammate needs to build.