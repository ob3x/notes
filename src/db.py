from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("postgresql://postgres:password@localhost:5432/notes")
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()

def create_base():
    Base.metadata.create_all(bind=engine)


