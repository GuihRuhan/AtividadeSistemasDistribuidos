import { useEffect, useState, useRef } from "react";

function App() {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [username, setUsername] = useState("");
  const [connected, setConnected] = useState(false);
  const [users, setUsers] = useState([]);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (!socket) return;

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "message") {
        setMessages((prev) => [
          ...prev,
          {
            text: data.message,
            sender: data.from === username ? "me" : "other",
            from: data.from,
            time: data.time
          }
        ]);
      }

      if (data.type === "users") {
        setUsers(data.users);
      }
    };
  }, [socket, username]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const connectUser = () => {
    const ws = new WebSocket("ws://localhost:5050");

    ws.onopen = () => {
      ws.send(JSON.stringify({ username }));
      setConnected(true);
    };

    setSocket(ws);
  };

  const sendMessage = () => {
    if (!input.trim()) return;

    const msg = {
      type: "message",
      id: Date.now().toString(),
      message: input,
      time: new Date().toLocaleTimeString()
    };

    socket.send(JSON.stringify(msg));

    setMessages((prev) => [
      ...prev,
      {
        text: input,
        sender: "me",
        from: username,
        time: msg.time
      }
    ]);

    setInput("");
  };

  if (!connected) {
    return (
      <div style={styles.login}>
        <h2>Entrar no Chat</h2>
        <input
          placeholder="Seu nome"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <button onClick={connectUser}>Entrar</button>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.sidebar}>
        <h3>Usuários</h3>
        {users.map((u, i) => (
          <div key={i} style={styles.user}>
            🟢 {u}
          </div>
        ))}
      </div>

      <div style={styles.chatBox}>
        <div style={styles.header}>💬 Chat</div>

        <div style={styles.messages}>
          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                ...styles.messageRow,
                justifyContent:
                  msg.sender === "me" ? "flex-end" : "flex-start"
              }}
            >
              <div style={styles.bubble}>
                {msg.sender !== "me" && (
                  <div style={styles.name}>{msg.from}</div>
                )}
                <div>{msg.text}</div>
                <div style={styles.time}>{msg.time}</div>
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        <div style={styles.inputArea}>
          <input
            style={styles.input}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button style={styles.button} onClick={sendMessage}>
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: { display: "flex", height: "100vh" },
  sidebar: { width: 200, background: "#075E54", color: "white", padding: 10 },
  user: { padding: 5 },
  chatBox: { flex: 1, display: "flex", flexDirection: "column" },
  header: { padding: 15, background: "#128C7E", color: "white" },
  messages: { flex: 1, padding: 10, overflowY: "auto", background: "#ECE5DD" },
  messageRow: { display: "flex", marginBottom: 10 },
  bubble: { background: "#FFF", padding: 10, borderRadius: 10, maxWidth: "60%" },
  name: { fontWeight: "bold", fontSize: 12 },
  time: { fontSize: 10, color: "gray", textAlign: "right" },
  inputArea: { display: "flex", padding: 10 },
  input: { flex: 1, padding: 10 },
  button: { marginLeft: 10, background: "#25D366", color: "white", border: "none", padding: "0 15px" },
  login: { display: "flex", flexDirection: "column", alignItems: "center", marginTop: 100 }
};

export default App;