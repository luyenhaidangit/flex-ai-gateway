from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schemas import ErrorDetail, InferenceRequest, InferenceResponse
from app.services.core import get_inference_by_id, ml_model, save_inference_result

router = APIRouter(prefix="/api", tags=["Inference"])


@router.post(
    "/infer",
    response_model=InferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit text for classification inference",
    description=(
        "Send raw text to the currently loaded ML model. "
        "The model predicts the sentiment (Positive/Negative/Neutral) "
        "and returns a confidence score. Results are logged to the database."
    ),
    responses={
        422: {"model": ErrorDetail, "description": "Validation error"},
        503: {"model": ErrorDetail, "description": "Model not loaded yet"},
    },
)
async def infer(request: InferenceRequest, db: AsyncSession = Depends(get_db)):
    if not ml_model.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML Model is currently initializing and not ready to accept requests.",
        )

    result = ml_model.predict(request.text)

    entry = await save_inference_result(
        text=request.text,
        prediction=result["prediction"],
        confidence=result["confidence"],
        model_version=ml_model.version,
        db=db,
    )

    return InferenceResponse(
        id=entry.id,
        text=entry.text,
        prediction=entry.prediction,
        confidence=entry.confidence,
        model_version=entry.model_version,
        created_at=entry.created_at,
    )


@router.get(
    "/infer/{infer_id}",
    response_model=InferenceResponse,
    summary="Get past inference result by ID",
    description="Retrieve a previously executed inference classification from the history database.",
    responses={
        404: {"model": ErrorDetail, "description": "Result not found"},
    },
)
async def get_inference(infer_id: int, db: AsyncSession = Depends(get_db)):
    entry = await get_inference_by_id(infer_id, db)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inference record with id {infer_id} not found",
        )

    return InferenceResponse(
        id=entry.id,
        text=entry.text,
        prediction=entry.prediction,
        confidence=entry.confidence,
        model_version=entry.model_version,
        created_at=entry.created_at,
    )
