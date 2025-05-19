from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager

DATABASE_URL = "sqlite:///./studyplanner.db"

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    from models import User, Progress, Course, Exam  
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@contextmanager
def get_db_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
