const express = require("express");
const http = require("http");
const WebSocket = require("ws");
const path = require("path");

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Statik fayllarni (client HTML/JS/CSS) xizmat qilish
app.use(express.static(path.join(__dirname, "public")));

// WebSocket ulanish
wss.on("connection", (ws) => {
  console.log("Yangi foydalanuvchi ulandi");

  ws.on("message", (message) => {
    console.log("Xabar:", message.toString());

    // Barcha ulanganlarga yuborish
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message.toString());
      }
    });
  });

  ws.on("close", () => {
    console.log("Foydalanuvchi chiqdi");
  });
});

// Render yoki lokal port
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`${PORT}-portda ishga tushdi`);
});
