from app_init import socketio
from app import app
import asyncio

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(socketio.run(app))
