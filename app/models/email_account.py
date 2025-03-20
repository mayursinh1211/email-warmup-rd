from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class WarmupStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class EmailAccount(BaseModel):
    email: EmailStr
    smtp_server: str
    smtp_port: int
    imap_server: str
    imap_port: int
    username: str
    password: str
    status: WarmupStatus = WarmupStatus.PENDING
    warmup_stage: int = 1
    daily_limit: int = 5
    current_daily_sent: int = 0
    spam_score: float = 0.0
    inbox_placement_rate: float = 0.0
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_warmup: Optional[datetime] = None
    total_warmup_emails: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    spam_incidents: int = 0

class EmailMetrics(BaseModel):
    email: EmailStr
    total_sent: int = 0
    total_received: int = 0
    inbox_placement: int = 0
    spam_count: int = 0
    bounce_count: int = 0
    reply_count: int = 0
    days_in_stage: int = 0
    average_response_time: Optional[float] = None
    engagement_rate: float = 0.0
    last_updated: datetime = datetime.utcnow()

class WarmupSettings(BaseModel):
    initial_volume: int = 5
    max_volume: int = 100
    ramp_up_rate: float = 1.5
    min_days_in_stage: int = 7
    required_success_rate: float = 0.95
    engagement_delay_min: int = 60  # seconds
    engagement_delay_max: int = 300  # seconds

class EmailTemplate(BaseModel):
    subject: str
    body: str
    category: str
    variables: List[str] = []
    language: str = "en"
    created_at: datetime = datetime.utcnow()
