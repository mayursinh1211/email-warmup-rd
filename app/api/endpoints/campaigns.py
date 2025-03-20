from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ...models.email import EmailCampaign
from ...database.mongodb import MongoDB
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.post("/campaigns/", response_model=EmailCampaign)
async def create_campaign(campaign: EmailCampaign):
    campaign_dict = campaign.model_dump()
    campaign_dict["created_at"] = datetime.utcnow()
    campaign_dict["updated_at"] = datetime.utcnow()
    
    result = await MongoDB.db.email_campaigns.insert_one(campaign_dict)
    campaign_dict["id"] = str(result.inserted_id)
    
    return EmailCampaign(**campaign_dict)

@router.get("/campaigns/{campaign_id}", response_model=EmailCampaign)
async def get_campaign(campaign_id: str):
    campaign = await MongoDB.db.email_campaigns.find_one({"_id": ObjectId(campaign_id)})
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    campaign["id"] = str(campaign["_id"])
    return EmailCampaign(**campaign)

@router.put("/campaigns/{campaign_id}", response_model=EmailCampaign)
async def update_campaign(campaign_id: str, campaign_update: EmailCampaign):
    update_dict = campaign_update.model_dump()
    update_dict["updated_at"] = datetime.utcnow()
    
    result = await MongoDB.db.email_campaigns.update_one(
        {"_id": ObjectId(campaign_id)},
        {"$set": update_dict}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    campaign = await MongoDB.db.email_campaigns.find_one({"_id": ObjectId(campaign_id)})
    campaign["id"] = str(campaign["_id"])
    return EmailCampaign(**campaign)

@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    result = await MongoDB.db.email_campaigns.delete_one({"_id": ObjectId(campaign_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return {"message": "Campaign deleted successfully"}
