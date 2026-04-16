"""
Shared utilities, database connection, and common dependencies for routers
"""
from fastapi import Header, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict, Any, Set
from pathlib import Path
import os
import logging
import json
import asyncio
from dotenv import load_dotenv
from fastapi import WebSocket

# Load .env from backend directory
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection - handle quoted values from .env
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017').strip('"')
db_name = os.environ.get('DB_NAME', 'test_database').strip('"')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== WEBSOCKET CONNECTION MANAGER ====================

class ConnectionManager:
    """Manages WebSocket connections for real-time bid stream"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        try:
            message_json = json.dumps(message)
        except Exception as e:
            logger.error(f"Failed to serialize message: {e}")
            return
            
        disconnected = set()
        
        for connection in self.active_connections.copy():  # Use copy to avoid modification during iteration
            try:
                await asyncio.wait_for(connection.send_text(message_json), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("WebSocket send timed out")
                disconnected.add(connection)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)

ws_manager = ConnectionManager()


# ==================== DATABASE INDEXES ====================

async def ensure_indexes():
    """Create indexes for better query performance"""
    try:
        # Bid logs indexes - critical for fast queries
        await db.bid_logs.create_index([("timestamp", -1)])  # Sort by newest
        await db.bid_logs.create_index([("bid_made", 1), ("timestamp", -1)])  # Filter + sort
        await db.bid_logs.create_index([("ssp_id", 1), ("timestamp", -1)])
        await db.bid_logs.create_index([("campaign_id", 1), ("timestamp", -1)])
        
        # Campaigns indexes
        await db.campaigns.create_index([("status", 1)])
        await db.campaigns.create_index([("id", 1)], unique=True)
        
        # Creatives indexes
        await db.creatives.create_index([("id", 1)], unique=True)
        
        logger.info("Database indexes created/verified")
    except Exception as e:
        logger.warning(f"Index creation warning (may already exist): {e}")


# ==================== AUTH HELPERS ====================

async def verify_api_key(x_api_key: str = Header(None)) -> Optional[Dict[str, Any]]:
    """Verify SSP API key and return endpoint info"""
    if not x_api_key:
        return None
    
    endpoint = await db.ssp_endpoints.find_one(
        {"api_key": x_api_key, "status": "active"},
        {"_id": 0}
    )
    return endpoint


async def require_api_key(x_api_key: str = Header(...)) -> Dict[str, Any]:
    """Require valid SSP API key"""
    endpoint = await verify_api_key(x_api_key)
    if not endpoint:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return endpoint
