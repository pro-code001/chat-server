// server.js
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const users = {};      // username: password
const rooms = {};      // roomName: { password, users: [] }

app.use(express.static('public')); // frontend fayllaringiz shu papkada bo‘lsa

io.on('connection', (socket) => {
  console.log('New client connected:', socket.id);

  socket.on('signup', ({username, password}) => {
    if (users[username]) {
      socket.emit('signup_response', {success: false, msg: 'Username already taken.'});
    } else {
      users[username] = password;
      socket.emit('signup_response', {success: true, msg: 'Sign up successful!'});
      console.log(User signed up: ${username});
    }
  });

  socket.on('login', ({username, password}) => {
    if (users[username] && users[username] === password) {
      socket.emit('login_response', {success: true, msg: 'Logged in successfully!'});
      console.log(User logged in: ${username});
    } else {
      socket.emit('login_response', {success: false, msg: 'Wrong username or password.'});
    }
  });

  socket.on('create', ({username, room, password}) => {
    if (rooms[room]) {
      socket.emit('error', {msg: 'Room already exists.'});
      return;
    }
    rooms[room] = {password, users: [username]};
    socket.join(room);
    socket.emit('created', {room});
    console.log(Room created: ${room} by ${username});
  });

  socket.on('join', ({username, room, password}) => {
    if (!rooms[room]) {
      socket.emit('error', {msg: 'Room does not exist.'});
      return;
    }
    if (rooms[room].password !== password) {
      socket.emit('error', {msg: 'Wrong room password.'});
      return;
    }
    rooms[room].users.push(username);
    socket.join(room);
    socket.emit('joined', {room});
    console.log(User ${username} joined room ${room});
  });

  socket.on('message', ({username, room, msg}) => {
    io.to(room).emit('message', {username, msg, room});
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(Server running on port ${PORT});
});
