from typing import List
from app.models.observer import Observer

class NoticeBoard:
    def __init__(self, classroom_id: str):
        self.classroom_id = classroom_id
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"[NoticeBoard - {self.classroom_id}] Attached observer for student: {getattr(observer, 'username', 'Unknown')}")

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"[NoticeBoard - {self.classroom_id}] Detached observer for student: {getattr(observer, 'username', 'Unknown')}")

    def notify(self, message: str) -> None:
        print(f"[NoticeBoard - {self.classroom_id}] Broadcasting notice: '{message}' to {len(self._observers)} observers.")
        for observer in self._observers:
            observer.update(message)
