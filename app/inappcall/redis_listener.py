"""Redis listener for in-app call events."""

import asyncio
import json
import logging

import redis.asyncio as redis

from app.inappcall.websocket_manager import ws_manager

logger = logging.getLogger(__name__)


async def start_call_listener(redis_client: redis.Redis) -> None:
    """Forward in-app call events to connected call WebSocket clients."""
    pubsub = redis_client.pubsub()

    try:
        await pubsub.subscribe("inapp_calls")
        logger.info("Redis listener subscribed to 'inapp_calls' channel")

        while True:
            try:
                message = await pubsub.get_message(ignore_subscribe_messages=True)

                if message:
                    payload = json.loads(message["data"])
                    user_id = payload.get("user_id")

                    if user_id is not None:
                        await ws_manager.send_to_user(int(user_id), payload)

                await asyncio.sleep(0.01)

            except asyncio.CancelledError:
                logger.info("Redis call listener cancelled")
                break

            except Exception as exc:
                logger.error(f"Call listener error: {exc}")
                await asyncio.sleep(0.1)

    finally:
        try:
            await pubsub.unsubscribe("inapp_calls")
            await pubsub.close()
            logger.info("Redis call listener closed cleanly")
        except Exception as exc:
            logger.debug(f"Redis pubsub cleanup error: {exc}")
