from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
socketio = SocketIO(app)

chat_rooms = {}  # {room_name: password}
users = {}       # {username: password} - oddiy foydalanuvchi bazasi

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('signup')
def handle_signup(data):
    username = data['username']
    password = data['password']

    if username in users:
        socketio.emit('signup_response', {'success': False, 'msg': 'Username already taken!'}, room=request.sid)
    else:
        users[username] = password
        socketio.emit('signup_response', {'success': True, 'msg': 'Sign up successful!'}, room=request.sid)

@socketio.on('login')
def handle_login(data):
    username = data['username']
    password = data['password']

    if username not in users:
        socketio.emit('login_response', {'success': False, 'msg': 'User does not exist!'}, room=request.sid)
    elif users[username] != password:
        socketio.emit('login_response', {'success': False, 'msg': 'Incorrect password!'}, room=request.sid)
    else:
        socketio.emit('login_response', {'success': True, 'msg': 'Login successful!'}, room=request.sid)

# Chat room handlers (create, join, message) shu yerda qoladi
# Qolgan kodlarni o'zgartirish shart emas, lekin siz xohlasangiz foydalanuvchi login bo'lmasa chatga kira olmasin deb qo'shishingiz mumkin.

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
