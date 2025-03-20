import asyncio
from datetime import datetime, timedelta
from typing import List
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..models.email import EmailAccount, EmailCampaign, EmailLog
from ..database.mongodb import MongoDB
import logging

logger = logging.getLogger(__name__)

class EmailWarmupManager:
    @staticmethod
    async def send_email(email_account: EmailAccount, to_email: str, subject: str, content: str) -> bool:
        try:
            message = MIMEMultipart()
            message["From"] = email_account.email
            message["To"] = to_email
            message["Subject"] = subject
            
            message.attach(MIMEText(content, "plain"))
            
            async with aiosmtplib.SMTP(
                hostname=email_account.smtp_server,
                port=email_account.smtp_port,
                use_tls=True
            ) as smtp:
                await smtp.login(email_account.username, email_account.password)
                await smtp.send_message(message)
            
            return True
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False

    @staticmethod
    async def process_campaign(campaign_id: str):
        campaign = await MongoDB.db.email_campaigns.find_one({"_id": campaign_id})
        if not campaign:
            return
        
        email_accounts = await MongoDB.db.email_accounts.find(
            {"user_id": campaign["user_id"], "is_active": True}
        ).to_list(None)
        
        if not email_accounts:
            return
        
        for account in email_accounts:
            emails_sent_today = await MongoDB.db.email_logs.count_documents({
                "from_email": account["email"],
                "sent_at": {"$gte": datetime.utcnow() - timedelta(days=1)}
            })
            
            if emails_sent_today >= account["daily_limit"]:
                continue
                
            emails_to_send = min(
                account["daily_limit"] - emails_sent_today,
                campaign["target_daily_emails"] - campaign["current_daily_emails"]
            )
            
            for _ in range(emails_to_send):
                # Get target email from pool
                target_email = await MongoDB.db.email_pool.find_one({
                    "campaign_id": campaign_id,
                    "status": "pending"
                })
                
                if not target_email:
                    continue
                
                success = await EmailWarmupManager.send_email(
                    EmailAccount(**account),
                    target_email["email"],
                    "Test Email for Warmup",
                    "This is a test email for warming up the email account."
                )
                
                if success:
                    await MongoDB.db.email_logs.insert_one({
                        "campaign_id": campaign_id,
                        "from_email": account["email"],
                        "to_email": target_email["email"],
                        "subject": "Test Email for Warmup",
                        "sent_at": datetime.utcnow(),
                        "delivered": True,
                        "opened": False,
                        "replied": False
                    })
                    
                    await MongoDB.db.email_pool.update_one(
                        {"_id": target_email["_id"]},
                        {"$set": {"status": "sent"}}
                    )

    @staticmethod
    async def update_warmup_stage(email_account_id: str):
        account = await MongoDB.db.email_accounts.find_one({"_id": email_account_id})
        if not account:
            return
            
        success_rate = await EmailWarmupManager.calculate_success_rate(account["email"])
        
        if success_rate >= 0.95 and account["warmup_stage"] < 5:
            await MongoDB.db.email_accounts.update_one(
                {"_id": email_account_id},
                {
                    "$inc": {
                        "warmup_stage": 1,
                        "daily_limit": 10
                    }
                }
            )

    @staticmethod
    async def calculate_success_rate(email: str) -> float:
        total_logs = await MongoDB.db.email_logs.count_documents({
            "from_email": email,
            "sent_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
        })
        
        if total_logs == 0:
            return 0.0
            
        successful_deliveries = await MongoDB.db.email_logs.count_documents({
            "from_email": email,
            "sent_at": {"$gte": datetime.utcnow() - timedelta(days=7)},
            "delivered": True
        })
        
        return successful_deliveries / total_logs
