import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, ValidationError

class Settings(BaseSettings):
    groq_api_key: str = Field(..., description="Groq API key required for LLM")
    groq_model: str = "llama-3.3-70b-versatile"
    groq_fallback_model: str = "llama-3.1-8b-instant"
    groq_temperature: float = 0.3
    groq_max_tokens: int = 2048
    
    budget_low_max: int = 500
    budget_medium_max: int = 1500
    
    max_candidates: int = 20
    top_n: int = 5
    
    data_cache_path: str = "data/processed/restaurants.parquet"
    hf_dataset_id: str = "ManikaSaini/zomato-restaurant-recommendation"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        if any("groq_api_key" in err.get("loc", []) for err in e.errors()):
            print("CRITICAL ERROR: GROQ_API_KEY is missing from environment or .env file.")
            print("Please copy .env.example to .env and provide your API key.")
            sys.exit(1)
        raise

# A global settings instance (this will fail fast if GROQ_API_KEY is missing on import)
settings = get_settings()

