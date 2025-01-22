import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import uvicorn

from message_handler import MessageHandler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await handler.bot.setup()
    yield
    # Shutdown
    # Add any cleanup here if needed
    pass

app = FastAPI(lifespan=lifespan)


handler = MessageHandler()

@app.post("/message")
async def send_message(message: dict):
    """
    Receives a new message from the user
    """
    await handler.handle_message(message)
    return {"status": "sent"}

@app.get("/messages")
async def get_messages():
    """
    Returns unread messages
    """
    async def message_generator():
        async for message in handler.get_messages_for_user():
            yield json.dumps({"messages": message}) + "\n"
            
    return StreamingResponse(message_generator(), media_type="application/json")


if __name__ == "__main__":
    config = uvicorn.Config(app, host="localhost", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    asyncio.run(server.serve())