# System Architecture

## Overview

The Counterparty Recommendation Engine is a full-stack application with an Angular frontend and FastAPI backend.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│                    (Angular + TypeScript)                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Dashboard Component                      │  │
│  │  ┌────────────────┐  ┌──────────────────────────┐   │  │
│  │  │  Left Panel    │  │     Right Panel          │   │  │
│  │  │                │  │                          │   │  │
│  │  │ • Counterparty │  │ • Scorecard              │   │  │
│  │  │   Form         │  │ • Structured Analysis    │   │  │
│  │  │ • Analysis     │  │ • Recommendation Memo    │   │  │
│  │  │   Input        │  │ • Export Options         │   │  │
│  │  │ • Generate Btn │  │                          │   │  │
│  │  └────────────────┘  └──────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           │ HTTP/JSON                       │
│                           ▼                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                              │
│                    (FastAPI + Python)                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   API Layer                           │  │
│  │  POST /analyze                                        │  │
│  │  GET  /analysis/{id}                                  │  │
│  │  GET  /recommendation/{id}                            │  │
│  │  POST /export/pdf                                     │  │
│  │  POST /export/docx                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Analysis Service                         │  │
│  │         (Pipeline Orchestration)                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│         ┌─────────────────┼─────────────────┐              │
│         ▼                 ▼                 ▼              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Text      │  │  Analysis   │  │   Signal    │       │
│  │ Extraction  │  │   Parser    │  │  Extractor  │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           ▼                                 │
│                  ┌─────────────────┐                       │
│                  │ Scoring Engine  │                       │
│                  └─────────────────┘                       │
│                           │                                 │
│                           ▼                                 │
│                  ┌─────────────────┐                       │
│                  │  LLM Service    │                       │
│                  │  (OpenRouter)   │                       │
│                  └─────────────────┘                       │
│                           │                                 │
│                           ▼                                 │
│                  ┌─────────────────┐                       │
│                  │ Memo Generator  │                       │
│                  └─────────────────┘                       │
│                           │                                 │
│         ┌─────────────────┼─────────────────┐              │
│         ▼                 ▼                 ▼              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │  Database   │  │   Export    │  │   Export    │       │
│  │  Service    │  │  PDF        │  │  DOCX       │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │   SQLite    │                                           │
│  │  Database   │                                           │
│  └─────────────┘                                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              OpenRouter API                           │  │
│  │         (LLM: Claude 3.5 Sonnet)                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Analysis Generation Flow

```
User Input (UI)
    │
    ├─ Counterparty Info (name, country, sector, ratings)
    └─ Analysis Text
    │
    ▼
POST /analyze
    │
    ▼
Text Extraction & Cleaning
    │
    ▼
Section Parsing (Company Profile, Assets, Liquidity, etc.)
    │
    ▼
Signal Extraction (CET1, NPL, LCR, ROAE, etc.)
    │
    ▼
Rule-Based Scoring (1-5 scale for each dimension)
    │
    ▼
LLM Narrative Generation (Strengths, Weaknesses, Recommendation)
    │
    ▼
Memo Formatting (Jinja2 template)
    │
    ▼
Database Persistence
    │
    ▼
Response to UI (Structured Analysis + Scores + Memo)
```

### 2. Export Flow

```
User clicks Export
    │
    ▼
POST /export/pdf or /export/docx
    │
    ▼
Retrieve Memo from Database
    │
    ▼
Generate PDF (reportlab) or DOCX (python-docx)
    │
    ▼
Return File to Browser
    │
    ▼
Browser Downloads File
```

## Technology Stack

### Frontend
- **Framework**: Angular 17 (standalone components)
- **UI Library**: Angular Material
- **HTTP Client**: Angular HttpClient
- **State Management**: RxJS Observables
- **Styling**: CSS + Material Design

### Backend
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: SQLite (dev), PostgreSQL (prod)
- **NLP**: spacy (en_core_web_sm)
- **LLM**: OpenRouter API (Claude 3.5 Sonnet)
- **PDF**: reportlab
- **DOCX**: python-docx
- **Templates**: Jinja2

## Key Design Decisions

1. **Standalone Angular Components**: Using Angular 17's standalone components for simpler architecture
2. **Pipeline Architecture**: Sequential processing stages for clarity and maintainability
3. **Deterministic Scoring**: Rule-based scoring (no LLM) for consistency and auditability
4. **LLM for Narrative Only**: AI used only for text generation, not for scoring or analysis
5. **SQLite for MVP**: Simple file-based database for development, easy to upgrade to PostgreSQL
6. **Two-Panel UI**: Left panel for input, right panel for output - optimized for analyst workflow
7. **Material Design**: Professional, clean UI suitable for enterprise use

## Security Considerations

- API key stored in environment variables (not in code)
- CORS configured for local development
- Input validation using Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM
- File upload validation (PDF/DOCX only)

## Scalability Considerations

- Stateless API design (can scale horizontally)
- Database connection pooling
- Async/await for I/O operations
- Retry logic for external API calls
- Graceful degradation (continues if signal extraction fails)

## Future Enhancements

- User authentication and authorization
- Multi-tenancy support
- Batch processing
- Real-time collaboration
- Version control for memos
- Advanced analytics dashboard
- Custom scoring rules per organization
- Integration with existing credit systems
