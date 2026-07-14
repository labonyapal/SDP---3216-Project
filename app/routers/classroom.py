import os
import uuid
import datetime
import time
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from app.database import get_db
from app.security import get_current_user, RoleChecker
from app.models.classroom_factory import ClassroomFactory
from app.models.classroom_manager import classroom_manager
from app.models.observer import notification_logs

router = APIRouter()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ClassroomCreate(BaseModel):
    name: str
    class_type: str  # Lecture, Lab, Seminar
    description: Optional[str] = ""

class JoinRequest(BaseModel):
    code: str

class NoticePublish(BaseModel):
    content: str

def serialize_doc(doc):
    if not doc:
        return doc
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

def serialize_list(docs):
    return [serialize_doc(doc) for doc in docs]

async def generate_unique_code(db) -> str:
    """Generates a unique 6-character classroom code."""
    while True:
        code = str(uuid.uuid4()).replace("-", "")[:6].upper()
        existing = await db.classrooms.find_one({"code": code})
        if not existing:
            return code

@router.get("/enrolled")
async def get_enrolled_classrooms(db = Depends(get_db), current_user = Depends(get_current_user)):
    """Fetch classrooms created by the teacher or joined by the student."""
    try:
        user_role = current_user.get("role")
        user_id = current_user.get("id")
        
        if user_role == "Teacher":
            classrooms = await db.classrooms.find({"teacher_id": user_id}).to_list(1000)
        else:
            classrooms = await db.classrooms.find({"students": user_id}).to_list(1000)
            
        return serialize_list(classrooms)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("")
async def create_classroom(classroom: ClassroomCreate, db = Depends(get_db), current_user = Depends(RoleChecker(["Teacher"]))):
    """Creates a new classroom using ClassroomFactory and registers it in-memory."""
    try:
        code = await generate_unique_code(db)
        teacher_id = current_user.get("id")
        
        # Instantiate classroom entity using the Factory Pattern
        classroom_entity = ClassroomFactory.create_classroom(
            class_type=classroom.class_type,
            name=classroom.name,
            description=classroom.description,
            teacher_id=teacher_id,
            code=code
        )
        
        classroom_dict = classroom_entity.to_dict()
        result = await db.classrooms.insert_one(classroom_dict)
        classroom_dict["id"] = str(result.inserted_id)
        del classroom_dict["_id"]
        
        # Initialize notice board instance
        classroom_manager.get_notice_board(classroom_dict["id"])
        
        return classroom_dict
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/join")
async def join_classroom(req: JoinRequest, current_user = Depends(RoleChecker(["Student"]))):
    """Joins a student into a classroom via its code and registers the observer."""
    try:
        joined_class = await classroom_manager.join_classroom(req.code, current_user.get("id"))
        return {
            "message": "Successfully joined classroom and attached notification observer",
            "classroom": joined_class
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database/Enrollment error: {str(e)}")

@router.get("/{classroom_id}/details")
async def get_classroom_details(classroom_id: str, db = Depends(get_db), current_user = Depends(get_current_user)):
    """Fetch notices, study materials, and info for a classroom."""
    try:
        classroom = await db.classrooms.find_one({"_id": ObjectId(classroom_id)})
        if not classroom:
            raise HTTPException(status_code=404, detail="Classroom not found")
            
        user_role = current_user.get("role")
        user_id = current_user.get("id")
        
        # Verify student is enrolled or teacher is the owner
        if user_role == "Teacher" and classroom.get("teacher_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        if user_role == "Student" and user_id not in classroom.get("students", []):
            raise HTTPException(status_code=403, detail="You are not enrolled in this classroom")
            
        return serialize_doc(classroom)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/{classroom_id}/notices")
async def publish_notice(classroom_id: str, req: NoticePublish, db = Depends(get_db), current_user = Depends(RoleChecker(["Teacher"]))):
    """Publishes a notice and notifies all enrolled students (Observers)."""
    try:
        classroom = await db.classrooms.find_one({"_id": ObjectId(classroom_id)})
        if not classroom:
            raise HTTPException(status_code=404, detail="Classroom not found")
            
        if classroom.get("teacher_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="You are not authorized to post notices in this classroom")
            
        notice = {
            "id": str(uuid.uuid4()),
            "content": req.content,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "author": current_user.get("username")
        }
        
        await db.classrooms.update_one(
            {"_id": ObjectId(classroom_id)},
            {"$push": {"notices": notice}}
        )
        
        # Notify Observers (enrolled students)
        nb = classroom_manager.get_notice_board(classroom_id)
        nb.notify(f"[{classroom.get('name')}] {req.content}")
        
        return {
            "message": "Notice published and students notified",
            "notice": notice
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database/Notification error: {str(e)}")

@router.post("/{classroom_id}/materials")
async def upload_material(
    classroom_id: str,
    title: str = Form(...),
    file: UploadFile = File(...),
    db = Depends(get_db),
    current_user = Depends(RoleChecker(["Teacher"]))
):
    """Uploads a study material file (PDF, etc.) for the classroom."""
    try:
        classroom = await db.classrooms.find_one({"_id": ObjectId(classroom_id)})
        if not classroom:
            raise HTTPException(status_code=404, detail="Classroom not found")
            
        if classroom.get("teacher_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="You are not authorized to upload study materials to this classroom")
            
        # Create safe unique filename
        safe_filename = f"{int(time.time())}_{file.filename.replace(' ', '_')}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Write file to disk
        with open(file_path, "wb") as f:
            f.write(await file.read())
            
        material = {
            "id": str(uuid.uuid4()),
            "title": title,
            "filename": file.filename,
            "file_url": f"/static/uploads/{safe_filename}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        await db.classrooms.update_one(
            {"_id": ObjectId(classroom_id)},
            {"$push": {"materials": material}}
        )
        
        return {
            "message": "Study material uploaded successfully",
            "material": material
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database/Upload error: {str(e)}")

@router.get("/notifications/logs")
async def get_notifications():
    """Fetch recent simulated notification event logs."""
    return notification_logs
