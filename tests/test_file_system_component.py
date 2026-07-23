from app.models.file_system_component import Folder, StudyFile


def test_folder_recursively_calculates_size_and_serializes_tree():
    root = Folder("Course Materials")
    root.add(StudyFile("intro.pdf", 120, "/static/uploads/intro.pdf"))

    week1 = Folder("Week 1")
    week1.add(StudyFile("slides.pdf", 300, "/static/uploads/slides.pdf"))
    root.add(week1)

    assert root.get_size() == 420
    assert root.get_details()["type"] == "folder"
    assert week1.get_details()["children"][0]["name"] == "slides.pdf"

    restored = Folder.from_dict(root.to_dict())
    assert restored.get_size() == 420
    assert restored.get_child("Week 1").get_child("slides.pdf").get_size() == 300
