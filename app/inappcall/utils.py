from app.inappcall.firebase import send_push_notification


def send_incoming_call_notification(
    *,
    db,
    call,
) -> bool:
    """Send the push shown when a user receives an in-app call."""
    return send_push_notification(
        db=db,
        user_id=call.receiver_id,
        title="Incoming Call",
        body=f"You have an incoming {call.call_type.value} call",
        data={
            "notification_type": "incoming_call",
            "entity_type": "call",
            "entity_id": call.id,
            "call_id": call.id,
            "room_id": call.room_id,
            "join_url": call.join_url,
            "caller_id": call.caller_id,
        },
    )
