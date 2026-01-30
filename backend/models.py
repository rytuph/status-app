from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

# This is our "Enum" - it limits the options for status
class StatusType(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"

class User(SQLModel, table=True):
    # We use UUIDs (The Lyft standard!)
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    phone_number: str = Field(index=True, unique=True)
    display_name: str
    
    # The current state of the user
    current_status: StatusType = Field(default=StatusType.BUSY)
    
    # "Last seen" helps for our future ML model
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, onupdate=datetime.utcnow)
    )

class Friendship(SQLModel, table=True):
    # This table links two users together
    id: int | None = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    friend_id: UUID = Field(foreign_key="user.id")
    status: str = Field(default="accepted") # can be 'pending', 'accepted'