import asyncio
import random
from datetime import datetime, timezone
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import InferenceResult
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MLModelSingleton:
    """Mock ML Model representing a loaded AI model in memory."""
    
    _instance = None
    _is_loaded = False
    _model_version = ""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLModelSingleton, cls).__new__(cls)
        return cls._instance

    async def load_model(self):
        """Simulate loading a model into RAM on startup (takes 2 seconds)."""
        if not self._is_loaded:
            logger.info("Initializing ML Model... (simulating 2s load time)")
            await asyncio.sleep(2)
            self._model_version = get_settings().MODEL_NAME
            self._is_loaded = True
            logger.info(f"Model {self._model_version} loaded successfully into memory.")

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded
        
    @property
    def version(self) -> str:
        return self._model_version

    def predict(self, text: str) -> dict:
        """
        Simulate text classification inference.
        Returns: { 'prediction': 'Positive'|'Negative'|'Neutral', 'confidence': float }
        """
        if not self._is_loaded:
            raise RuntimeError("Model is not loaded!")
            
        text_lower = text.lower()
        
        # Simple keyword-based mock logic
        if any(word in text_lower for word in ["good", "great", "excellent", "love", "amazing", "happy"]):
            pred = "Positive"
            conf = round(random.uniform(0.75, 0.99), 4)
        elif any(word in text_lower for word in ["bad", "terrible", "awful", "hate", "worst", "sad"]):
            pred = "Negative"
            conf = round(random.uniform(0.75, 0.99), 4)
        else:
            pred = "Neutral"
            conf = round(random.uniform(0.40, 0.70), 4)
            
        return {"prediction": pred, "confidence": conf}


# Global model instance
ml_model = MLModelSingleton()


async def get_inference_by_id(infer_id: int, db: AsyncSession) -> InferenceResult | None:
    """Retrieve an inference result by its ID."""
    try:
        stmt = select(InferenceResult).where(InferenceResult.id == infer_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error reading from DB: {e}")
        return None


async def save_inference_result(
    text: str,
    prediction: str,
    confidence: float,
    model_version: str,
    db: AsyncSession,
) -> InferenceResult:
    """Save inference result to database history."""
    entry = InferenceResult(
        text=text,
        prediction=prediction,
        confidence=confidence,
        model_version=model_version,
    )
    
    try:
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
    except Exception as e:
        logger.warning(f"Failed to save inference result to DB: {e}")
        # Gracefully handle DB run without crashing the response
        entry.id = -1
        entry.created_at = datetime.now(timezone.utc)
        
    return entry


async def check_database_health(db: AsyncSession) -> bool:
    """Check if database connection is healthy."""
    try:
        await db.execute(select(1))
        return True
    except Exception:
        return False
