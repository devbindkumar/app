"""
Creative management endpoints - CRUD operations, validation
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from models import Creative, CreativeCreate, CreativeType
from routers.shared import db

router = APIRouter(tags=["Creatives"])


@router.get("/creatives", response_model=List[Creative])
async def get_creatives(type: Optional[str] = None):
    """Get all creatives"""
    query = {}
    if type:
        query["type"] = type
    
    creatives = await db.creatives.find(query, {"_id": 0}).to_list(1000)
    return creatives


@router.get("/creatives/{creative_id}", response_model=Creative)
async def get_creative(creative_id: str):
    """Get a single creative"""
    creative = await db.creatives.find_one({"id": creative_id}, {"_id": 0})
    if not creative:
        raise HTTPException(status_code=404, detail="Creative not found")
    return creative


@router.post("/creatives", response_model=Creative)
async def create_creative(input: CreativeCreate):
    """Create a new creative"""
    creative = Creative(
        name=input.name,
        type=input.type,
        format=input.format,
        adomain=input.adomain,
        iurl=input.iurl,
        cat=input.cat,
        banner_data=input.banner_data,
        video_data=input.video_data,
        native_data=input.native_data,
        audio_data=input.audio_data,
        js_tag=input.js_tag
    )
    
    # Generate preview URL based on creative type
    if creative.type == CreativeType.BANNER:
        if creative.banner_data and creative.banner_data.image_url:
            creative.preview_url = creative.banner_data.image_url
        elif creative.iurl:
            creative.preview_url = creative.iurl
    elif creative.type == CreativeType.VIDEO:
        if creative.video_data:
            if creative.video_data.vast_url:
                creative.preview_url = creative.video_data.vast_url
            elif creative.video_data.video_url:
                creative.preview_url = creative.video_data.video_url
    
    doc = creative.model_dump()
    for field in ["created_at", "updated_at"]:
        if doc.get(field):
            doc[field] = doc[field].isoformat()
    
    await db.creatives.insert_one(doc)
    return creative


@router.delete("/creatives/{creative_id}")
async def delete_creative(creative_id: str):
    """Delete a creative"""
    # Check if used by campaigns
    campaign = await db.campaigns.find_one({"creative_id": creative_id})
    if campaign:
        raise HTTPException(status_code=400, detail="Creative is used by a campaign")
    
    result = await db.creatives.delete_one({"id": creative_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Creative not found")
    return {"status": "deleted"}


@router.post("/creatives/validate")
async def validate_creative(creative_data: dict):
    """Validate creative data"""
    issues = []
    warnings = []
    
    creative_type = creative_data.get("type")
    
    if creative_type == "banner":
        banner = creative_data.get("banner_data", {})
        if not banner.get("width") or not banner.get("height"):
            issues.append("Banner dimensions are required")
        if not banner.get("image_url"):
            issues.append("Banner image URL is required")
        
        # Check for common sizes
        common_sizes = [(300, 250), (728, 90), (160, 600), (320, 50), (300, 600)]
        size = (banner.get("width"), banner.get("height"))
        if size not in common_sizes:
            warnings.append(f"Banner size {size} is not a standard IAB size")
    
    elif creative_type == "video":
        video = creative_data.get("video_data", {})
        if not video.get("vast_url") and not video.get("video_url"):
            issues.append("Video URL or VAST tag is required")
        if not video.get("duration"):
            warnings.append("Video duration not specified")
    
    elif creative_type == "native":
        native = creative_data.get("native_data", {})
        if not native.get("title"):
            issues.append("Native ad title is required")
        if not native.get("image_url"):
            warnings.append("Native ad main image recommended")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings
    }
