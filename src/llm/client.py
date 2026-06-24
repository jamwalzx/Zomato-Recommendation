import os
from groq import Groq, APIError, APIConnectionError, RateLimitError
import time
from src.config import settings
import logging

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        # Pass the API key explicitly from pydantic settings
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        
    def generate_recommendations(self, system_prompt: str, user_prompt: str, retries: int = 1) -> str:
        """
        Calls Groq Chat Completions API enforcing JSON output.
        Retries on timeout/rate-limit.
        """
        for attempt in range(retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3,
                    max_tokens=2048
                )
                return response.choices[0].message.content
            except (APIConnectionError, RateLimitError, APIError) as e:
                logger.warning(f"Groq API Error on attempt {attempt + 1}: {str(e)}")
                if attempt == retries:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        return "{}"
