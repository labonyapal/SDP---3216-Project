from abc import ABC, abstractmethod
from typing import Any, Dict


class GradingStrategy(ABC):
    """Abstract base class for grading strategies."""

    @abstractmethod
    def grade(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return a grading result with score and feedback."""
        raise NotImplementedError
