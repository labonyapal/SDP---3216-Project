from abc import ABC, abstractmethod

class User(ABC):
    @abstractmethod
    def get_role(self): pass

class Teacher(User):
    def get_role(self): return "Teacher"

class Staff(User):
    def get_role(self): return "Staff"

class Student(User):
    def get_role(self): return "Student"

class UserFactory:
    _registry = {"teacher": Teacher, "staff": Staff, "student": Student}

    @staticmethod
    def create_user(role: str):
        user_class = UserFactory._registry.get(role.lower())
        if not user_class:
            raise ValueError("Invalid Role")
        return user_class()