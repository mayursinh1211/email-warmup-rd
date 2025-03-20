from datetime import datetime, timedelta
import random
from typing import List, Dict
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
import aioimaplib
import logging
from .utils import generate_natural_response
from ..models.email_account import EmailAccount, WarmupStatus
from ..database.mongodb import MongoDB

logger = logging.getLogger(__name__)

class WarmupEngine:
    def __init__(self):
        self.active_accounts: Dict[str, EmailAccount] = {}
        self.network_pool: List[EmailAccount] = []
        self.engagement_patterns = [
            "read",
            "reply",
            "mark_important",
            "move_to_primary"
        ]

    async def initialize_network(self):
        """Initialize the warmup network with available accounts"""
        accounts = await MongoDB.db.email_accounts.find(
            {"status": "active"}
        ).to_list(None)
        
        for account in accounts:
            email_acc = EmailAccount(**account)
            self.active_accounts[email_acc.email] = email_acc
            self.network_pool.append(email_acc)

    async def send_warmup_email(self, from_account: EmailAccount, to_account: EmailAccount):
        """Send a warmup email from one account to another"""
        try:
            message = MIMEMultipart()
            message["From"] = from_account.email
            message["To"] = to_account.email
            message["Subject"] = await self._generate_natural_subject()
            
            body = await self._generate_email_body()
            message.attach(MIMEText(body, "plain"))
            
            async with aiosmtplib.SMTP(
                hostname=from_account.smtp_server,
                port=from_account.smtp_port,
                use_tls=True
            ) as smtp:
                await smtp.login(from_account.username, from_account.password)
                await smtp.send_message(message)
            
            await self._log_email_sent(from_account.email, to_account.email)
            return True
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False

    async def check_inbox_placement(self, account: EmailAccount):
        """Check inbox placement and spam status"""
        try:
            imap_client = aioimaplib.IMAP4_SSL(
                account.imap_server, 
                account.imap_port
            )
            await imap_client.wait_hello_from_server()
            await imap_client.login(account.username, account.password)
            
            # Check Inbox
            await imap_client.select('INBOX')
            _, inbox_messages = await imap_client.search('ALL')
            
            # Check Spam folder
            await imap_client.select('[Gmail]/Spam')
            _, spam_messages = await imap_client.search('ALL')
            
            inbox_count = len(inbox_messages[0].split())
            spam_count = len(spam_messages[0].split())
            
            await self._update_placement_stats(
                account.email, 
                inbox_count, 
                spam_count
            )
            
            await imap_client.logout()
            
        except Exception as e:
            logger.error(f"Error checking inbox: {str(e)}")

    async def process_warmup_cycle(self, account: EmailAccount):
        """Process a complete warmup cycle for an account"""
        # Calculate daily volume based on warmup stage
        daily_volume = self._calculate_daily_volume(account.warmup_stage)
        
        # Get network participants for this cycle
        participants = self._select_network_participants(
            daily_volume, 
            exclude_email=account.email
        )
        
        for participant in participants:
            # Send email
            success = await self.send_warmup_email(account, participant)
            if success:
                # Simulate natural delay
                await asyncio.sleep(random.randint(60, 300))
                
                # Process engagement
                await self._process_engagement(participant, account)
            
            # Update account metrics
            await self._update_account_metrics(account.email)

    async def _process_engagement(self, from_account: EmailAccount, to_account: EmailAccount):
        """Process engagement actions for received emails"""
        engagement = random.choice(self.engagement_patterns)
        
        if engagement == "reply":
            reply_content = await generate_natural_response()
            await self.send_warmup_email(from_account, to_account)
        
        await self._log_engagement(
            from_account.email,
            to_account.email,
            engagement
        )

    async def _update_account_metrics(self, email: str):
        """Update account metrics based on performance"""
        metrics = await MongoDB.db.email_metrics.find_one({"email": email})
        
        if metrics:
            # Calculate success rate
            total_sent = metrics.get("total_sent", 0)
            inbox_placement = metrics.get("inbox_placement", 0)
            spam_count = metrics.get("spam_count", 0)
            
            if total_sent > 0:
                success_rate = (inbox_placement / total_sent) * 100
                
                # Update warmup stage if criteria met
                if success_rate >= 95 and metrics.get("days_in_stage", 0) >= 7:
                    await MongoDB.db.email_accounts.update_one(
                        {"email": email},
                        {
                            "$inc": {
                                "warmup_stage": 1,
                                "daily_limit": 10
                            }
                        }
                    )

    def _calculate_daily_volume(self, warmup_stage: int) -> int:
        """Calculate daily email volume based on warmup stage"""
        base_volume = 5
        return base_volume * (2 ** (warmup_stage - 1))

    def _select_network_participants(
        self, 
        count: int, 
        exclude_email: str
    ) -> List[EmailAccount]:
        """Select random participants from the network"""
        available = [acc for acc in self.network_pool if acc.email != exclude_email]
        return random.sample(available, min(count, len(available)))

    async def _generate_natural_subject(self) -> str:
        """Generate a natural-looking email subject"""
        subjects = [
            "Quick question about the project",
            "Following up on our discussion",
            "Update on the recent changes",
            "Thoughts on this approach?",
            "Checking in"
        ]
        return random.choice(subjects)

    async def _generate_email_body(self) -> str:
        """Generate a natural-looking email body"""
        # This should be enhanced with more sophisticated content generation
        bodies = [
            "I hope this email finds you well. I wanted to follow up on our previous discussion.",
            "I've been reviewing the latest updates and had a few thoughts to share.",
            "Just checking in to see how things are progressing on your end.",
            "I came across something interesting that I thought might be relevant to our project."
        ]
        return random.choice(bodies)

    async def _log_email_sent(self, from_email: str, to_email: str):
        """Log email sending activity"""
        await MongoDB.db.email_logs.insert_one({
            "from_email": from_email,
            "to_email": to_email,
            "sent_at": datetime.utcnow(),
            "type": "warmup",
            "status": "sent"
        })

    async def _log_engagement(self, from_email: str, to_email: str, engagement_type: str):
        """Log engagement activity"""
        await MongoDB.db.engagement_logs.insert_one({
            "from_email": from_email,
            "to_email": to_email,
            "engagement_type": engagement_type,
            "timestamp](#)** ▋
