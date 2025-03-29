import { useState, useEffect, useRef } from "react";
import "./App.css";

interface Message {
  user: string;
  bot: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [isBotWriting, setIsBotWriting] = useState<boolean>(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = () => {
    if (input) {
      const newBotMessage = "I am analyzing your message.";
      setMessages([...messages, { user: input, bot: "" }]);
      setInput("");
      setIsBotWriting(true);

      let index = 0;
      const interval = setInterval(() => {
        setMessages((prevMessages) => {
          const updatedMessages = [...prevMessages];
          updatedMessages[updatedMessages.length - 1].bot = newBotMessage.slice(
            0,
            index + 1
          );
          return updatedMessages;
        });
        index += 1;
        if (index === newBotMessage.length) {
          clearInterval(interval);
          setIsBotWriting(false);
        }
      }, 50);
    }
  };

  const deleteMessage = () => {
    if (!isBotWriting) {
      setMessages([]);
    }
  };

  return (
    <div className="App">
      <h1>Smart Nurse</h1>
      <div className="chatbox">
        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={idx} className="message">
              <div className="user-message">{msg.user}</div>
              <div className="bot-message">
                <img src="./src/bot-image.png" alt="Bot" />
                <div className="bot-text">
                  <strong>Bot: </strong>
                  {msg.bot}
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>
      <div className="input-container">
        <button
          className="delete-button"
          onClick={deleteMessage}
          disabled={isBotWriting}
        >
          🗑️
        </button>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleSendMessage();
            }
          }}
          placeholder="Type your message here..."
        />
        <button onClick={handleSendMessage}>➤</button>
      </div>
    </div>
  );
}

export default App;
