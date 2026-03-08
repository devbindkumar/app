"""
Optimization endpoints - Bid optimization, ML prediction, frequency capping, SPO
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import uuid

from models import BidPredictionFeatures
from routers.shared import db

router = APIRouter(tags=["Optimization"])


# ==================== FREQUENCY CAPPING ====================

@router.get("/frequency/{campaign_id}/{user_id}")
async def get_user_frequency(campaign_id: str, user_id: str):
    """Get impression frequency for a user on a campaign"""
    freq = await db.user_frequencies.find_one(
        {"campaign_id": campaign_id, "user_id": user_id},
        {"_id": 0}
    )
    
    if not freq:
        return {"campaign_id": campaign_id, "user_id": user_id, "impression_count": 0}
    
    return freq


@router.post("/frequency/record")
async def record_impression(campaign_id: str, user_id: str):
    """Record an impression for frequency capping"""
    now = datetime.now(timezone.utc)
    hour_key = now.strftime("%Y-%m-%d-%H")
    
    await db.user_frequencies.update_one(
        {"campaign_id": campaign_id, "user_id": user_id},
        {
            "$inc": {"impression_count": 1, f"hourly_impressions.{hour_key}": 1},
            "$set": {"last_impression": now.isoformat()}
        },
        upsert=True
    )
    
    return {"status": "recorded", "campaign_id": campaign_id, "user_id": user_id}


@router.delete("/frequency/reset/{campaign_id}")
async def reset_campaign_frequency(campaign_id: str):
    """Reset all frequency data for a campaign"""
    result = await db.user_frequencies.delete_many({"campaign_id": campaign_id})
    return {"status": "reset", "deleted_count": result.deleted_count}


# ==================== ML PREDICTION ====================

@router.get("/ml/stats/{campaign_id}")
async def get_ml_stats(campaign_id: str):
    """Get ML model statistics for a campaign"""
    stats = await db.ml_model_stats.find(
        {"campaign_id": campaign_id},
        {"_id": 0}
    ).to_list(1000)
    
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    
    return {
        "campaign_id": campaign_id,
        "ml_enabled": campaign.get("ml_prediction", {}).get("enabled", False) if campaign else False,
        "feature_stats": stats,
        "total_data_points": sum(s.get("total_bids", 0) for s in stats)
    }


@router.post("/ml/train/{campaign_id}")
async def train_ml_model(campaign_id: str):
    """Train/update ML model from historical data"""
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    logs = await db.bid_logs.find(
        {"campaign_id": campaign_id, "bid_made": True},
        {"_id": 0}
    ).to_list(10000)
    
    if len(logs) < 100:
        return {
            "status": "insufficient_data",
            "data_points": len(logs),
            "required": 100
        }
    
    feature_stats = {}
    
    for log in logs:
        summary = log.get("request_summary", {})
        
        # Device type feature
        device_type = summary.get("device_type")
        if device_type:
            key = f"device_type:{device_type}"
            if key not in feature_stats:
                feature_stats[key] = {"bids": 0, "wins": 0, "total_price": 0, "total_win_price": 0}
            feature_stats[key]["bids"] += 1
            feature_stats[key]["total_price"] += log.get("shaded_price") or log.get("bid_price", 0)
            if log.get("win_notified"):
                feature_stats[key]["wins"] += 1
                feature_stats[key]["total_win_price"] += log.get("win_price", 0)
        
        # Geo country feature
        country = summary.get("country")
        if country:
            key = f"geo_country:{country}"
            if key not in feature_stats:
                feature_stats[key] = {"bids": 0, "wins": 0, "total_price": 0, "total_win_price": 0}
            feature_stats[key]["bids"] += 1
            feature_stats[key]["total_price"] += log.get("shaded_price") or log.get("bid_price", 0)
            if log.get("win_notified"):
                feature_stats[key]["wins"] += 1
                feature_stats[key]["total_win_price"] += log.get("win_price", 0)
        
        # OS feature
        os_name = summary.get("os")
        if os_name:
            key = f"os:{os_name}"
            if key not in feature_stats:
                feature_stats[key] = {"bids": 0, "wins": 0, "total_price": 0, "total_win_price": 0}
            feature_stats[key]["bids"] += 1
            feature_stats[key]["total_price"] += log.get("shaded_price") or log.get("bid_price", 0)
            if log.get("win_notified"):
                feature_stats[key]["wins"] += 1
                feature_stats[key]["total_win_price"] += log.get("win_price", 0)
    
    now = datetime.now(timezone.utc)
    for key, stats in feature_stats.items():
        win_rate = stats["wins"] / stats["bids"] if stats["bids"] > 0 else 0
        avg_bid = stats["total_price"] / stats["bids"] if stats["bids"] > 0 else 0
        avg_win = stats["total_win_price"] / stats["wins"] if stats["wins"] > 0 else 0
        
        await db.ml_model_stats.update_one(
            {"campaign_id": campaign_id, "feature_key": key},
            {"$set": {
                "total_bids": stats["bids"],
                "total_wins": stats["wins"],
                "win_rate": win_rate,
                "avg_bid_price": avg_bid,
                "avg_win_price": avg_win,
                "last_updated": now.isoformat()
            }},
            upsert=True
        )
    
    return {
        "status": "trained",
        "campaign_id": campaign_id,
        "data_points": len(logs),
        "features_trained": len(feature_stats)
    }


@router.post("/ml/predict")
async def predict_bid_price(campaign_id: str, features: BidPredictionFeatures):
    """Predict optimal bid price based on features"""
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    base_price = campaign.get("bid_price", 1.0)
    ml_config = campaign.get("ml_prediction", {})
    
    if not ml_config.get("enabled"):
        return {
            "campaign_id": campaign_id,
            "predicted_price": base_price,
            "adjustment_factor": 1.0,
            "ml_enabled": False
        }
    
    adjustments = []
    feature_weights = ml_config.get("feature_weights", {})
    
    if features.device_type:
        stats = await db.ml_model_stats.find_one(
            {"campaign_id": campaign_id, "feature_key": f"device_type:{features.device_type}"},
            {"_id": 0}
        )
        if stats and stats.get("total_bids", 0) >= 10:
            win_rate = stats.get("win_rate", 0.3)
            target_rate = ml_config.get("target_win_rate", 0.3)
            adjustment = 1.0 + (target_rate - win_rate) * feature_weights.get("device_type", 0.15)
            adjustments.append(adjustment)
    
    if features.geo_country:
        stats = await db.ml_model_stats.find_one(
            {"campaign_id": campaign_id, "feature_key": f"geo_country:{features.geo_country}"},
            {"_id": 0}
        )
        if stats and stats.get("total_bids", 0) >= 10:
            win_rate = stats.get("win_rate", 0.3)
            target_rate = ml_config.get("target_win_rate", 0.3)
            adjustment = 1.0 + (target_rate - win_rate) * feature_weights.get("geo_country", 0.15)
            adjustments.append(adjustment)
    
    if features.bid_floor and features.bid_floor > base_price * 0.9:
        adjustments.append(1.1)
    
    if adjustments:
        avg_adjustment = sum(adjustments) / len(adjustments)
        weight = ml_config.get("prediction_weight", 0.5)
        final_adjustment = 1.0 * (1 - weight) + avg_adjustment * weight
    else:
        final_adjustment = 1.0
    
    final_adjustment = max(0.5, min(1.5, final_adjustment))
    predicted_price = base_price * final_adjustment
    
    return {
        "campaign_id": campaign_id,
        "base_price": base_price,
        "predicted_price": round(predicted_price, 4),
        "adjustment_factor": round(final_adjustment, 4),
        "adjustments_applied": len(adjustments),
        "ml_enabled": True
    }


@router.get("/ml/models")
async def get_all_ml_models():
    """Get all ML model statuses"""
    campaigns = await db.campaigns.find(
        {},
        {"_id": 0, "id": 1, "name": 1, "ml_prediction": 1, "bids": 1, "wins": 1}
    ).to_list(1000)
    
    models = []
    for c in campaigns:
        ml_config = c.get("ml_prediction", {})
        stats = await db.ml_model_stats.find({"campaign_id": c["id"]}, {"_id": 0}).to_list(100)
        
        models.append({
            "campaign_id": c["id"],
            "campaign_name": c["name"],
            "enabled": ml_config.get("enabled", False),
            "feature_count": len(stats),
            "total_training_data": sum(s.get("total_bids", 0) for s in stats),
            "prediction_weight": ml_config.get("prediction_weight", 0.5),
            "target_win_rate": ml_config.get("target_win_rate", 0.3)
        })
    
    return {"models": models}


@router.get("/ml/model/{campaign_id}/details")
async def get_ml_model_details(campaign_id: str):
    """Get detailed ML model information"""
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    ml_config = campaign.get("ml_prediction", {})
    stats = await db.ml_model_stats.find({"campaign_id": campaign_id}, {"_id": 0}).to_list(100)
    
    feature_analysis = {
        "device_type": [],
        "geo_country": [],
        "os": []
    }
    
    for stat in stats:
        key = stat.get("feature_key", "")
        if key.startswith("device_type:"):
            feature_analysis["device_type"].append({
                "value": key.split(":")[1],
                "bids": stat.get("total_bids", 0),
                "wins": stat.get("total_wins", 0),
                "win_rate": round(stat.get("win_rate", 0) * 100, 2),
                "avg_bid_price": round(stat.get("avg_bid_price", 0), 2)
            })
        elif key.startswith("geo_country:"):
            feature_analysis["geo_country"].append({
                "value": key.split(":")[1],
                "bids": stat.get("total_bids", 0),
                "wins": stat.get("total_wins", 0),
                "win_rate": round(stat.get("win_rate", 0) * 100, 2),
                "avg_bid_price": round(stat.get("avg_bid_price", 0), 2)
            })
        elif key.startswith("os:"):
            feature_analysis["os"].append({
                "value": key.split(":")[1],
                "bids": stat.get("total_bids", 0),
                "wins": stat.get("total_wins", 0),
                "win_rate": round(stat.get("win_rate", 0) * 100, 2),
                "avg_bid_price": round(stat.get("avg_bid_price", 0), 2)
            })
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.get("name"),
        "config": {
            "enabled": ml_config.get("enabled", False),
            "prediction_weight": ml_config.get("prediction_weight", 0.5),
            "target_win_rate": ml_config.get("target_win_rate", 0.3),
            "feature_weights": ml_config.get("feature_weights", {})
        },
        "feature_analysis": feature_analysis,
        "total_features": len(stats)
    }


# ==================== BID OPTIMIZATION ====================

@router.get("/bid-optimization/status")
async def get_bid_optimization_status():
    """Get status of automated bid optimization for all campaigns"""
    campaigns = await db.campaigns.find({}, {"_id": 0}).to_list(1000)
    
    optimization_status = []
    for campaign in campaigns:
        opt_config = campaign.get("bid_optimization", {})
        
        optimization_status.append({
            "campaign_id": campaign["id"],
            "campaign_name": campaign["name"],
            "status": campaign.get("status"),
            "bid_price": campaign.get("bid_price", 0),
            "optimization_enabled": opt_config.get("enabled", False),
            "target_win_rate": opt_config.get("target_win_rate", 30),
            "current_win_rate": round((campaign.get("wins", 0) / max(campaign.get("bids", 1), 1)) * 100, 2),
            "auto_adjust": opt_config.get("auto_adjust", False),
            "last_adjustment": opt_config.get("last_adjustment"),
            "adjustment_history": opt_config.get("history", [])[-5:]
        })
    
    return {
        "total_campaigns": len(campaigns),
        "optimization_enabled_count": len([c for c in optimization_status if c["optimization_enabled"]]),
        "campaigns": optimization_status
    }


@router.post("/bid-optimization/{campaign_id}/enable")
async def enable_bid_optimization(campaign_id: str, target_win_rate: float = 30.0, auto_adjust: bool = True):
    """Enable automated bid optimization for a campaign"""
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    opt_config = {
        "enabled": True,
        "target_win_rate": target_win_rate,
        "auto_adjust": auto_adjust,
        "min_bid_price": campaign.get("bid_price", 1.0) * 0.5,
        "max_bid_price": campaign.get("bid_price", 1.0) * 2.0,
        "adjustment_step": 0.05,
        "evaluation_window_hours": 24,
        "min_bids_for_adjustment": 100,
        "history": [],
        "last_adjustment": None
    }
    
    await db.campaigns.update_one(
        {"id": campaign_id},
        {"$set": {"bid_optimization": opt_config}}
    )
    
    return {"status": "enabled", "config": opt_config}


@router.post("/bid-optimization/{campaign_id}/disable")
async def disable_bid_optimization(campaign_id: str):
    """Disable automated bid optimization for a campaign"""
    result = await db.campaigns.update_one(
        {"id": campaign_id},
        {"$set": {"bid_optimization.enabled": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {"status": "disabled"}


@router.post("/bid-optimization/{campaign_id}/run")
async def run_bid_optimization(campaign_id: str):
    """Manually trigger bid optimization for a campaign"""
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    opt_config = campaign.get("bid_optimization", {})
    if not opt_config.get("enabled"):
        raise HTTPException(status_code=400, detail="Bid optimization not enabled for this campaign")
    
    current_bid = campaign.get("bid_price", 1.0)
    bids = campaign.get("bids", 0)
    wins = campaign.get("wins", 0)
    current_win_rate = (wins / bids * 100) if bids > 0 else 0
    target_win_rate = opt_config.get("target_win_rate", 30)
    
    if bids < opt_config.get("min_bids_for_adjustment", 100):
        return {
            "status": "skipped",
            "reason": f"Not enough bids ({bids}) for adjustment. Need at least {opt_config.get('min_bids_for_adjustment', 100)}",
            "current_bid": current_bid,
            "current_win_rate": round(current_win_rate, 2)
        }
    
    adjustment_step = opt_config.get("adjustment_step", 0.05)
    min_bid = opt_config.get("min_bid_price", current_bid * 0.5)
    max_bid = opt_config.get("max_bid_price", current_bid * 2.0)
    
    new_bid = current_bid
    adjustment_reason = ""
    
    if current_win_rate < target_win_rate - 5:
        new_bid = min(current_bid * (1 + adjustment_step), max_bid)
        adjustment_reason = f"Win rate ({current_win_rate:.1f}%) below target ({target_win_rate}%), increasing bid"
    elif current_win_rate > target_win_rate + 10:
        new_bid = max(current_bid * (1 - adjustment_step), min_bid)
        adjustment_reason = f"Win rate ({current_win_rate:.1f}%) above target ({target_win_rate}%), decreasing bid to optimize cost"
    else:
        return {
            "status": "no_change",
            "reason": f"Win rate ({current_win_rate:.1f}%) within acceptable range of target ({target_win_rate}%)",
            "current_bid": current_bid,
            "current_win_rate": round(current_win_rate, 2)
        }
    
    adjustment_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "old_bid": current_bid,
        "new_bid": round(new_bid, 4),
        "win_rate_at_change": round(current_win_rate, 2),
        "target_win_rate": target_win_rate,
        "reason": adjustment_reason
    }
    
    if opt_config.get("auto_adjust"):
        await db.campaigns.update_one(
            {"id": campaign_id},
            {
                "$set": {
                    "bid_price": round(new_bid, 4),
                    "bid_optimization.last_adjustment": datetime.now(timezone.utc).isoformat()
                },
                "$push": {"bid_optimization.history": adjustment_record}
            }
        )
        
        return {
            "status": "adjusted",
            "old_bid": current_bid,
            "new_bid": round(new_bid, 4),
            "adjustment_percent": round((new_bid - current_bid) / current_bid * 100, 2),
            "reason": adjustment_reason,
            "current_win_rate": round(current_win_rate, 2),
            "target_win_rate": target_win_rate
        }
    else:
        return {
            "status": "recommendation",
            "current_bid": current_bid,
            "recommended_bid": round(new_bid, 4),
            "reason": adjustment_reason,
            "note": "Auto-adjust is disabled. Enable to apply automatically."
        }


@router.get("/bid-optimization/{campaign_id}/history")
async def get_optimization_history(campaign_id: str):
    """Get bid optimization history for a campaign"""
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    opt_config = campaign.get("bid_optimization", {})
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.get("name"),
        "current_bid": campaign.get("bid_price"),
        "optimization_enabled": opt_config.get("enabled", False),
        "target_win_rate": opt_config.get("target_win_rate"),
        "history": opt_config.get("history", [])
    }


# ==================== SPO (Supply Path Optimization) ====================

@router.get("/spo/analyze/{campaign_id}")
async def analyze_supply_paths(campaign_id: str):
    """Analyze supply paths for a campaign"""
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    logs = await db.bid_logs.find(
        {"campaign_id": campaign_id, "bid_made": True},
        {"_id": 0, "request_summary": 1, "win_notified": 1, "win_price": 1, "shaded_price": 1, "bid_price": 1}
    ).to_list(5000)
    
    path_stats = {}
    
    for log in logs:
        summary = log.get("request_summary", {})
        path_key = summary.get("bundle") or summary.get("domain") or "unknown"
        
        if path_key not in path_stats:
            path_stats[path_key] = {
                "bids": 0,
                "wins": 0,
                "total_bid_price": 0,
                "total_win_price": 0
            }
        
        path_stats[path_key]["bids"] += 1
        path_stats[path_key]["total_bid_price"] += log.get("shaded_price") or log.get("bid_price", 0)
        
        if log.get("win_notified"):
            path_stats[path_key]["wins"] += 1
            path_stats[path_key]["total_win_price"] += log.get("win_price", 0)
    
    paths = []
    for path_key, stats in path_stats.items():
        win_rate = stats["wins"] / stats["bids"] if stats["bids"] > 0 else 0
        avg_bid = stats["total_bid_price"] / stats["bids"] if stats["bids"] > 0 else 0
        avg_win = stats["total_win_price"] / stats["wins"] if stats["wins"] > 0 else 0
        efficiency = win_rate / avg_bid if avg_bid > 0 else 0
        
        paths.append({
            "path": path_key,
            "bids": stats["bids"],
            "wins": stats["wins"],
            "win_rate": round(win_rate * 100, 2),
            "avg_bid_price": round(avg_bid, 2),
            "avg_win_price": round(avg_win, 2),
            "efficiency_score": round(efficiency * 100, 2)
        })
    
    paths.sort(key=lambda x: x["efficiency_score"], reverse=True)
    
    spo_config = campaign.get("spo", {})
    
    return {
        "campaign_id": campaign_id,
        "spo_enabled": spo_config.get("enabled", False),
        "total_paths_analyzed": len(paths),
        "recommended_paths": paths[:10],
        "underperforming_paths": [p for p in paths if p["win_rate"] < 10][-10:],
        "paths": paths
    }
