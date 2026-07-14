from fastapi import APIRouter, HTTPException, Depends
from app.models.user_factory import UserFactory
from app.models.user_schemas import UserRegistration, UserLogin
from app.database import get_db
from app.security import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register/{role}")
async def register(role: str, user_data: UserRegistration, db = Depends(get_db)):
    """Registers a new user (Student or Teacher) and saves to MongoDB."""
    try:
        # Validate role using Factory pattern
        user_entity = UserFactory.create_user(role)
        target_role = user_entity.get_role()
        
        # Check if username or email already exists
        existing_user = await db.users.find_one({
            "$or": [
                {"username": user_data.username},
                {"email": user_data.email}
            ]
        })
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or email already registered")
            
        # Hash password and model data to dictionary
        user_dict = {
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": hash_password(user_data.password),
            "role": target_role
        }
        
        result = await db.users.insert_one(user_dict)
        return {
            "message": f"Successfully registered as {target_role}",
            "id": str(result.inserted_id),
            "username": user_data.username,
            "role": target_role
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/login")
async def login(user_data: UserLogin, db = Depends(get_db)):
    """Authenticates user and returns a JWT access token."""
    try:
        # Find user by username or email
        user = await db.users.find_one({
            "$or": [
                {"username": user_data.username_or_email},
                {"email": user_data.username_or_email}
            ]
        })
        if not user or not verify_password(user_data.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect username, email, or password")
            
        # Create access token
        access_token = create_access_token(data={
            "sub": str(user["_id"]),
            "username": user["username"],
            "role": user["role"]
        })
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "role": user["role"]
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database/Login error: {str(e)}")