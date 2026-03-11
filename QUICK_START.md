# Quick Start Guide

Get the Counterparty Recommendation Engine running in 5 minutes!

## Prerequisites

- Python 3.11 or 3.12
- Node.js 18+
- Google Gemini API key (free - get at https://makersuite.google.com/app/apikey)

## Step 1: Backend Setup (2 minutes)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Download NLP model
python -m spacy download en_core_web_sm

# Create environment file
# Get free Gemini API key at: https://makersuite.google.com/app/apikey
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
echo "DATABASE_URL=sqlite:///./counterparty_engine.db" >> .env

# Start backend
uvicorn app.main:app --reload
```

✅ Backend running at http://localhost:8000

**Note:** System will use Mock LLM if no API key is set. See [GEMINI_SETUP.md](GEMINI_SETUP.md) for free Gemini API setup.

## Step 2: Frontend Setup (3 minutes)

```bash
# Install Angular CLI (if not installed)
npm install -g @angular/cli

# Navigate to frontend
cd counterparty-ui

# Install dependencies (you'll see some warnings - this is normal)
npm install

# Start frontend
npm start
```

**Note**: You'll see npm security warnings during install. These are in build tools only and safe for development. See `counterparty-ui/SECURITY_NOTE.md` for details.

✅ Frontend running at http://localhost:4200

## Step 3: Test the System

1. Open http://localhost:4200
2. Enter:
   - **Name**: Example Bank
   - **Country**: USA
   - **Sector**: Banking

3. Paste this sample analysis:
```
Company Profile:
Example Bank is a leading financial institution.

Assets:
NPL ratio of 2.3%.

Liquidity:
LCR of 145%.

Strategy:
Digital transformation focus.

Means:
CET1 ratio of 13.5%.

Performance:
ROAE of 11.2% and cost-to-income ratio of 55%.
```

4. Click **Generate Recommendation**

5. View the results:
   - ✅ Scorecard with risk scores
   - ✅ Structured analysis sections
   - ✅ AI-generated recommendation memo

6. Try exporting:
   - Click **Export as PDF** or **Export as DOCX**

## Troubleshooting

**Backend won't start?**
- Check Python version: `python --version` (need 3.11+)
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`
- Check .env file has OPENROUTER_API_KEY

**Frontend won't start?**
- Check Node version: `node --version` (need 18+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Angular CLI: `ng version`

**Can't generate recommendation?**
- Check backend is running at http://localhost:8000
- Check browser console for errors (F12)
- System uses Mock LLM by default (no API key needed)
- For AI-powered narratives, see [LLM_OPTIONS.md](LLM_OPTIONS.md)

**Error: 402 Payment Required?**
- Your OpenRouter account needs credits
- OR switch to Mock LLM: set `OPENROUTER_API_KEY=your_api_key_here` in `.env`
- See [LLM_OPTIONS.md](LLM_OPTIONS.md) for details

## What's Next?

- Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup instructions
- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- Check [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) before deploying
- Customize scoring rules in `app/services/scoring_engine.py`
- Adjust LLM prompts in `app/services/llm_service.py`
- Modify UI styling in `counterparty-ui/src/app/pages/dashboard/`

## Support

- Backend API docs: http://localhost:8000/docs
- Check logs in terminal for errors
- Review error messages in browser console (F12)

Enjoy using the Counterparty Recommendation Engine! 🚀
