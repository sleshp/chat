import uuid

from fastapi import APIRouter, Depends, Query
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket, WebSocketDisconnect

from chats.services import ChatService
from config import get_auth_data
from database import async_session
from dependencies import get_session
from messages.schemas import MessageCreateSchema, MessageReadSchema
from messages.services import MessageService
from messages.ws_manager import ConnectionManager

ws_router = APIRouter(tags=["websockets"])
manager = ConnectionManager()


@ws_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
):
    await websocket.accept()
    try:
        auth_data = await websocket.receive_json()
        if auth_data.get("action") != "auth":
            await websocket.close(code=1008)
            return
        token = auth_data.get("token")
        if not token:
            await websocket.close(code=1008)
            return
        token_data = get_auth_data()
        payload = jwt.decode(
            token, token_data["secret_key"], algorithms=[token_data["algorithm"]]
        )
        user_id = uuid.UUID(payload.get("sub"))
    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(user_id, websocket)

    async with async_session() as session:
        chat_ids = await ChatService.list_user_chat_ids(session, user_id)

    manager.subscribe_many(user_id, chat_ids)

    await manager.send_to_user(
        user_id,
        {
            "type": "presence.snapshot_all",
            "online_by_chat": {
                str(cid): manager.get_online_user_ids_in_chat(cid) for cid in chat_ids
            },
        },
    )

    for cid in chat_ids:
        await manager.broadcast(
            cid,
            {
                "type": "presence.update",
                "chat_id": str(cid),
                "user_id": str(user_id),
                "status": "online",
            },
            exclude_user_id=user_id,
        )

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            async with async_session() as session:
                if action == "subscribe":
                    chat_id = uuid.UUID(data.get("chat_id"))
                    await ChatService.ensure_member(session, chat_id, user_id)
                    manager.subscribe(user_id, chat_id)

                elif action == "unsubscribe":
                    chat_id = uuid.UUID(data.get("chat_id"))
                    await ChatService.ensure_member(session, chat_id, user_id)
                    manager.unsubscribe(user_id, chat_id)

                elif action == "send_message":
                    chat_id = uuid.UUID(data.get("chat_id"))
                    await ChatService.ensure_member(session, chat_id, user_id)
                    text = data.get("text")
                    client_msg_id = uuid.UUID(data.get("client_msg_id"))

                    message_create = MessageCreateSchema(
                        chat_id=chat_id, text=text, client_msg_id=client_msg_id
                    )
                    message = await MessageService.create_message(
                        session, message_create, user_id
                    )
                    await session.commit()

                    await manager.broadcast(
                        chat_id,
                        MessageReadSchema.model_validate(message).model_dump(
                            mode="json"
                        ),
                    )

                elif action == "typing":
                    chat_id = uuid.UUID(data.get("chat_id"))
                    is_typing = bool(data.get("is_typing", True))

                    await ChatService.ensure_member(session, chat_id, user_id)

                    if not manager.typing_allowed(
                        user_id, chat_id, min_interval_sec=1.0
                    ):
                        continue

                    await manager.broadcast(
                        chat_id,
                        {
                            "type": "typing",
                            "chat_id": str(chat_id),
                            "user_id": str(user_id),
                            "is_typing": is_typing,
                        },
                        exclude_user_id=user_id,
                    )

                elif action == "read_messages":
                    message_ids = [
                        uuid.UUID(mid) for mid in data.get("message_ids", [])
                    ]
                    messages = await MessageService.mark_as_read(
                        session, message_ids, user_id
                    )
                    await session.commit()

                    for msg in messages:
                        await manager.broadcast(
                            msg.chat_id,
                            MessageReadSchema.model_validate(msg).model_dump(
                                mode="json"
                            ),
                        )
                else:
                    pass

    except WebSocketDisconnect:
        subs = manager.get_user_subscriptions(user_id)
        for cid in subs:
            await manager.broadcast(
                cid,
                {
                    "type": "presence.update",
                    "chat_id": str(cid),
                    "user_id": str(user_id),
                    "status": "offline",
                },
                exclude_user_id=user_id,
            )
        manager.disconnect(user_id)
