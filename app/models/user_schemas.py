from pydantic import BaseModel, Field

class UserRegistration(BaseModel):
    username: str
    email: str
    # You can add more fields here later