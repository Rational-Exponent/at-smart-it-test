import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from message_handler import MessageHandler

from logging import getLogger, INFO
logger = getLogger(__name__)
logger.setLevel(INFO)


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
    await handler.handle_received_message(message)
    return {"status": "sent"}

@app.get("/messages")
async def get_messages():
    try:
        # return JSONResponse({"messages": ["Hello, user"]})
        
        # Create the async generator once
        message_generator = handler.get_messages_for_user()
        
        # Try to get one message for up to 30 seconds
        for _ in range(300):
            try:
                # Try to get the next message with a timeout
                message = await anext(message_generator, None)
                logger.info(f">> app-api /messages\n{message}")
                if message is not None:
                    return JSONResponse({"messages": [message]})
                
                # No message yet, sleep a bit
                await asyncio.sleep(0.1)
                
            except StopAsyncIteration:
                break
            
        # If no message after polling, return empty
        return JSONResponse({"messages": None})
            
    except Exception as e:
        print(f"Error reading from queue: {e}")
        return JSONResponse({"messages": None})



if __name__ == "__main__":
    config = uvicorn.Config(app, host="localhost", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    asyncio.run(server.serve())