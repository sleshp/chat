import uuid

import jwt
from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket, WebSocketDisconnect

from chats.services import ChatService
from config import get_auth_data
from dependencies import get_session
from messages.schemas import MessageCreateSchema, MessageReadSchema
from messages.services import MessageService
from messages.ws_manager import ConnectionManager

ws_router = APIRouter(tags=['websockets'])
manager = ConnectionManager()


@ws_router.websocket('/ws')
async def websocket_endpoint(websocket:WebSocket, session: AsyncSession = Depends(get_session)):
    await websocket.accept()
    try:
        auth_data = await websocket.receive_json()
        if auth_data.get("action") != "auth":
            await websocket.close(code=1008)
            return
        token = auth_data.get("token")
        token_data = get_auth_data()
        payload = jwt.decode(token, token_data['secret_key'], algorithms=[token_data['algorithm']])
        user_id = uuid.UUID(payload.get('sub'))
    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
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

                message_create = MessageCreateSchema(chat_id=chat_id, text=text, client_msg_id=client_msg_id)
                message = await MessageService.create_message(session, message_create, user_id)

                await manager.broadcast(chat_id, MessageReadSchema.model_validate(message).model_dump(mode="json"))
            elif action == "read_messages":
                message_ids = [uuid.UUID(mid) for mid in data.get("message_ids", [])]
                messages = await MessageService.mark_as_read(session, message_ids, user_id)
                for msg in messages:
                    await ChatService.ensure_member(session, msg.chat_id, user_id)
                    await manager.broadcast(
                        msg.chat_id,
                        MessageReadSchema.model_validate(msg).model_dump(mode="json")
                    )

    except WebSocketDisconnect:
        manager.disconnect(user_id)
