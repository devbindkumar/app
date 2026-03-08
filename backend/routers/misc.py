"""
Misc endpoints - Insights, Currencies, Comparison, A/B Testing, Audiences, Uploads
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from pathlib import Path
import uuid
import shutil
import os

from routers.shared import db

router = APIRouter(tags=["Miscellaneous"])


# Create uploads directory
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


# ==================== CURRENCY ====================

CURRENCY_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "CAD": 1.36,
    "AUD": 1.53,
    "JPY": 149.5
}

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "CAD": "C$",
    "AUD": "A$",
    "JPY": "¥"
}


@router.get("/currencies")
async def get_supported_currencies():
    """Get list of supported currencies with conversion rates"""
    return {
        "base_currency": "USD",
        "currencies": [
            {"code": code, "symbol": CURRENCY_SYMBOLS.get(code, code), "rate": rate}
            for code, rate in CURRENCY_RATES.items()
        ]
    }


@router.get("/currency/convert")
async def convert_currency(amount: float, from_currency: str = "USD", to_currency: str = "USD"):
    """Convert amount between currencies"""
    if from_currency not in CURRENCY_RATES or to_currency not in CURRENCY_RATES:
        raise HTTPException(status_code=400, detail="Unsupported currency")
    
    usd_amount = amount / CURRENCY_RATES[from_currency]
    converted = usd_amount * CURRENCY_RATES[to_currency]
    
    return {
        "original": {"amount": amount, "currency": from_currency},
        "converted": {"amount": round(converted, 2), "currency": to_currency},
        "rate": CURRENCY_RATES[to_currency] / CURRENCY_RATES[from_currency]
    }


# ==================== CAMPAIGN COMPARISON ====================

class CampaignCompareRequest(BaseModel):
    campaign_ids: List[str]


@router.post("/campaigns/compare")
async def compare_campaigns(request: CampaignCompareRequest):
    """Compare 2-3 campaigns side by side"""
    campaign_ids = request.campaign_ids
    if len(campaign_ids) < 2 or len(campaign_ids) > 3:
        raise HTTPException(status_code=400, detail="Select 2-3 campaigns to compare")
    
    campaigns = []
    for cid in campaign_ids:
        campaign = await db.campaigns.find_one({"id": cid}, {"_id": 0})
        if campaign:
            campaigns.append(campaign)
    
    if len(campaigns) < 2:
        raise HTTPException(status_code=404, detail="One or more campaigns not found")
    
    comparison = {
        "campaigns": campaigns,
        "metrics_comparison": {},
        "targeting_differences": {},
        "recommendations": []
    }
    
    metrics = ["bids", "wins", "impressions", "clicks", "bid_price"]
    for metric in metrics:
        values = [c.get(metric, 0) for c in campaigns]
        comparison["metrics_comparison"][metric] = {
            "values": values,
            "best": campaign_ids[values.index(max(values))] if max(values) > 0 else None,
            "diff_pct": round((max(values) - min(values)) / max(values) * 100, 2) if max(values) > 0 else 0
        }
    
    win_rates = []
    for c in campaigns:
        bids = c.get("bids", 0)
        wins = c.get("wins", 0)
        win_rates.append(round(wins / bids * 100, 2) if bids > 0 else 0)
    comparison["metrics_comparison"]["win_rate"] = {
        "values": win_rates,
        "best": campaign_ids[win_rates.index(max(win_rates))] if max(win_rates) > 0 else None
    }
    
    targeting_fields = ["geo.countries", "device.device_types", "inventory.categories"]
    for field in targeting_fields:
        parts = field.split(".")
        values = []
        for c in campaigns:
            val = c.get("targeting", {})
            for p in parts:
                val = val.get(p, []) if isinstance(val, dict) else []
            values.append(set(val) if isinstance(val, list) else set())
        
        common = set.intersection(*values) if values else set()
        unique = [v - common for v in values]
        comparison["targeting_differences"][field] = {
            "common": list(common),
            "unique": [list(u) for u in unique]
        }
    
    if comparison["metrics_comparison"]["win_rate"]["values"]:
        best_idx = win_rates.index(max(win_rates))
        worst_idx = win_rates.index(min(win_rates))
        if best_idx != worst_idx:
            comparison["recommendations"].append({
                "type": "win_rate",
                "message": f"Consider adopting targeting from '{campaigns[best_idx]['name']}' for '{campaigns[worst_idx]['name']}'"
            })
    
    return comparison


# ==================== A/B TESTING ====================

class ABTestCreate(BaseModel):
    name: str
    campaign_ids: List[str]
    traffic_split: Optional[List[float]] = None


@router.post("/ab-tests")
async def create_ab_test(data: ABTestCreate):
    """Create an A/B test between campaigns"""
    if len(data.campaign_ids) < 2 or len(data.campaign_ids) > 4:
        raise HTTPException(status_code=400, detail="Select 2-4 campaigns for A/B test")
    
    traffic_split = data.traffic_split
    if traffic_split is None:
        traffic_split = [100 / len(data.campaign_ids)] * len(data.campaign_ids)
    
    if len(traffic_split) != len(data.campaign_ids) or abs(sum(traffic_split) - 100) > 0.1:
        raise HTTPException(status_code=400, detail="Traffic split must add up to 100%")
    
    campaigns = []
    for cid in data.campaign_ids:
        campaign = await db.campaigns.find_one({"id": cid}, {"_id": 0, "id": 1, "name": 1})
        if not campaign:
            raise HTTPException(status_code=404, detail=f"Campaign {cid} not found")
        campaigns.append(campaign)
    
    ab_test = {
        "id": str(uuid.uuid4()),
        "name": data.name,
        "status": "active",
        "campaign_ids": data.campaign_ids,
        "campaign_names": [c["name"] for c in campaigns],
        "traffic_split": traffic_split,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "stats": {cid: {"impressions": 0, "clicks": 0, "conversions": 0} for cid in data.campaign_ids}
    }
    
    await db.ab_tests.insert_one(ab_test)
    if "_id" in ab_test:
        del ab_test["_id"]
    
    return ab_test


@router.get("/ab-tests")
async def get_ab_tests():
    """Get all A/B tests"""
    tests = await db.ab_tests.find({}, {"_id": 0}).to_list(100)
    return {"tests": tests}


@router.get("/ab-tests/{test_id}")
async def get_ab_test(test_id: str):
    """Get A/B test details with performance data"""
    test = await db.ab_tests.find_one({"id": test_id}, {"_id": 0})
    if not test:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    for cid in test["campaign_ids"]:
        campaign = await db.campaigns.find_one({"id": cid}, {"_id": 0})
        if campaign:
            bids = campaign.get("bids", 0)
            wins = campaign.get("wins", 0)
            test["stats"][cid]["bids"] = bids
            test["stats"][cid]["wins"] = wins
            test["stats"][cid]["win_rate"] = round(wins / bids * 100, 2) if bids > 0 else 0
    
    winner = None
    best_metric = 0
    for cid, stats in test["stats"].items():
        if stats.get("win_rate", 0) > best_metric:
            best_metric = stats["win_rate"]
            winner = cid
    
    test["winner"] = winner
    test["winner_name"] = None
    if winner:
        for idx, cid in enumerate(test["campaign_ids"]):
            if cid == winner:
                test["winner_name"] = test["campaign_names"][idx]
                break
    
    return test


@router.delete("/ab-tests/{test_id}")
async def delete_ab_test(test_id: str):
    """Delete an A/B test"""
    result = await db.ab_tests.delete_one({"id": test_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="A/B test not found")
    return {"status": "deleted"}


# ==================== AUDIENCES ====================

class AudienceCreate(BaseModel):
    name: str
    description: str = ""
    rules: dict = {}


@router.post("/audiences")
async def create_audience(data: AudienceCreate):
    """Create an audience segment"""
    audience = {
        "id": str(uuid.uuid4()),
        "name": data.name,
        "description": data.description,
        "rules": data.rules,
        "user_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.audiences.insert_one(audience)
    if "_id" in audience:
        del audience["_id"]
    
    return audience


@router.get("/audiences")
async def get_audiences():
    """Get all audience segments"""
    audiences = await db.audiences.find({}, {"_id": 0}).to_list(100)
    return {"audiences": audiences}


@router.get("/audiences/{audience_id}")
async def get_audience(audience_id: str):
    """Get audience segment details"""
    audience = await db.audiences.find_one({"id": audience_id}, {"_id": 0})
    if not audience:
        raise HTTPException(status_code=404, detail="Audience not found")
    return audience


@router.delete("/audiences/{audience_id}")
async def delete_audience(audience_id: str):
    """Delete audience segment"""
    result = await db.audiences.delete_one({"id": audience_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Audience not found")
    return {"status": "deleted"}


# ==================== CAMPAIGN INSIGHTS ====================

@router.get("/insights/campaigns")
async def get_campaign_insights():
    """Analyze all campaigns and provide actionable insights"""
    campaigns = await db.campaigns.find({}, {"_id": 0}).to_list(1000)
    
    insights = []
    overall_health = {"healthy": 0, "warning": 0, "critical": 0}
    
    for campaign in campaigns:
        campaign_insight = {
            "campaign_id": campaign["id"],
            "campaign_name": campaign["name"],
            "status": campaign.get("status", "draft"),
            "health_score": 100,
            "health_status": "healthy",
            "issues": [],
            "recommendations": [],
            "metrics": {}
        }
        
        bids = campaign.get("bids", 0)
        wins = campaign.get("wins", 0)
        impressions = campaign.get("impressions", 0)
        clicks = campaign.get("clicks", 0)
        
        win_rate = (wins / bids * 100) if bids > 0 else 0
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        
        campaign_insight["metrics"] = {
            "bids": bids,
            "wins": wins,
            "impressions": impressions,
            "clicks": clicks,
            "win_rate": round(win_rate, 2),
            "ctr": round(ctr, 2)
        }
        
        # Analyze issues
        if campaign.get("status") == "active" and bids == 0:
            campaign_insight["issues"].append({
                "severity": "critical",
                "message": "Active campaign has no bids - check targeting or SSP connections"
            })
            campaign_insight["health_score"] -= 40
        
        if bids > 100 and win_rate < 5:
            campaign_insight["issues"].append({
                "severity": "warning",
                "message": f"Very low win rate ({win_rate:.1f}%) - consider increasing bid price"
            })
            campaign_insight["health_score"] -= 20
            campaign_insight["recommendations"].append("Increase bid price or enable bid optimization")
        
        if impressions > 1000 and ctr < 0.1:
            campaign_insight["issues"].append({
                "severity": "warning",
                "message": f"Very low CTR ({ctr:.2f}%) - review creative quality"
            })
            campaign_insight["health_score"] -= 15
            campaign_insight["recommendations"].append("Test new creative variations")
        
        budget = campaign.get("budget", {})
        if budget.get("daily_budget") and budget.get("daily_spend", 0) >= budget.get("daily_budget", 0):
            campaign_insight["issues"].append({
                "severity": "info",
                "message": "Daily budget exhausted"
            })
        
        # Determine health status
        if campaign_insight["health_score"] < 50:
            campaign_insight["health_status"] = "critical"
            overall_health["critical"] += 1
        elif campaign_insight["health_score"] < 80:
            campaign_insight["health_status"] = "warning"
            overall_health["warning"] += 1
        else:
            overall_health["healthy"] += 1
        
        insights.append(campaign_insight)
    
    insights.sort(key=lambda x: x["health_score"])
    
    return {
        "overall_health": overall_health,
        "campaigns": insights,
        "top_issues": [i for i in insights if i["health_status"] != "healthy"][:5]
    }


# ==================== FILE UPLOAD ====================

@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image file for creative assets"""
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed: {allowed_types}")
    
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = UPLOAD_DIR / filename
    
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    base_url = os.environ.get('REACT_APP_BACKEND_URL', '')
    file_url = f"{base_url}/api/uploads/{filename}"
    
    return {
        "filename": filename,
        "url": file_url,
        "content_type": file.content_type,
        "size": filepath.stat().st_size
    }


@router.get("/uploads/{filename}")
async def get_uploaded_file(filename: str):
    """Serve uploaded files"""
    filepath = UPLOAD_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    ext = filename.split('.')[-1].lower()
    content_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp"
    }
    content_type = content_types.get(ext, "application/octet-stream")
    
    return FileResponse(filepath, media_type=content_type)


@router.delete("/uploads/{filename}")
async def delete_uploaded_file(filename: str):
    """Delete an uploaded file"""
    filepath = UPLOAD_DIR / filename
    if filepath.exists():
        filepath.unlink()
    return {"status": "deleted"}


# ==================== FRAUD DETECTION ====================

@router.get("/fraud/detection/{campaign_id}")
async def analyze_fraud_indicators(campaign_id: str):
    """Analyze potential fraud indicators for a campaign"""
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    logs = await db.bid_logs.find(
        {"campaign_id": campaign_id, "bid_made": True},
        {"_id": 0}
    ).to_list(1000)
    
    if not logs:
        return {
            "campaign_id": campaign_id,
            "fraud_score": 0,
            "indicators": [],
            "message": "Not enough data to analyze"
        }
    
    indicators = []
    fraud_score = 0
    
    # Analyze patterns
    ip_counts = {}
    ua_counts = {}
    bundle_counts = {}
    
    for log in logs:
        summary = log.get("request_summary", {})
        ip = summary.get("ip", "unknown")
        ua = summary.get("user_agent", "unknown")
        bundle = summary.get("bundle", "unknown")
        
        ip_counts[ip] = ip_counts.get(ip, 0) + 1
        ua_counts[ua] = ua_counts.get(ua, 0) + 1
        bundle_counts[bundle] = bundle_counts.get(bundle, 0) + 1
    
    # Check for IP concentration
    total_bids = len(logs)
    max_ip_count = max(ip_counts.values()) if ip_counts else 0
    ip_concentration = max_ip_count / total_bids if total_bids > 0 else 0
    
    if ip_concentration > 0.5:
        indicators.append({
            "type": "ip_concentration",
            "severity": "high",
            "message": f"Single IP accounts for {ip_concentration*100:.1f}% of traffic"
        })
        fraud_score += 30
    elif ip_concentration > 0.3:
        indicators.append({
            "type": "ip_concentration",
            "severity": "medium",
            "message": f"Single IP accounts for {ip_concentration*100:.1f}% of traffic"
        })
        fraud_score += 15
    
    # Check user agent diversity
    ua_diversity = len(ua_counts) / total_bids if total_bids > 0 else 0
    if ua_diversity < 0.1 and total_bids > 100:
        indicators.append({
            "type": "low_ua_diversity",
            "severity": "medium",
            "message": "Very low user agent diversity suggests bot traffic"
        })
        fraud_score += 20
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.get("name"),
        "fraud_score": min(fraud_score, 100),
        "risk_level": "high" if fraud_score >= 50 else "medium" if fraud_score >= 25 else "low",
        "indicators": indicators,
        "analyzed_bids": total_bids,
        "unique_ips": len(ip_counts),
        "unique_user_agents": len(ua_counts)
    }
