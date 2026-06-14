from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from app.database import db
from motor.motor_asyncio import AsyncIOMotorClient
from app.routers import auth

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to Mongo
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db.client = AsyncIOMotorClient(MONGO_URI)
    yield
    # Shutdown: Close connection
    db.client.close()

app = FastAPI(lifespan=lifespan)

# Include router first so that dynamic auth paths take priority over static catchalls
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")