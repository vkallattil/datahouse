import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO, emit
from agents.core import DatahouseAgent
import asyncio

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
datahouse_agent = DatahouseAgent()

# This ensures proper event loop handling with eventlet

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

async def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return await coro
    finally:
        loop.close()

@socketio.on('message')
def handle_message(message):
    if message.get("type") == "chat":
        print('Received message:', message["message"]["content"])
        # Capture the sid while we're still in the request context
        sid = request.sid
        msg_content = message["message"]["content"]
        
        # Create a new event loop for this background task
        def background_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(process_message(msg_content, sid))
            except Exception as e:
                print(f"Error in background task: {e}")
            finally:
                loop.close()
        
        # Start the background task
        eventlet.spawn_n(background_task)

async def process_message(message, sid):
    print("Processing message...")
    try:
        # Stream the response using DatahouseAgent's process method
        async for chunk in datahouse_agent.process(message):
            if chunk:  # Only send non-empty chunks
                socketio.emit('message', {
                    'type': 'chat',
                    'message': {
                        'author': 'assistant',
                        'content': chunk,
                    },
                    'is_streaming': True
                }, room=sid)
        
        # Finalize the message when streaming is complete
        socketio.emit('message', {
            'type': 'chat',
            'message': {
                'author': 'assistant',
                'content': '',
            },
            'is_streaming': False
        }, room=sid)
        
    except Exception as e:
        print(f"Error in process_message: {e}")
        socketio.emit('error', {'message': str(e)}, room=sid)

if __name__ == '__main__':
    socketio.run(app=app, host='0.0.0.0', port=5173, debug=True)
