from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
socketio = SocketIO(app)

# Chat xonalar uchun vaqtinchalik saqlash
chat_rooms = {}

@app.route('/')
def index():
    return "Server ishlayapti! Frontend alohida bo'ladi."

@socketio.on('join')
def handle_join(data):
    room = data['room']
    password = data['password']
    username = data['username']

    if room not in chat_rooms:
        chat_rooms[room] = password
        join_room(room)
        send(f"{username} xonaga qo'shildi", room=room)
    elif chat_rooms[room] == password:
        join_room(room)
        send(f"{username} xonaga qo'shildi", room=room)
    else:
        socketio.emit('error', {'msg': 'Parol noto‘g‘ri!'}, room=request.sid)

@socketio.on('message')
def handle_message(data):
    send(data['msg'], room=data['room'])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
