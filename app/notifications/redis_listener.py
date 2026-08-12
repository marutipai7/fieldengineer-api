"""
Redis Notification Listener

Background task that subscribes to the notifications Redis channel
and routes messages to connected WebSocket clients.

Runs once per FastAPI instance.
"""

import asyncio
import logging
import json
import redis.asyncio as redis

from app.notifications.websocket_manager import ws_manager

logger = logging.getLogger(__name__)


async def start_notification_listener(redis_client: redis.Redis) -> None:
    pubsub = redis_client.pubsub()

    try:
        await pubsub.subscribe("notifications")
        logger.info("✓ Redis listener subscribed to 'notifications' channel")

        while True:
            try:
                message = await pubsub.get_message(ignore_subscribe_messages=True)

                if message:
                    payload = json.loads(message["data"])

                    if user_id := payload.get("user_id"):
                        await ws_manager.send_to_user(user_id, payload)

                await asyncio.sleep(0.01)

            except asyncio.CancelledError:
                logger.info("🛑 Redis listener cancelled")
                break

            except Exception as exc:
                logger.error(f"Listener error: {exc}")
                await asyncio.sleep(0.1)

    finally:
        try:
            await pubsub.unsubscribe("notifications")
            await pubsub.close()
            logger.info("✓ Redis listener closed cleanly")
        except Exception as exc:
            logger.debug(f"Pubsub cleanup error: {exc}")