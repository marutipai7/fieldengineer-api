#!/usr/bin/env python3
"""
Test WebSocket connection
"""

import asyncio
import json
import jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal, get_redis
from app.profile.models import User
from datetime import datetime

async def test_websocket():
    """Test WebSocket connection"""
    try:
        # Create a test user if it doesn't exist
        db: Session = SessionLocal()
        try:
            test_email = "websocket_test@example.com"
            user = db.query(User).filter(User.email == test_email).first()
            
            if not user:
                print("📝 Creating test user...")
                user = User(
                    email=test_email,
                    phone_number="+1234567890",
                    first_name="Test",
                    last_name="User",
                    password_hash="test_hash",  # This won't be used
                    created_at=datetime.utcnow(),
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"✅ Test user created with ID: {user.id}")
            else:
                print(f"✅ Using existing test user: {user.email}")
        
        finally:
            db.close()
        
        # Create a test token for the user
        payload = {
            "sub": test_email,
        }
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        
        print(f"✅ Generated token: {token[:50]}...")
        
        # Try to connect to WebSocket
        import websockets
        
        uri = f"ws://127.0.0.1:8000/notifications/ws?token={token}"
        print(f"🔗 Connecting to: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected!")
            
            # Send ping
            await websocket.send("ping")
            print("📤 Sent: ping")
            
            # Receive pong
            response = await websocket.recv()
            print(f"📥 Received: {response}")
            
            if response == "pong":
                print("✅ WebSocket working correctly!")
                return True
            else:
                print(f"❌ Unexpected response: {response}")
                return False
                
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket())
    exit(0 if result else 1)
