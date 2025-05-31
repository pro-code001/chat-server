from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
socketio = SocketIO(app)

rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create')
def handle_create(data):
    room = data['room']
    password = data['password']
    username = data['username']

    if room in rooms:
        emit('error', {'msg': 'Room already exists.'})
        return

    rooms[room] = {'password': password}
    join_room(room)
    emit('created', {'room': room})

@socketio.on('join')
def handle_join(data):
    room = data['room']
    password = data['password']
    username = data['username']

    if room not in rooms:
        emit('error', {'msg': 'Room does not exist.'})
        return

    if rooms[room]['password'] != password:
        emit('error', {'msg': 'Incorrect password.'})
        return

    join_room(room)
    emit('joined', {'room': room})

@socketio.on('message')
def handle_message(data):
    room = data['room']
    msg = data['msg']
    emit('message', msg, to=room)

if __name__ == '__main__':
    socketio.run(app)
