from typing import Optional, List
from contextlib import asynccontextmanager

from sqlmodel import SQLModel, Field, select, create_engine, Session
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, field_validator

import os


# ===== DATABASE MODEL (for SQLModel/Database) =====
class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    is_completed: bool = False
    tags: Optional[str] = Field(default=None)


# ===== INPUT MODEL (for API requests - STRICT validation) =====
class NoteCreate(BaseModel):
    content: str
    is_completed: bool = False
    tags: Optional[str] = None

    @field_validator('content')
    @classmethod
    def content_must_be_string(cls, v):
        # Reject if not a string (no coercion from int)
        if not isinstance(v, str):
            raise ValueError('content must be a string')
        if len(v.strip()) == 0:
            raise ValueError('content cannot be empty')
        return v


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


# 4. INITIALIZE APP
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


# ===== UPDATED ENDPOINT (uses NoteCreate for input) =====
@app.post("/notes", response_model=Note, status_code=201)
def create_note(note_input: NoteCreate, session: Session = Depends(get_session)):
    # Convert NoteCreate to Note (database model)
    note = Note(**note_input.model_dump())

    session.add(note)
    session.commit()
    session.refresh(note)

    return note

@app.get("/notes", response_model=List[Note])  # ← KEEP THIS FIRST
def get_notes(session: Session = Depends(get_session)):
    statement = select(Note)
    results = session.exec(statement).all()
    return results

@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int, session: Session = Depends(get_session)):
    # session.get(Model, id) is the standard way to fetch by Primary Key
    note = session.get(Note, note_id)

    if not note:
        # Stop execution immediately and send 404
        raise HTTPException(status_code=404, detail="Note not found")

    return note