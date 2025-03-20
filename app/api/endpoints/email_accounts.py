from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime
from ...models.email_account import EmailAccount, EmailMetrics, WarmupStatus
from ...core.warmup_engine import WarmupEngine
from ...database.mongodb import MongoDB
from ...core.auth import get_current_user

router = APIRouter()
warmup_engine = WarmupEngine()

@router.post("/accounts/", response_model=EmailAccount)
async def add_email_account(
    account: EmailAccount,
    current_user = Depends(get_current_user)
):
    """Add a new email account to the warmup system"""
    # Check if account already exists
    existing = await MongoDB.db.email_accounts.find_one({"email": account.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email account already exists"
        )
    
    # Validate SMTP/IMAP connections
    try:
        # Test SMTP connection
        await warmup_engine.send_warmup_email(account, account)  # Send test email to self
        
        # Test IMAP connection
        await warmup_engine.check_inbox_placement(account)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to validate email account: {str(e)}"
        )
    
    # Save account to database
    account_dict = account.model_dump()
    account_dict["user_id"] = str(current_user.id)
    result = await MongoDB.db.email_accounts.insert_one(account_dict)
    
    # Initialize metrics
    await MongoDB.db.email_metrics.insert_one({
        "email": account.email,
        "created_at": datetime.utcnow()
    })
    
    account_dict["id"] = str(result.inserted_id)
    return EmailAccount(**account_dict)

@router.get("/accounts/", response_model=List[EmailAccount])
async def get_email_accounts(current_user = Depends(get_current_user)):
    """Get all email accounts for the current user"""
    accounts = await MongoDB.db.email_accounts.find(
        {"user_id": str(current_user.id)}
    ).to_list(None)
    return [EmailAccount(**account) for account in accounts]

@router.get("/accounts/{email}/metrics", response_model=EmailMetrics)
async def get_account_metrics(
    email: str,
    current_user = Depends(get_current_user)
):
    """Get metrics for a specific email account"""
    metrics = await MongoDB.db.email_metrics.find_one({"email": email})
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account metrics not found"
        )
    return EmailMetrics(**metrics)

@router.post("/accounts/{email}/pause")
async def pause_warmup(
    email: str,
    current_user = Depends(get_current_user)
):
    """Pause warmup for an email account"""
    result = await MongoDB.db.email_accounts.update_one(
        {"email": email, "user_id": str(current_user.id)},
        {"$set": {"status": WarmupStatus.PAUSED}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    return {"message": "Warmup paused successfully"}

@router.post("/accounts/{email}/resume")
async def resume_warmup(
    email: str,
    current_user = Depends(get_current_user)
):
    """Resume warmup for an email account"""
    result = await MongoDB.db.email_accounts.update_one(
        {"email": email, "user_id": str(current_user.id)},
        {"$set": {"status": WarmupStatus.ACTIVE}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    return {"message": "Warmup resumed successfully"}

@router.delete("/accounts/{email}")
async def delete_account(
    email: str,
    current_user = Depends(get_current_user)
):
    """Delete an email account"""
    result = await MongoDB.db.email_accounts.delete_one(
        {"email": email, "user_id": str(current_user.id)}
    )
    
    if result.deleted_count == 
