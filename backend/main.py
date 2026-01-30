from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

# Import our database logic and models
from database import create_db_and_tables, get_session
from models import User, StatusType

app = FastAPI()

# This runs once when the server starts up
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"status": "The Kitchen is Open", "db": "Tables Initialized"}

# Our first "Real" SWE Endpoint: Create a User
@app.post("/users/", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    # Check if phone number already exists
    statement = select(User).where(User.phone_number == user.phone_number)
    results = session.exec(statement)
    if results.first():
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Save the new user to the fridge
    session.add(user)
    session.commit()
    session.refresh(user)
    return user