import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
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
    try:
        # Try to get messages for up to 30 seconds
        for _ in range(30):  # 30 seconds max
            # Get one message from the generator
            async for message in handler.get_messages_for_user():
                return JSONResponse({"messages": message})
                
            # No message yet, sleep a bit
            await asyncio.sleep(0.1)
        
        # If no message after polling, return empty
        return JSONResponse({"messages": None})
            
    except Exception as e:
        print(f"Error reading from queue: {e}")
        return JSONResponse({"messages": None})



if __name__ == "__main__":
    config = uvicorn.Config(app, host="localhost", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    asyncio.run(server.serve())