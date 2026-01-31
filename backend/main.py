from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

# Import our database logic and models
from database import create_db_and_tables, get_session
from models import User, StatusType, Friendship

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

@app.patch("/users/{user_id}/toggle")
def toggle_status(user_id: UUID, session: Session = Depends(get_session)):
    # 1. Find the user in the "Fridge" (Database)
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Logic: Flip the switch
    if user.current_status == StatusType.AVAILABLE:
        user.current_status = StatusType.BUSY
    else:
        user.current_status = StatusType.AVAILABLE

    # 3. Save the changes
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"new_status": user.current_status, "updated_at": user.updated_at}

# 1. Send a Friend Request
@app.post("/friends/request")
def send_friend_request(user_id: UUID, friend_phone: str, session: Session = Depends(get_session)):
    # Find the friend by phone number
    friend = session.exec(select(User).where(User.phone_number == friend_phone)).first()
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create the link (start as 'pending')
    new_friendship = Friendship(user_id=user_id, friend_id=friend.id, status="pending")
    session.add(new_friendship)
    session.commit()
    return {"message": "Request sent"}

# 2. Accept a Friend Request
@app.patch("/friends/accept")
def accept_friend_request(user_id: UUID, requester_id: UUID, session: Session = Depends(get_session)):
    statement = select(Friendship).where(
        Friendship.user_id == requester_id, 
        Friendship.friend_id == user_id
    )
    friendship = session.exec(statement).first()
    if not friendship:
        raise HTTPException(status_code=404, detail="Request not found")
    
    friendship.status = "accepted"
    session.add(friendship)
    session.commit()
    return {"message": "Friendship accepted"}

@app.get("/friends/list/{user_id}", response_model=List[User])
def get_friends_list(user_id: UUID, session: Session = Depends(get_session)):
    # 1. This query finds EVERYONE you have an 'accepted' friendship with
    # 2. It joins the User table to get their name and status
    # 3. It sorts them: 'available' comes before 'busy' alphabetically (a before b!)
    
    statement = select(User).join(
        Friendship, 
        ((Friendship.user_id == User.id) & (Friendship.friend_id == user_id)) | 
        ((Friendship.friend_id == User.id) & (Friendship.user_id == user_id))
    ).where(Friendship.status == "accepted").order_by(User.current_status, User.display_name)
    
    friends = session.exec(statement).all()
    return friends