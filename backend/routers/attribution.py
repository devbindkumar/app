"""
Attribution endpoints - Cross-campaign attribution tracking and analysis
"""
from fastapi import APIRouter
from datetime import datetime, timezone
import uuid

from routers.shared import db

router = APIRouter(tags=["Attribution"])


@router.post("/attribution/track")
async def track_attribution_event(
    user_id: str,
    campaign_id: str,
    event_type: str,
    event_value: float = 0.0
):
    """Track an attribution event for cross-campaign analysis"""
    event = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "campaign_id": campaign_id,
        "event_type": event_type,
        "event_value": event_value,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await db.attribution_events.insert_one(event)
    
    return {"status": "tracked", "event_id": event["id"]}


@router.get("/attribution/user/{user_id}")
async def get_user_journey(user_id: str):
    """Get the complete attribution journey for a user"""
    events = await db.attribution_events.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(1000)
    
    if not events:
        return {"user_id": user_id, "journey": [], "campaigns_touched": []}
    
    campaigns_touched = list(set(e["campaign_id"] for e in events))
    
    campaign_names = {}
    for cid in campaigns_touched:
        campaign = await db.campaigns.find_one({"id": cid}, {"_id": 0, "name": 1})
        if campaign:
            campaign_names[cid] = campaign.get("name", "Unknown")
    
    journey = []
    for event in events:
        journey.append({
            "campaign_id": event["campaign_id"],
            "campaign_name": campaign_names.get(event["campaign_id"], "Unknown"),
            "event_type": event["event_type"],
            "event_value": event.get("event_value", 0),
            "timestamp": event["timestamp"]
        })
    
    return {
        "user_id": user_id,
        "campaigns_touched": len(campaigns_touched),
        "total_events": len(events),
        "journey": journey,
        "first_touch": journey[0] if journey else None,
        "last_touch": journey[-1] if journey else None
    }


@router.get("/attribution/analysis")
async def get_attribution_analysis(model: str = "last_touch"):
    """Get cross-campaign attribution analysis"""
    conversions = await db.attribution_events.find(
        {"event_type": "conversion"},
        {"_id": 0}
    ).to_list(10000)
    
    if not conversions:
        return {
            "model": model,
            "total_conversions": 0,
            "attribution": [],
            "message": "No conversion data available"
        }
    
    user_journeys = {}
    all_events = await db.attribution_events.find({}, {"_id": 0}).sort("timestamp", 1).to_list(100000)
    
    for event in all_events:
        uid = event["user_id"]
        if uid not in user_journeys:
            user_journeys[uid] = []
        user_journeys[uid].append(event)
    
    campaign_attribution = {}
    
    for uid, journey in user_journeys.items():
        conversions_in_journey = [e for e in journey if e["event_type"] == "conversion"]
        if not conversions_in_journey:
            continue
        
        touchpoints = [e for e in journey if e["event_type"] in ["impression", "click"]]
        if not touchpoints:
            continue
        
        total_conversion_value = sum(c.get("event_value", 1) for c in conversions_in_journey)
        
        if model == "first_touch":
            cid = touchpoints[0]["campaign_id"]
            if cid not in campaign_attribution:
                campaign_attribution[cid] = {"conversions": 0, "value": 0}
            campaign_attribution[cid]["conversions"] += len(conversions_in_journey)
            campaign_attribution[cid]["value"] += total_conversion_value
            
        elif model == "last_touch":
            cid = touchpoints[-1]["campaign_id"]
            if cid not in campaign_attribution:
                campaign_attribution[cid] = {"conversions": 0, "value": 0}
            campaign_attribution[cid]["conversions"] += len(conversions_in_journey)
            campaign_attribution[cid]["value"] += total_conversion_value
            
        elif model == "linear":
            credit_per_touch = total_conversion_value / len(touchpoints)
            for tp in touchpoints:
                cid = tp["campaign_id"]
                if cid not in campaign_attribution:
                    campaign_attribution[cid] = {"conversions": 0, "value": 0}
                campaign_attribution[cid]["conversions"] += len(conversions_in_journey) / len(touchpoints)
                campaign_attribution[cid]["value"] += credit_per_touch
                
        elif model == "time_decay":
            decay_factor = 0.7
            total_weight = sum(decay_factor ** i for i in range(len(touchpoints)))
            
            for idx, tp in enumerate(reversed(touchpoints)):
                weight = (decay_factor ** idx) / total_weight
                cid = tp["campaign_id"]
                if cid not in campaign_attribution:
                    campaign_attribution[cid] = {"conversions": 0, "value": 0}
                campaign_attribution[cid]["conversions"] += len(conversions_in_journey) * weight
                campaign_attribution[cid]["value"] += total_conversion_value * weight
    
    results = []
    for cid, stats in campaign_attribution.items():
        campaign = await db.campaigns.find_one({"id": cid}, {"_id": 0, "name": 1})
        results.append({
            "campaign_id": cid,
            "campaign_name": campaign.get("name", "Unknown") if campaign else "Unknown",
            "attributed_conversions": round(stats["conversions"], 2),
            "attributed_value": round(stats["value"], 2),
            "attribution_share": 0
        })
    
    total_conversions = sum(r["attributed_conversions"] for r in results)
    for r in results:
        r["attribution_share"] = round((r["attributed_conversions"] / total_conversions * 100) if total_conversions > 0 else 0, 2)
    
    results.sort(key=lambda x: x["attributed_value"], reverse=True)
    
    return {
        "model": model,
        "total_conversions": total_conversions,
        "total_value": sum(r["attributed_value"] for r in results),
        "attribution": results,
        "available_models": ["first_touch", "last_touch", "linear", "time_decay"]
    }
