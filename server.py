from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
socketio = SocketIO(app)

chat_rooms = {}  # Xonalar va parollari saqlanadi

@app.route('/')
def index():
    return render_template('index.html')  # templates/index.html ni render qiladi

@socketio.on('create')
def handle_create(data):
    room = data['room']
    password = data['password']
    username = data['username']

    if room in chat_rooms:
        socketio.emit('error', {'msg': 'Room already exists!'}, room=request.sid)
    else:
        chat_rooms[room] = password
        join_room(room)
        send(f"{username} created and joined the room {room}", room=room)
        socketio.emit('created', {'room': room}, room=request.sid)

@socketio.on('join')
def handle_join(data):
    room = data['room']
    password = data['password']
    username = data['username']

    if room not in chat_rooms:
        socketio.emit('error', {'msg': 'Room does not exist!'}, room=request.sid)
    elif chat_rooms[room] == password:
        join_room(room)
        send(f"{username} joined the room {room}", room=room)
        socketio.emit('join', {'room': room}, room=request.sid)
    else:
        socketio.emit('error', {'msg': 'Incorrect password!'}, room=request.sid)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    msg = data['msg']
    send(msg, room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
