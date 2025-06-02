import asyncio
import websockets
import json
import os
from aiohttp import web
import hashlib
import time
from modules.auth import register_user, login_user
from modules.messages import save_message, get_messages
from modules.files import handle_file_upload
from modules.groups import create_group, add_user_to_group

# Statik fayllar papkasi
STATIC_DIR = "static"

async def serve_static(request):
    path = request.path[1:] if request.path.startswith("/") else request.path
    if not path:
        path = "index.html"
    file_path = os.path.join(STATIC_DIR, path)
    if os.path.exists(file_path):
        return web.FileResponse(file_path)
    return web.Response(status=404, text="Fayl topilmadi")

# WebSocket ulanishlari
connected_users = {}

async def handle_connection(websocket, path):
    user = path.split("user=")[-1]
    connected_users[user] = websocket
    print(f"{user} ulandi")

    # Onlayn statusni yangilash
    await broadcast_status(user, "online")

    try:
        async for message in websocket:
            data = json.loads(message)
            sender = data["sender"]
            chat = data["chat"]
            msg = data.get("message")
            file = data.get("file")
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            if msg:
                # Xabarni saqlash
                save_message(sender, chat, msg, timestamp)
                # Xabarni yuborish
                for recipient in [sender, chat]:
                    if recipient in connected_users and connected_users[recipient].open:
                        await connected_users[recipient].send(json.dumps({
                            "sender": sender,
                            "message": msg,
                            "timestamp": timestamp,
                            "type": "text"
                        }))
            elif file:
                # Faylni saqlash
                file_url = handle_file_upload(file, sender)
                for recipient in [sender, chat]:
                    if recipient in connected_users and connected_users[recipient].open:
                        await connected_users[recipient].send(json.dumps({
                            "sender": sender,
                            "file_url": file_url,
                            "timestamp": timestamp,
                            "type": "file"
                        }))

    except websockets.exceptions.ConnectionClosed:
        print(f"{user} ulanishi yopildi")
        del connected_users[user]
        await broadcast_status(user, "offline")

async def broadcast_status(user, status):
    for recipient in connected_users:
        if connected_users[recipient].open:
            await connected_users[recipient].send(json.dumps({
                "type": "status",
                "user": user,
                "status": status
            }))

# HTTP API
app = web.Application()
app.add_routes([
    web.get("/{path:.*}", serve_static),  # Statik fayllarni xizmat qilish
    web.post("/register", register_user),
    web.post("/login", login_user),
    web.get("/messages", get_messages),
    web.post("/upload", handle_file_upload),
    web.post("/create_group", create_group)
])

# WebSocket server
async def main():
    server = await websockets.serve(handle_connection, "0.0.0.0", 8000)
    print("WebSocket server 8000-portda ishga tushdi")
    await web._run_app(app, host="0.0.0.0", port=8001)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
