from typing import Any, Dict
from app.strategies.grading_strategy import GradingStrategy


class GradingContext:
    """Context class that executes the active grading strategy dynamically."""

    def __init__(self, strategy: GradingStrategy):
        self._strategy = strategy

    def execute_grading(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._strategy.grade(submission_data)
