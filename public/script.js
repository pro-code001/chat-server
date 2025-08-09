let ws;
let name;

document.getElementById("joinBtn").onclick = () => {
  name = document.getElementById("name").value;
  const room = document.getElementById("room").value;
  const password = document.getElementById("password").value;

  ws = new WebSocket("ws://localhost:3000");

  ws.onopen = () => {
    ws.send(JSON.stringify({ type: "join", room, password }));
  };

  ws.onmessage = (msg) => {
    const data = JSON.parse(msg.data);
    if (data.type === "error") {
      document.getElementById("error").innerText = data.message;
    }
    if (data.type === "info") {
      document.querySelector(".join-screen").classList.add("hidden");
      document.querySelector(".chat-screen").classList.remove("hidden");
    }
    if (data.type === "message") {
      const div = document.createElement("div");
      div.classList.add("message");
      div.classList.add(data.sender === name ? "mine" : "theirs");
      div.innerHTML = `<strong>${data.sender}:</strong> ${data.text} <small>${data.time}</small>`;
      document.getElementById("messages").appendChild(div);
      div.scrollIntoView();
    }
  };
};

document.getElementById("sendBtn").onclick = () => {
  const text = document.getElementById("msgInput").value;
  const time = new Date().toLocaleTimeString();
  ws.send(JSON.stringify({ type: "message", text, sender: name, time }));
  document.getElementById("msgInput").value = "";
};
