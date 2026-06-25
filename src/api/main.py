from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import logging

from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.services.orchestrator import get_recommendations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CraveAI Restaurant Recommendation API",
    description="AI-powered restaurant recommendations using deterministic filtering and Groq LLM."
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/recommendations", response_model=RecommendationResponse)
async def create_recommendations(prefs: UserPreferences):
    """
    Accepts user preferences and returns a ranked list of AI-explained recommendations.
    """
    try:
        response = get_recommendations(prefs)
        return response
    except ValueError as e:
        logger.error(f"Validation or domain error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred while processing your request.")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

from fastapi.staticfiles import StaticFiles
import os

static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
