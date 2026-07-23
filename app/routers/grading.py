from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional
from app.security import get_current_user, RoleChecker
from app.services.grading_context import GradingContext
from app.strategies.grading_strategies import AutoQuizStrategy, CodeSubmissionStrategy, ManualReviewStrategy

router = APIRouter()


class GradingRequest(BaseModel):
    submission_type: str
    submission_data: Dict[str, Any]


class GradingResult(BaseModel):
    strategy: str
    score: float
    feedback: str
    status: str
    placeholder_score: Optional[float] = None


def build_strategy(method: str):
    method = method.lower()
    if method == "quiz":
        return AutoQuizStrategy()
    if method == "code":
        return CodeSubmissionStrategy()
    if method == "manual":
        return ManualReviewStrategy()
    raise ValueError("Unsupported grading method")


@router.post("/grade")
async def grade_submission(
    req: GradingRequest,
    current_user=Depends(RoleChecker(["Teacher"])),
):
    """Grade a submission using the selected strategy pattern implementation."""
    try:
        strategy = build_strategy(req.submission_type)
        context = GradingContext(strategy)
        result = context.execute_grading(req.submission_data)
        return GradingResult(
            strategy=req.submission_type,
            score=result.get("score", 0),
            feedback=result.get("feedback", ""),
            status=result.get("status", "Graded"),
            placeholder_score=result.get("placeholder_score"),
        ).dict()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Grading error: {str(exc)}")
