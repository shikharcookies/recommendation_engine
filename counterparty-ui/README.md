# Counterparty Recommendation Engine - Frontend

Angular-based UI for the Counterparty Recommendation Engine.

## Prerequisites

- Node.js 18+ and npm
- Angular CLI: `npm install -g @angular/cli`

## Setup

1. Install dependencies:
```bash
cd counterparty-ui
npm install
```

2. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:4200`

## Backend Connection

The frontend connects to the backend API at `http://localhost:8000`.

Make sure the backend is running before using the UI:
```bash
# In the root directory
uvicorn app.main:app --reload
```

## Features

- Enter counterparty information (name, country, sector, model ratings)
- Paste credit analysis text
- Generate recommendation with one click
- View structured analysis sections
- View risk scores (asset quality, liquidity, capitalisation, profitability)
- View generated recommendation memo
- Export as PDF or DOCX

## Project Structure

```
src/
├── app/
│   ├── models/           # TypeScript interfaces
│   ├── services/         # API services
│   ├── pages/
│   │   └── dashboard/    # Main dashboard component
│   ├── app.component.ts
│   └── app.config.ts
├── index.html
├── main.ts
└── styles.css
```

## Build for Production

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.
