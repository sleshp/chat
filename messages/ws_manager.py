import uuid
from typing import Dict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_users: Dict[uuid.UUID, Dict] = {}

    async def connect(self, user_id: uuid.UUID, websocket: WebSocket):
        self.active_users[user_id] = {
            "socket": websocket,
            "subscriptions": set()
        }

    def disconnect(self, user_id: uuid.UUID):
        if user_id in self.active_users:
            del self.active_users[user_id]

    def subscribe(self, user_id: uuid.UUID, chat_id: uuid.UUID):
        if user_id in self.active_users:
            self.active_users[user_id]["subscriptions"].add(chat_id)

    def unsubscribe(self, user_id: uuid.UUID, chat_id: uuid.UUID):
        if user_id in self.active_users:
            self.active_users[user_id]["subscriptions"].discard(chat_id)

    async def broadcast(self, chat_id: uuid.UUID, message: dict):
        for user_id, data in self.active_users.items():
            if chat_id in data["subscriptions"]:
                await data["socket"].send_json(message)
