"""
FastAPI application for User Service
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import RequestValidationError
from bson import ObjectId
from datetime import datetime
import uvicorn

from shared.models.user import UserCreate, UserResponse
from shared.models.base import Token

from shared.utils.responses import (
    APIResponse,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from database import db
from auth import (
    get_password_hash,
    create_access_token,
    get_current_user,
    verify_password
)


@asynccontextmanager
async def lifespan(app_: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    print("Starting up...")
    await db.connect_db()

    yield  # Server is running and handling requests

    # Shutdown
    print("Shutting down...")
    await db.close_db()

app = FastAPI(
    title="User Service",
    version="1.0.0",
    description="User management microservice",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.post("/users/createUser", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """
    Create a new user
    """
    database = await db.get_database()
    if await database.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_dict = user.model_dump()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    user_dict["created_at"] = datetime.now()
    user_dict["updated_at"] = user_dict["created_at"]

    result = await database.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)

    return UserResponse(**user_dict)


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and generate access token.
    """
    database = await db.get_database()
    user = await database.users.find_one({"email": form_data.username})

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    access_token = create_access_token(
        data={"sub": form_data.username, "user_id": str(user["_id"])}
    )
    return Token(access_token=access_token)


@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get information about the currently authenticated user.
    """
    current_user["id"] = str(current_user["_id"])
    return UserResponse(**current_user)


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: str,
        current_user: dict = Depends(get_current_user)
):
    """
    Get user information by ID (requires authentication).
    """
    database = await db.get_database()
    user = await database.users.find_one({"_id": ObjectId(user_id)})

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user["id"] = str(user.pop("_id"))
    return UserResponse(**user)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
