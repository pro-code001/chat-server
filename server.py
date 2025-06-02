import asyncio
import websockets
import json
import os
from aiohttp import web
import hashlib
import time

# Foydalanuvchilar va xabarlar bazasi (JSON fayl)
USERS_FILE = "users.json"
MESSAGES_FILE = "messages.json"

# Fayllarni boshlash
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)
if not os.path.exists(MESSAGES_FILE):
    with open(MESSAGES_FILE, "w") as f:
        json.dump({}, f)

# Foydalanuvchilarni o‘qish
def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

# Xabarlarni o‘qish
def load_messages():
    with open(MESSAGES_FILE, "r") as f:
        return json.load(f)

# Foydalanuvchilarni saqlash
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# Xabarlarni saqlash
def save_messages(messages):
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=2)

# Parolni hash qilish
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# WebSocket ulanishlari
connected_users = {}

async def handle_connection(websocket, path):
    # Foydalanuvchi identifikatorini olish
    user = path.split("user=")[-1]
    connected_users[user] = websocket
    print(f"{user} ulandi")

    try:
        async for message in websocket:
            data = json.loads(message)
            sender = data["sender"]
            chat = data["chat"]
            msg = data["message"]
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            # Xabarni saqlash
            messages = load_messages()
            chat_key = f"{sender}_{chat}"
            if chat_key not in messages:
                messages[chat_key] = []
            messages[chat_key].append({"sender": sender, "message": msg, "timestamp": timestamp})
            save_messages(messages)

            # Xabarni chatdagi barcha ishtirokchilarga yuborish
            for recipient in [sender, chat]:
                if recipient in connected_users and connected_users[recipient].open:
                    await connected_users[recipient].send(json.dumps({"sender": sender, "message": msg, "timestamp": timestamp}))

    except websockets.exceptions.ConnectionClosed:
        print(f"{user} ulanishi yopildi")
        del connected_users[user]

# Statik fayl xizmati
async def serve_index(request):
    return web.FileResponse("./index.html")

# HTTP API
async def register(request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    users = load_users()

    if username in users:
        return web.json_response({"success": False, "message": "Bu ism band!"})
    
    users[username] = hash_password(password)
    save_users(users)
    return web.json_response({"success": True})

async def login(request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    users = load_users()

    if username in users and users[username] == hash_password(password):
        return web.json_response({"success": True})
    return web.json_response({"success": False, "message": "Noto‘g‘ri ism yoki parol!"})

async def get_messages(request):
    user = request.query.get("user")
    chat = request.query.get("chat")
    messages = load_messages()
    chat_key = f"{user}_{chat}"
    reverse_key = f"{chat}_{user}"
    result = messages.get(chat_key, []) + messages.get(reverse_key, [])
    return web.json_response({"messages": result})

# HTTP server
app = web.Application()
app.add_routes([
    web.get("/", serve_index),  # index.html ni xizmat qilish
    web.post("/register", register),
    web.post("/login", login),
    web.get("/messages", get_messages)
])

# WebSocket server
async def main():
    server = await websockets.serve(handle_connection, "0.0.0.0", 8000)
    print("WebSocket server 8000-portda ishga tushdi")
    await web._run_app(app, host="0.0.0.0", port=8001)  # HTTP server 8001-portda
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
