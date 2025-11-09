"""
WebSocket routes for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict
import json
import asyncio
from backend.auth.jwt import decode_token
from backend.models.database import get_db
from backend.models.user import User
from sqlalchemy.orm import Session

router = APIRouter()


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a WebSocket"""
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a WebSocket"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id in self.user_connections and websocket in self.user_connections[user_id]:
            self.user_connections[user_id].remove(websocket)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to a specific connection"""
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connections"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass
    
    async def send_to_user(self, message: dict, user_id: int):
        """Send message to all connections of a user"""
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass


manager = ConnectionManager()


async def get_user_from_token(token: str, db: Session) -> User:
    """Get user from JWT token"""
    payload = decode_token(token)
    if not payload:
        raise ValueError("Invalid token")
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise ValueError("User not found or inactive")
    
    return user


@router.websocket("/alerts")
async def websocket_alerts(websocket: WebSocket, token: str = None):
    """WebSocket endpoint for real-time alerts"""
    user = None
    user_id = None
    
    try:
        # Authenticate
        if not token:
            await websocket.close(code=1008, reason="Authentication required")
            return
        
        # Get user from token
        from backend.models.database import SessionLocal
        db = SessionLocal()
        try:
            user = await get_user_from_token(token, db)
            user_id = user.id
        except Exception as e:
            await websocket.close(code=1008, reason=f"Authentication failed: {str(e)}")
            return
        finally:
            db.close()
        
        # Connect
        await manager.connect(websocket, user_id)
        
        # Send welcome message
        await manager.send_personal_message({
            "type": "connected",
            "message": "Connected to SentinelVNC alert stream",
            "user_id": user_id
        }, websocket)
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for ping or message
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await manager.send_personal_message({"type": "pong"}, websocket)
                
            except asyncio.TimeoutError:
                # Send keepalive
                await manager.send_personal_message({"type": "keepalive"}, websocket)
            except WebSocketDisconnect:
                break
            except Exception as e:
                await manager.send_personal_message({
                    "type": "error",
                    "message": str(e)
                }, websocket)
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close(code=1011, reason=f"Server error: {str(e)}")
    finally:
        if user_id:
            manager.disconnect(websocket, user_id)


# Function to broadcast alerts (called from detection service)
async def broadcast_alert(alert_data: dict):
    """Broadcast alert to all connected clients"""
    await manager.broadcast({
        "type": "alert",
        "data": alert_data
    })

