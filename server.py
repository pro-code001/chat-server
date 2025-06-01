from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, send
import re  # Import regular expressions for email validation
import random  # Import random for generating room IDs

app = Flask(__name__)
socketio = SocketIO(app)

users = {}  # Dictionary to store user data
rooms = {}  # Dictionary to store room data

@app.route('/')
def index():
    return render_template('index.html')  # Corrected file name

@socketio.on('signup')
def handle_signup(data):
    email = data['email']
    username = data['username']
    password = data['password']

    # Validate email format
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        socketio.emit('signup_response', {'success': False, 'msg': 'Invalid email format.'})
        return

    # Check if email or username is already taken
    if email in users:
        socketio.emit('signup_response', {'success': False, 'msg': 'Email is already registered.'})
        return
    elif username in [user['username'] for user in users.values()]:
        socketio.emit('signup_response', {'success': False, 'msg': 'Username is already taken.'})
        return

    # Add user to the dictionary
    users[email] = {'username': username, 'password': password}
    socketio.emit('signup_response', {'success': True, 'msg': 'Signup successful!'})

@socketio.on('login')
def handle_login(data):
    email = data['email']
    password = data['password']

    # Check if user exists and password matches
    user = users.get(email)
    if user and user['password'] == password:
        socketio.emit('login_response', {'success': True, 'msg': 'Login successful!'})
    else:
        socketio.emit('login_response', {'success': False, 'msg': 'Invalid email or password.'})

@socketio.on('create')
def handle_create(data):
    password = data['password']
    roomId = str(random.randint(100000000000, 999999999999))  # Generate random ID

    if roomId in rooms:
        socketio.emit('error', {'msg': 'Room ID conflict. Please try again.'})
        return

    rooms[roomId] = {'password': password, 'users': []}
    socketio.emit('created', {'roomId': roomId})

@socketio.on('join')
def handle_join(data):
    roomId = data['roomId']
    password = data['password']
    username = data['username']

    if roomId not in rooms:
        socketio.emit('error', {'msg': 'Room does not exist.'})
        return
    elif rooms[roomId]['password'] != password:
        socketio.emit('error', {'msg': 'Incorrect room password.'})
        return

    rooms[roomId]['users'].append(username)
    join_room(roomId)
    socketio.emit('joined', {'roomId': roomId})

@socketio.on('message')
def handle_message(data):
    room = data['room']
    username = data['username']
    msg = data['msg']
    send({'username': username, 'msg': msg, 'room': room}, room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
