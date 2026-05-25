# app/models/usage.py
from sqlmodel import SQLModel, Field
from datetime import datetime

class UserUsage(SQLModel, table=True):
    __tablename__ = "user_usage"

    # Hardcoded primary key so there is only ever ONE row in this table
    global_key: str = Field(default="global", primary_key=True)
    messages_sent: int = Field(default=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)