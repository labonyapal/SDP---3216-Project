from abc import ABC, abstractmethod

class Classroom(ABC):
    def __init__(self, name: str, description: str, teacher_id: str, code: str):
        self.name = name
        self.description = description
        self.teacher_id = teacher_id
        self.code = code
        self.students = []
        self.notices = []
        self.materials = []

    @abstractmethod
    def get_class_type(self) -> str:
        pass

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "teacher_id": self.teacher_id,
            "code": self.code,
            "class_type": self.get_class_type(),
            "students": self.students,
            "notices": self.notices,
            "materials": self.materials
        }

class LectureClassroom(Classroom):
    def get_class_type(self) -> str:
        return "Lecture"

class LabClassroom(Classroom):
    def get_class_type(self) -> str:
        return "Lab"

class SeminarClassroom(Classroom):
    def get_class_type(self) -> str:
        return "Seminar"

class ClassroomFactory:
    @staticmethod
    def create_classroom(class_type: str, name: str, description: str, teacher_id: str, code: str) -> Classroom:
        t = class_type.lower()
        if t == "lecture":
            return LectureClassroom(name, description, teacher_id, code)
        elif t == "lab":
            return LabClassroom(name, description, teacher_id, code)
        elif t == "seminar":
            return SeminarClassroom(name, description, teacher_id, code)
        else:
            raise ValueError(f"Unknown classroom type: {class_type}")
