from typing import Optional, List
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from sqlmodel import SQLModel, Field, select, create_engine, Session, Relationship
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator, EmailStr

import os

# ===== PASSWORD HASHING =====
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ===== JWT CONFIGURATION =====
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ===== DATABASE MODELS =====
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    notes: List["Note"] = Relationship(back_populates="owner")

class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    is_completed: bool = False
    tags: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Foreign key - links note to user
    user_id: int = Field(foreign_key="user.id")
    
    # Relationship
    owner: User = Relationship(back_populates="notes")


# ===== PYDANTIC MODEL (for API input validation) =====
class NoteCreate(BaseModel):
    content: str
    is_completed: bool = False
    tags: Optional[str] = None
    
    @field_validator('content')
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v

# ===== USER SCHEMAS =====
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

# Dynamic database URL (PostgreSQL in Docker, SQLite for local testing)
database_url = os.getenv("DATABASE_URL", "sqlite:///database.db")

# Create engine with connection pooling
# pool_pre_ping=True checks connection health before using
engine = create_engine(
    database_url,
    echo=True,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {}
)


# 2. CREATE TABLES
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# 3. THE DEPENDENCY
def get_session():
    with Session(engine) as session:
        yield session

security = HTTPBearer()

# ===== AUTHENTICATION DEPENDENCY =====
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


# 4. INITIALIZE APP
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== AUTHENTICATION ENDPOINTS =====
@app.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    # Check if username exists
    existing_user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email exists
    existing_email = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create user with hashed password
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user

@app.post("/login", response_model=Token)
def login(user_data: UserLogin, session: Session = Depends(get_session)):
    # Find user by username
    user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()
    
    # Verify credentials
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    # Create JWT token
    access_token = create_access_token({"user_id": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/notes", response_model=Note, status_code=201)
def create_note(
    note_input: NoteCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Create note and link it to the current user
    note = Note(**note_input.model_dump(), user_id=current_user.id)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note

@app.get("/notes")
def get_notes(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Only return notes belonging to the current user
    statement = select(Note).where(Note.user_id == current_user.id)
    notes = session.exec(statement).all()
    return notes

@app.get("/notes/{note_id}", response_model=Note)
def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    note = session.get(Note, note_id)
    
    # Check if note exists
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check if note belongs to current user (IMPORTANT!)
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this note")
    
    return note

@app.put("/notes/{note_id}", response_model=Note)
def update_note(
    note_id: int,
    note_update: NoteCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get the note
    note = session.get(Note, note_id)
    
    # Check if note exists
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check if note belongs to current user (IMPORTANT!)
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this note")
    
    # Update the note fields
    note.content = note_update.content
    note.is_completed = note_update.is_completed
    note.tags = note_update.tags
    
    session.add(note)
    session.commit()
    session.refresh(note)
    
    return note


@app.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get the note
    note = session.get(Note, note_id)
    
    # Check if note exists
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check if note belongs to current user (IMPORTANT!)
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this note")
    
    # Delete the note
    session.delete(note)
    session.commit()
    
    return {"message": "Note deleted successfully", "id": note_id}
