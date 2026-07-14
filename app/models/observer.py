from abc import ABC, abstractmethod
import datetime

# Global in-memory list to store notification events for UI demonstration
notification_logs = []

class Observer(ABC):
    @abstractmethod
    def update(self, message: str) -> None:
        """
        Receive notification from the subject.
        """
        pass

class StudentNotificationObserver(Observer):
    def __init__(self, student_id: str, username: str, email: str):
        self.student_id = student_id
        self.username = username
        self.email = email

    def update(self, message: str) -> None:
        # Simulate sending a notification (printing to console)
        log_message = f"[OBSERVER NOTIFICATION] Student: {self.username} ({self.email}) received notice: '{message}'"
        print(log_message)
        
        # Record notification event for the UI to display
        notification_logs.append({
            "student_id": self.student_id,
            "username": self.username,
            "email": self.email,
            "message": message,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
