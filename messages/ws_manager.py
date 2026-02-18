import time
import uuid
from typing import Dict, Optional

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_users: Dict[uuid.UUID, Dict] = {}
        self._typing_last_sent: Dict[tuple[uuid.UUID, uuid.UUID], float] = {}

    async def connect(self, user_id: uuid.UUID, websocket: WebSocket):
        old = self.active_users.get(user_id)
        if old:
            try:
                await old["socket"].close(code=1000)
            except Exception:
                pass

        self.active_users[user_id] = {"socket": websocket, "subscriptions": set()}

    def disconnect(self, user_id: uuid.UUID):
        if user_id in self.active_users:
            del self.active_users[user_id]

    def subscribe(self, user_id: uuid.UUID, chat_id: uuid.UUID):
        if user_id in self.active_users:
            self.active_users[user_id]["subscriptions"].add(chat_id)

    def unsubscribe(self, user_id: uuid.UUID, chat_id: uuid.UUID):
        if user_id in self.active_users:
            self.active_users[user_id]["subscriptions"].discard(chat_id)

    def subscribe_many(self, user_id: uuid.UUID, chat_ids: list[uuid.UUID]):
        if user_id not in self.active_users:
            return
        self.active_users[user_id]["subscriptions"].update(chat_ids)

    def get_user_subscriptions(self, user_id: uuid.UUID) -> set[uuid.UUID]:
        data = self.active_users.get(user_id)
        if not data:
            return set()
        return set(data["subscriptions"])

    def get_online_user_ids_in_chat(self, chat_id: uuid.UUID) -> list[str]:
        online = []
        for uid, data in self.active_users.items():
            if chat_id in data["subscriptions"]:
                online.append(str(uid))
        return online

    def typing_allowed(
        self, user_id: uuid.UUID, chat_id: uuid.UUID, min_interval_sec: float = 1.0
    ) -> bool:
        key = (user_id, chat_id)
        now = time.time()
        last = self._typing_last_sent.get(key, 0.0)
        if now - last < min_interval_sec:
            return False
        self._typing_last_sent[key] = now
        return True

    async def send_to_user(self, user_id: uuid.UUID, message: dict):
        data = self.active_users.get(user_id)
        if not data:
            return
        try:
            await data["socket"].send_json(message)
        except Exception:
            self.disconnect(user_id)

    async def broadcast(
        self,
        chat_id: uuid.UUID,
        message: dict,
        exclude_user_id: Optional[uuid.UUID] = None,
    ):
        dead = []
        for user_id, data in self.active_users.items():
            if exclude_user_id and user_id == exclude_user_id:
                continue
            if chat_id in data["subscriptions"]:
                try:
                    await data["socket"].send_json(message)
                except Exception:
                    dead.append(user_id)

        for user_id in dead:
            self.disconnect(user_id)
