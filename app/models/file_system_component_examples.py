from app.models.file_system_component import Folder, StudyFile


def build_sample_tree() -> Folder:
    root = Folder("Course Materials")
    root.add(StudyFile("syllabus.pdf", 140, "/static/uploads/syllabus.pdf"))

    week1 = Folder("Week 1")
    week1.add(StudyFile("slides.pdf", 300, "/static/uploads/slides.pdf"))
    root.add(week1)

    return root
