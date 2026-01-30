from sqlmodel import SQLModel, create_engine, Session
from models import User # We will import our models here

# The address of our Docker Fridge
sqlite_url = "postgresql://user:password@localhost:5432/status_app_db"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    # This command looks at our models and builds the tables in Postgres
    SQLModel.metadata.create_all(engine)

def get_session():
    # This creates a "Session" (a temporary connection to the fridge)
    with Session(engine) as session:
        yield session