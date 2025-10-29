# Next.js Frontend Setup

Modern UI for RAG Pipeline using Next.js, TypeScript, and shadcn/ui components.

## Prerequisites

- Node.js >= 18
- npm or yarn

## Installation

```bash
cd frontend/nextjs
npm install
```

## Development

```bash
npm run dev
```

Opens at `http://localhost:3000`

## Build

```bash
npm run build
npm start
```

## Architecture

### Components
- **app/page.tsx** - Main chat interface
  - Session management
  - Document upload & indexing
  - Chat interface with sources

### State Management
- **lib/store.ts** - Zustand store for global state
  - Session ID
  - Messages
  - Loading state
  - Errors

### API Client
- **lib/api.ts** - Axios client for backend API
  - Session endpoints
  - Document endpoints
  - Chat endpoints
  - Health checks

## API Connection

Configure the backend URL:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Features

✅ Session management
✅ Document upload (PDF, TXT, MD, HTML)
✅ Document indexing & vectorization
✅ RAG chat with source citations
✅ Real-time message display
✅ Toast notifications
✅ Responsive Tailwind CSS design
✅ TypeScript for type safety

## Running Both Frontend & Backend

### Terminal 1 - FastAPI Backend
```bash
cd /path/to/rag_frmk
uv run python backend/api.py
```

### Terminal 2 - Next.js Frontend
```bash
cd frontend/nextjs
npm run dev
```

### Terminal 3 - LM Studio
```
Keep LM Studio running with qwen2.5-7b-instruct-1m model
```

## API Endpoints

See `/backend/api.py` for full OpenAPI documentation at `http://localhost:8000/docs`

### Sessions
- `POST /api/sessions` - Create session
- `GET /api/sessions` - List sessions
- `GET /api/sessions/{id}` - Get session info
- `DELETE /api/sessions/{id}` - Delete session

### Documents
- `POST /api/sessions/{id}/documents/upload` - Upload files
- `POST /api/sessions/{id}/documents/index` - Index documents
- `GET /api/sessions/{id}/documents` - Get document info
- `DELETE /api/sessions/{id}/documents/{filename}` - Remove document

### Chat
- `POST /api/sessions/{id}/chat` - Send query
- `GET /api/sessions/{id}/chat/history` - Get chat history
- `DELETE /api/sessions/{id}/chat/history` - Clear history
