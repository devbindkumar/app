"""
Redis Cache Manager for Distributed Caching
Supports multiple workers with shared cache state
"""
import os
import json
import logging
from typing import Optional, Any, List, Dict
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Load .env file if not already loaded
def _load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key not in os.environ:
                        os.environ[key] = value

_load_env()

# Redis connection (lazy initialization)
_redis_client = None
_redis_available = None

# Default TTLs
CAMPAIGNS_CACHE_TTL = 10  # 10 seconds for campaigns
BID_STATS_TTL = 3600  # 1 hour for bid stats (persisted)
RECENT_BIDS_TTL = 300  # 5 minutes for recent bids list

# Cache keys
CAMPAIGNS_CACHE_KEY = "dsp:campaigns:active"
BID_STATS_KEY = "dsp:stats:bids"
RECENT_BIDS_KEY = "dsp:bids:recent"


def get_redis_client():
    """Get or create Redis client with lazy initialization"""
    global _redis_client, _redis_available
    
    if _redis_available is False:
        return None
    
    if _redis_client is not None:
        return _redis_client
    
    try:
        import redis
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = redis.from_url(redis_url, decode_responses=True)
        # Test connection
        _redis_client.ping()
        _redis_available = True
        logger.info(f"Redis connected: {redis_url}")
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis not available, using in-memory fallback: {e}")
        _redis_available = False
        return None


def is_redis_available() -> bool:
    """Check if Redis is available"""
    return get_redis_client() is not None


# ==================== CAMPAIGNS CACHE ====================

def get_cached_campaigns() -> Optional[List[Dict]]:
    """Get campaigns from Redis cache"""
    client = get_redis_client()
    if not client:
        return None
    
    try:
        data = client.get(CAMPAIGNS_CACHE_KEY)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logger.warning(f"Redis get campaigns failed: {e}")
        return None


def set_cached_campaigns(campaigns: List[Dict], ttl: int = CAMPAIGNS_CACHE_TTL):
    """Set campaigns in Redis cache"""
    client = get_redis_client()
    if not client:
        return False
    
    try:
        client.setex(CAMPAIGNS_CACHE_KEY, ttl, json.dumps(campaigns))
        return True
    except Exception as e:
        logger.warning(f"Redis set campaigns failed: {e}")
        return False


def invalidate_campaigns_cache():
    """Invalidate campaigns cache"""
    client = get_redis_client()
    if client:
        try:
            client.delete(CAMPAIGNS_CACHE_KEY)
            logger.info("Redis campaigns cache invalidated")
        except Exception as e:
            logger.warning(f"Redis invalidate failed: {e}")


# ==================== BID STATS ====================

def get_bid_stats() -> Dict[str, int]:
    """Get bid stats from Redis"""
    client = get_redis_client()
    default_stats = {"total_requests": 0, "total_bids": 0, "total_no_bids": 0}
    
    if not client:
        return default_stats
    
    try:
        data = client.hgetall(BID_STATS_KEY)
        if data:
            return {
                "total_requests": int(data.get("total_requests", 0)),
                "total_bids": int(data.get("total_bids", 0)),
                "total_no_bids": int(data.get("total_no_bids", 0))
            }
        return default_stats
    except Exception as e:
        logger.warning(f"Redis get stats failed: {e}")
        return default_stats


def increment_bid_stats(bid_made: bool):
    """Increment bid stats atomically in Redis"""
    client = get_redis_client()
    if not client:
        return False
    
    try:
        pipe = client.pipeline()
        pipe.hincrby(BID_STATS_KEY, "total_requests", 1)
        if bid_made:
            pipe.hincrby(BID_STATS_KEY, "total_bids", 1)
        else:
            pipe.hincrby(BID_STATS_KEY, "total_no_bids", 1)
        pipe.execute()
        return True
    except Exception as e:
        logger.warning(f"Redis increment stats failed: {e}")
        return False


# ==================== RECENT BIDS ====================

def add_recent_bid(bid_entry: Dict, max_bids: int = 100):
    """Add a bid to the recent bids list in Redis"""
    client = get_redis_client()
    if not client:
        return False
    
    try:
        # Use a sorted set with timestamp as score for ordering
        score = datetime.now(timezone.utc).timestamp()
        client.zadd(RECENT_BIDS_KEY, {json.dumps(bid_entry): score})
        # Trim to keep only the most recent bids
        client.zremrangebyrank(RECENT_BIDS_KEY, 0, -max_bids - 1)
        # Set expiry
        client.expire(RECENT_BIDS_KEY, RECENT_BIDS_TTL)
        return True
    except Exception as e:
        logger.warning(f"Redis add recent bid failed: {e}")
        return False


def get_recent_bids(limit: int = 50) -> List[Dict]:
    """Get recent bids from Redis"""
    client = get_redis_client()
    if not client:
        return []
    
    try:
        # Get most recent bids (highest scores = most recent)
        data = client.zrevrange(RECENT_BIDS_KEY, 0, limit - 1)
        return [json.loads(item) for item in data]
    except Exception as e:
        logger.warning(f"Redis get recent bids failed: {e}")
        return []


# ==================== FREQUENCY CAPPING ====================

def get_user_frequency(user_id: str, campaign_id: str) -> int:
    """Get user frequency count from Redis"""
    client = get_redis_client()
    if not client:
        return 0
    
    try:
        key = f"dsp:freq:{campaign_id}:{user_id}"
        count = client.get(key)
        return int(count) if count else 0
    except Exception as e:
        logger.warning(f"Redis get frequency failed: {e}")
        return 0


def increment_user_frequency(user_id: str, campaign_id: str, ttl_hours: int = 24) -> int:
    """Increment user frequency count in Redis"""
    client = get_redis_client()
    if not client:
        return 0
    
    try:
        key = f"dsp:freq:{campaign_id}:{user_id}"
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, ttl_hours * 3600)
        results = pipe.execute()
        return results[0]  # New count after increment
    except Exception as e:
        logger.warning(f"Redis increment frequency failed: {e}")
        return 0


# ==================== HEALTH CHECK ====================

def redis_health_check() -> Dict[str, Any]:
    """Check Redis health and return stats"""
    client = get_redis_client()
    if not client:
        return {"available": False, "message": "Redis not configured"}
    
    try:
        info = client.info("memory")
        return {
            "available": True,
            "used_memory": info.get("used_memory_human"),
            "connected_clients": client.info("clients").get("connected_clients"),
            "campaigns_cached": client.exists(CAMPAIGNS_CACHE_KEY),
            "recent_bids_count": client.zcard(RECENT_BIDS_KEY)
        }
    except Exception as e:
        return {"available": False, "error": str(e)}
