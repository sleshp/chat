import uvicorn
from fastapi import FastAPI

from users.api import user_router
from chats.api import chat_router
from messages.api import messages_router
app = FastAPI()

app.include_router(user_router)
app.include_router(chat_router)
app.include_router(messages_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
