# Counterparty Recommendation Engine - Complete Setup Guide

This guide will help you set up both the backend and frontend of the Counterparty Recommendation Engine.

## System Requirements

- Python 3.11 or 3.12
- Node.js 18+ and npm
- OpenRouter API key (get one at https://openrouter.ai/)

## Part 1: Backend Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download Spacy Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
OPENROUTER_API_KEY=your_actual_api_key_here
DATABASE_URL=sqlite:///./counterparty_engine.db
```

Replace `your_actual_api_key_here` with your actual OpenRouter API key.

### 4. Start the Backend Server

```bash
uvicorn app.main:app --reload
```

The backend API will be available at `http://localhost:8000`

You can view the API documentation at `http://localhost:8000/docs`

## Part 2: Frontend Setup

### 1. Install Angular CLI (if not already installed)

```bash
npm install -g @angular/cli
```

### 2. Navigate to Frontend Directory

```bash
cd counterparty-ui
```

### 3. Install Dependencies

```bash
npm install
```

### 4. Start the Frontend Development Server

```bash
npm start
```

The frontend will be available at `http://localhost:4200`

## Using the Application

1. **Open your browser** and go to `http://localhost:4200`

2. **Enter counterparty information:**
   - Counterparty Name (required)
   - Country (optional)
   - Sector (optional)
   - Model Ratings: Intrinsic HRC, Intrinsic PD, Counterparty HRC, Counterparty PD (all optional)

3. **Paste credit analysis text** in the large text area. Include sections like:
   - Company Profile
   - Assets
   - Liquidity
   - Strategy
   - Means
   - Performance

4. **Click "Generate Recommendation"**

5. **View the results:**
   - Credit Scorecard with risk scores
   - Structured Analysis (expandable sections)
   - Recommendation Memo

6. **Export the memo:**
   - Click "Export as PDF" or "Export as DOCX"

## Example Analysis Text

```
Company Profile:
Example Bank is a leading financial institution with strong market presence in the UK.

Assets:
The bank maintains a diversified asset portfolio with NPL ratio of 2.3%.

Liquidity:
Strong liquidity position with LCR of 145%.

Strategy:
Focus on digital transformation and customer experience improvement.

Means:
Well-capitalized with CET1 ratio of 13.5%.

Performance:
ROAE of 11.2% and cost-to-income ratio of 55%.
```

## Troubleshooting

### Backend Issues

**Error: "openrouter_api_key" field required**
- Make sure you've created the `.env` file with your OpenRouter API key

**Error: Module not found**
- Run `pip install -r requirements.txt` again

**Error: spacy model not found**
- Run `python -m spacy download en_core_web_sm`

### Frontend Issues

**Error: Cannot connect to backend**
- Make sure the backend is running at `http://localhost:8000`
- Check that CORS is enabled in the backend (it should be by default)

**Error: npm install fails**
- Make sure you have Node.js 18+ installed
- Try deleting `node_modules` and `package-lock.json`, then run `npm install` again

## Architecture

### Backend (Python/FastAPI)
- **API Layer**: FastAPI endpoints
- **Services**: Text extraction, parsing, signal detection, scoring, LLM integration
- **Database**: SQLite with SQLAlchemy ORM
- **Export**: PDF and DOCX generation

### Frontend (Angular/TypeScript)
- **Components**: Dashboard with two-panel layout
- **Services**: HTTP client for API communication
- **UI**: Angular Material components
- **State**: Component-based state management with RxJS

## API Endpoints

- `POST /analyze` - Generate analysis and recommendation
- `GET /analysis/{id}` - Retrieve saved analysis
- `GET /recommendation/{id}` - Retrieve saved recommendation
- `POST /export/pdf` - Export as PDF
- `POST /export/docx` - Export as DOCX

## Next Steps

- Add more test data
- Customize the scoring rules in `app/services/scoring_engine.py`
- Adjust the LLM prompt in `app/services/llm_service.py`
- Customize the UI styling in `counterparty-ui/src/app/pages/dashboard/dashboard.component.css`
