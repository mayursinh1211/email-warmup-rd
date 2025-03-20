from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class EmailAccount(BaseModel):
    email: EmailStr
    smtp_server: str
    smtp_port: int
    imap_server: str
    imap_port: int
    username: str
    password: str
    is_active: bool = True
    daily_limit: int = 50
    warmup_stage: int = 1

class EmailCampaign(BaseModel):
    id: str
    user_id: str
    name: str
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    daily_increment: int = 5
    target_daily_emails: int = 100
    current_daily_emails: int = 0
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class EmailLog(BaseModel):
    id: str
    campaign_id: str
    from_email: EmailStr
    to_email: EmailStr
    subject: str
    sent_at: datetime
    delivered: bool
    opened: bool
    replied: bool
    spam_score: Optional[float]
