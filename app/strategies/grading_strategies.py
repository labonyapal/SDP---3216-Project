from typing import Any, Dict
from app.strategies.grading_strategy import GradingStrategy


class AutoQuizStrategy(GradingStrategy):
    """Grades quiz-style submissions by comparing answers against a key."""

    def grade(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        answers = submission_data.get("answers", {})
        answer_key = submission_data.get("answer_key", {})
        if not answers or not answer_key:
            return {"score": 0, "feedback": "No quiz answers were provided.", "status": "Needs Review"}

        correct = 0
        total = len(answer_key)
        for question, expected in answer_key.items():
            if answers.get(question) == expected:
                correct += 1

        score = round((correct / total) * 100, 2) if total else 0
        feedback = f"Matched {correct} out of {total} answers correctly."
        return {"score": score, "feedback": feedback, "status": "Graded"}


class CodeSubmissionStrategy(GradingStrategy):
    """Simulates grading code submissions by checking passed tests."""

    def grade(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        passed_tests = submission_data.get("passed_tests", 0)
        total_tests = submission_data.get("total_tests", 0)
        if total_tests <= 0:
            return {"score": 0, "feedback": "No test cases were provided.", "status": "Needs Review"}

        score = round((passed_tests / total_tests) * 100, 2)
        feedback = f"Passed {passed_tests} out of {total_tests} automated tests."
        return {"score": score, "feedback": feedback, "status": "Graded"}


class ManualReviewStrategy(GradingStrategy):
    """Flags submissions for teacher review with a placeholder score."""

    def grade(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "score": 0,
            "feedback": "Pending teacher review.",
            "status": "Pending Teacher Review",
            "placeholder_score": 0,
        }
