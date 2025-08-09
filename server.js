const WebSocket = require("ws");
const wss = new WebSocket.Server({ port: 3000 });

let rooms = {}; // { roomName: { password: "...", clients: [] } }

wss.on("connection", (ws) => {
  ws.on("message", (message) => {
    const data = JSON.parse(message);

    if (data.type === "join") {
      if (!rooms[data.room]) {
        rooms[data.room] = { password: data.password, clients: [] };
      }
      if (rooms[data.room].password !== data.password) {
        ws.send(JSON.stringify({ type: "error", message: "Parol noto‘g‘ri!" }));
        return;
      }
      if (rooms[data.room].clients.length >= 2) {
        ws.send(JSON.stringify({ type: "error", message: "Xona to‘la!" }));
        return;
      }
      ws.room = data.room;
      rooms[data.room].clients.push(ws);
      ws.send(JSON.stringify({ type: "info", message: "Xonaga qo‘shildingiz." }));
    }

    if (data.type === "message" && ws.room) {
      rooms[ws.room].clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify({ type: "message", text: data.text, sender: data.sender, time: data.time }));
        }
      });
    }
  });

  ws.on("close", () => {
    if (ws.room && rooms[ws.room]) {
      rooms[ws.room].clients = rooms[ws.room].clients.filter((c) => c !== ws);
      if (rooms[ws.room].clients.length === 0) delete rooms[ws.room];
    }
  });
});

console.log("Server 3000-portda ishga tushdi");
