from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes

app = FastAPI(
    title="Counterparty Recommendation Engine",
    description="Transform unstructured credit analysis into structured insights",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(routes.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    from app.services.database_service import DatabaseService
    db = DatabaseService()
    # Database tables are created in DatabaseService.__init__


@app.get("/")
async def root():
    return {"message": "Counterparty Recommendation Engine API"}
