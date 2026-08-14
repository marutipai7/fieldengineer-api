<<<<<<< HEAD
=======
"""
Redis Notification Listener

Background task that subscribes to the notifications Redis channel
and routes messages to connected WebSocket clients.

Runs once per FastAPI instance.
"""

>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
import asyncio
import json
import logging

import redis.asyncio as redis

from app.notifications.websocket_manager import ws_manager

logger = logging.getLogger(__name__)


<<<<<<< HEAD
async def start_notification_listener(
    redis_client: redis.Redis,
) -> None:
    """
    Listen for notification events from Redis
    and send them to the user's WebSocket connections.
    """

=======
async def start_notification_listener(redis_client: redis.Redis) -> None:
    """Listen for notification events from Redis and forward them to active WebSocket clients."""
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
    pubsub = redis_client.pubsub()

    try:
        await pubsub.subscribe("notifications")
<<<<<<< HEAD

        logger.info(
            "Redis listener subscribed to 'notifications' channel"
        )

        while True:
            try:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True
                )

                if message:
                    payload = json.loads(message["data"])

                    user_id = payload.get("user_id")

                    if user_id:
                        await ws_manager.send_to_user(
                            int(user_id),
                            payload,
                        )
=======
        logger.info("Redis listener subscribed to 'notifications' channel")

        while True:
            try:
                message = await pubsub.get_message(ignore_subscribe_messages=True)

                if message:
                    payload = json.loads(message["data"])
                    user_id = payload.get("user_id")

                    if user_id is not None:
                        await ws_manager.send_to_user(int(user_id), payload)
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6

                await asyncio.sleep(0.01)

            except asyncio.CancelledError:
<<<<<<< HEAD
                logger.info(
                    "Redis notification listener cancelled"
                )
                break

            except Exception as exc:
                logger.error(
                    f"Notification listener error: {exc}"
                )

=======
                logger.info("Redis notification listener cancelled")
                break

            except Exception as exc:
                logger.error(f"Notification listener error: {exc}")
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
                await asyncio.sleep(0.1)

    finally:
        try:
            await pubsub.unsubscribe("notifications")
            await pubsub.close()
<<<<<<< HEAD

            logger.info(
                "Redis notification listener closed"
            )

        except Exception as exc:
            logger.debug(
                f"Redis pubsub cleanup error: {exc}"
            )
=======
            logger.info("Redis notification listener closed cleanly")
        except Exception as exc:
            logger.debug(f"Redis pubsub cleanup error: {exc}")
>>>>>>> 7425a69e89a67de1c0f662f4ee4c5927fff75ee6
