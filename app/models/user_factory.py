from abc import ABC, abstractmethod

class User(ABC):
    @abstractmethod
    def get_role(self) -> str:
        pass

class Teacher(User):
    def get_role(self) -> str:
        return "Teacher"

class Student(User):
    def get_role(self) -> str:
        return "Student"

class UserFactory:
    _registry = {"teacher": Teacher, "student": Student}

    @staticmethod
    def create_user(role: str) -> User:
        user_class = UserFactory._registry.get(role.lower())
        if not user_class:
            raise ValueError("Invalid Role. Must be 'Student' or 'Teacher'")
        return user_class()