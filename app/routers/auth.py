from fastapi import APIRouter, HTTPException, Depends
from app.models.user_factory import UserFactory
from app.models.user_schemas import UserRegistration  # Assuming you create this
from app.database import get_db

router = APIRouter()

@router.post("/register/{role}")
async def register(role: str, user_data: UserRegistration, db = Depends(get_db)):
    """
    Registers a new user and saves it to MongoDB.
    """
    try:
        # 1. Use Factory Pattern to get the user type
        user = UserFactory.create_user(role)
        
        # 2. Convert Pydantic schema to dictionary
        user_dict = user_data.model_dump()
        
        # 3. Add the role (determined by Factory) to the data
        user_dict["role"] = user.get_role()
        
        # 4. Save to MongoDB (using 'users' collection)
        # Note: 'db' here comes from the get_db dependency
        result = await db.users.insert_one(user_dict)
        
        return {
            "message": "User registered successfully",
            "id": str(result.inserted_id),
            "role": user.get_role()
        }
        
    except ValueError as e:
        # This handles the case where an invalid role is passed
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # This handles database errors
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")