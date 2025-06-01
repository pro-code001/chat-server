from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room, send

app = Flask(__name__)
socketio = SocketIO(app)

users = {}  # Dictionary to store user data
rooms = {}  # Dictionary to store room data

@app.route('/')
def index():
    return "Server is running!"

@socketio.on('signup')
def handle_signup(data):
    email = data['email']
    username = data['username']
    password = data['password']
    if email in users:
        socketio.emit('signup_response', {'success': False, 'msg': 'Email is already registered.'})
    elif username in [user['username'] for user in users.values()]:
        socketio.emit('signup_response', {'success': False, 'msg': 'Username is already taken.'})
    else:
        users[email] = {'username': username, 'password': password}
        socketio.emit('signup_response', {'success': True, 'msg': 'Signup successful!'})

@socketio.on('login')
def handle_login(data):
    username = data['username']
    password = data['password']
    user = next((user for user in users.values() if user['username'] == username and user['password'] == password), None)
    if user:
        socketio.emit('login_response', {'success': True, 'msg': 'Login successful!'})
    else:
        socketio.emit('login_response', {'success': False, 'msg': 'Invalid username or password.'})

@socketio.on('create')
def handle_create(data):
    room = data['room']
    password = data['password']
    username = data['username']
    if room in rooms:
        socketio.emit('error', {'msg': 'Room already exists.'})
    else:
        rooms[room] = {'password': password, 'users': [username]}
        join_room(room)
        socketio.emit('created', {'room': room})

@socketio.on('join')
def handle_join(data):
    room = data['room']
    password = data['password']
    username = data['username']
    if room not in rooms:
        socketio.emit('error', {'msg': 'Room does not exist.'})
    elif rooms[room]['password'] != password:
        socketio.emit('error', {'msg': 'Incorrect room password.'})
    else:
        rooms[room]['users'].append(username)
        join_room(room)
        socketio.emit('joined', {'room': room})

@socketio.on('message')
def handle_message(data):
    room = data['room']
    username = data['username']
    msg = data['msg']
    send({'username': username, 'msg': msg, 'room': room}, room=room)

if __name__ == '__main__':
    if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
