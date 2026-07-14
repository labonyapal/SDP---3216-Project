from typing import Dict, List
from app.models.notice_board import NoticeBoard
from app.models.observer import StudentNotificationObserver
from app.database import db
from bson import ObjectId

class NoticeBoardManager:
    def __init__(self):
        # Maps classroom_id (str) to NoticeBoard instance
        self._notice_boards: Dict[str, NoticeBoard] = {}

    def get_notice_board(self, classroom_id: str) -> NoticeBoard:
        if classroom_id not in self._notice_boards:
            self._notice_boards[classroom_id] = NoticeBoard(classroom_id)
        return self._notice_boards[classroom_id]

    async def initialize_from_db(self) -> None:
        """
        Load all classrooms and enrollments from MongoDB on startup
        and rebuild the observer relationships in-memory.
        """
        try:
            database = db.get_database()
            # Fetch all classrooms
            cursor = database.classrooms.find({})
            async for classroom in cursor:
                classroom_id = str(classroom["_id"])
                nb = self.get_notice_board(classroom_id)
                
                # Fetch students enrolled in this classroom
                student_ids = classroom.get("students", [])
                for s_id in student_ids:
                    try:
                        # Find student details
                        student_doc = await database.users.find_one({"_id": ObjectId(s_id)})
                        if student_doc:
                            # Instantiate Observer
                            observer = StudentNotificationObserver(
                                student_id=str(student_doc["_id"]),
                                username=student_doc["username"],
                                email=student_doc["email"]
                            )
                            # Attach to classroom's notice board
                            nb.attach(observer)
                    except Exception as ex:
                        print(f"[NoticeBoardManager] Error attaching student {s_id}: {ex}")
            print("[NoticeBoardManager] Successfully initialized notice boards and attached student observers from database.")
        except Exception as e:
            print(f"[NoticeBoardManager] Error initializing from database: {e}")

    async def join_classroom(self, code: str, student_id: str) -> dict:
        """
        Join a student into a classroom using its unique code.
        """
        database = db.get_database()
        
        # 1. Look up student and verify role
        student_doc = await database.users.find_one({"_id": ObjectId(student_id)})
        if not student_doc:
            raise ValueError("Student not found")
        if student_doc.get("role") != "Student":
            raise ValueError("Only students can join classrooms")

        # 2. Look up classroom by code
        classroom = await database.classrooms.find_one({"code": code.upper().strip()})
        if not classroom:
            raise ValueError("Invalid classroom code")
        
        classroom_id = str(classroom["_id"])
        
        # 3. Add student to classroom in MongoDB
        await database.classrooms.update_one(
            {"_id": classroom["_id"]},
            {"$addToSet": {"students": student_id}}
        )

        # 4. Attach StudentNotificationObserver in-memory
        nb = self.get_notice_board(classroom_id)
        
        # Verify if already attached in memory
        already_attached = False
        for obs in nb._observers:
            if isinstance(obs, StudentNotificationObserver) and obs.student_id == student_id:
                already_attached = True
                break
        
        if not already_attached:
            observer = StudentNotificationObserver(
                student_id=student_id,
                username=student_doc["username"],
                email=student_doc["email"]
            )
            nb.attach(observer)
            
        return {
            "id": classroom_id,
            "name": classroom["name"],
            "code": classroom["code"],
            "class_type": classroom.get("class_type", "Standard")
        }

# Global single instance of NoticeBoardManager
classroom_manager = NoticeBoardManager()
