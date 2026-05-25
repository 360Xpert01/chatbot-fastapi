# app/services/usage_service.py
from sqlmodel import Session, select
from app.modules.usage.model import UserUsage
from app.core.config import settings
from datetime import datetime

class UsageService:
    
    @staticmethod
    def check_and_increment(db: Session) -> bool:
        """
        Checks if the global message limit has been reached across the whole app. 
        If not, increments the global count and returns True.
        """
        # 1. Fetch or create the single global usage record
        statement = select(UserUsage).where(UserUsage.global_key == "global")
        usage = db.exec(statement).first()
        
        if not usage:
            usage = UserUsage(global_key="global", messages_sent=0)
            db.add(usage)
            
        # 2. Guardrail check against your hardcoded config limit
        if usage.messages_sent >= settings.CHAT_MESSAGE_LIMIT:
            return False
            
        # 3. Increment, update timestamp, and commit permanently
        usage.messages_sent += 1
        usage.last_updated = datetime.utcnow()
        db.add(usage)
        db.commit()
        return True