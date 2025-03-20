import pytest
from datetime import datetime, timedelta
from app.core.email_warmup import EmailWarmupManager
from app.models.email import EmailAccount, EmailCampaign
from app.database.mongodb import MongoDB

@pytest.mark.asyncio
async def test_send_email():
    email_account = EmailAccount(
        email="test@example.com",
        smtp_server="smtp.example.com",
        smtp_port=587,
        imap_server="imap.example.com",
        imap_port=993,
        username="test@example.com",
        password="test_password"
    )
    
    result = await EmailWarmupManager.send_email(
        email_account,
        "recipient@example.com",
        "Test Subject",
        "Test Content"
    )
    
    assert isinstance(result, bool)

@pytest.mark.asyncio
async def test_calculate_success_rate():
    # Insert test data
    await MongoDB.db.email_logs.insert_many([
        {
            "from_email": "test@example.com",
            "sent_at": datetime.utcnow(),
            "delivered": True
        },
        {
            "from_email": "test@example.com",
            "sent_at": datetime.utcnow(),
            "delivered": False
        }
    ])
    
    success_rate = await EmailWarmupManager.calculate_success_rate("test@example.com")
    assert success_rate == 0.5
    
    # Cleanup
    await MongoDB.db.email_logs.delete_many({"from_email": "test@example.com"})
