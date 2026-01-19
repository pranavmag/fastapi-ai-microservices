from typing import Optional, List
from sqlmodel import SQLModel, Field, select


# We inherit from SQLModel.
# table=True means "Create a table in SQLite called 'note' for this."
class Note(SQLModel, table=True):
    # Field(primary_key=True) tells the DB this is the unique ID.
    # Optional[int] means it can be None (because it doesn't exist before we save it).
    id: Optional[int] = Field(default=None, primary_key=True)

    # Strict typing: content MUST be a string.
    content: str

    # We set a default so strict mode doesn't complain if it's missing.
    is_completed: bool = False

    tags: Optional[str] = Field(default=None)



from sqlmodel import create_engine, SQLModel, Session
from fastapi import FastAPI, Depends

# 1. SET UP THE ENGINE
# simple sqlite file named "database.db"
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# echo=True prints SQL commands to console (great for debugging)
engine = create_engine(sqlite_url, echo=True)

# 2. CREATE TABLES
# This function looks at all classes with table=True and builds the DB
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 3. THE DEPENDENCY (The Magic Part)
# We yield the session. This keeps the connection open while the request runs,
# and closes it immediately after the "return" happens.
def get_session():
    with Session(engine) as session:
        yield session

# 4. INITIALIZE APP
# lifespan events are the new "on_startup" in FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables() # Run this when server starts
    yield

app = FastAPI(lifespan=lifespan)


# 'note: Note' tells FastAPI to read the JSON body using the Note schema.
# 'session: Session = Depends(get_session)' injects the DB connection.
# added status_code=201 inside the decorator to make sure a note was created rather than status code 200
@app.post("/notes", response_model=Note, status_code=201)
def create_note(note: Note, session: Session = Depends(get_session)):
    # 1. Add to the "staging area"
    session.add(note)

    # 2. Commit (actually write to SQLite)
    session.commit()

    # 3. Refresh (The Note object currently doesn't know its new ID.
    # This fetches the ID and any default values from the DB back into Python)
    session.refresh(note)

    # 4. Return it. FastAPI converts python object -> JSON
    return note


# response_model=List[Note] guarantees the output is ALWAYS a list of Notes.
# It enforces strict structure on the data leaving your API.
@app.get("/notes", response_model=List[Note])
def get_notes(session: Session = Depends(get_session)):
    # 1. Build the statement (The "Search Query")
    statement = select(Note)

    # 2. Execute and Fetch
    # session.exec() runs the SQL.
    # .all() fetches all rows and puts them into a list.
    results = session.exec(statement).all()

    # 3. Return
    return results