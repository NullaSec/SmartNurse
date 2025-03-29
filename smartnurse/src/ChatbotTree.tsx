import { useState, useEffect, useRef } from "react";
import "./ChatbotTree.css";

interface Message {
  user: string;
  bot: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [isBotWriting, setIsBotWriting] = useState<boolean>(false);
  const [initialMessageSent, setInitialMessageSent] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!initialMessageSent) {
      const initialMessage =
        "Olá! Sou o assistente do Smart Diagnosis. Diga-me os seus sintomas e vou tentar ajudá-lo a descobrir o que pode estar por trás.";
      setMessages([{ user: "", bot: initialMessage }]);
      setInitialMessageSent(true);
    }
  }, [initialMessageSent]);

  const handleSendMessage = () => {
    if (input) {
      setMessages((prevMessages) => {
        const updatedMessages = [...prevMessages, { user: input, bot: "" }];
        return updatedMessages;
      });
      setInput("");
      setIsBotWriting(true);

      let botResponse =
        "Desculpa, mas não percebi. Podes reformular a tua pergunta?";

      let index = 0;
      const interval = setInterval(() => {
        setMessages((prevMessages) => {
          const updatedMessages = [...prevMessages];
          updatedMessages[updatedMessages.length - 1].bot = botResponse.slice(
            0,
            index + 1
          );
          return updatedMessages;
        });
        index += 1;
        if (index === botResponse.length) {
          clearInterval(interval);
          setIsBotWriting(false);
        }
      }, 50);

      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    }
  };

  const deleteMessage = () => {
    if (!isBotWriting) {
      setMessages([]);
      setInitialMessageSent(false);
    }
  };

  return (
    <div className="Chatbot">
      <button
        className="back-button"
        onClick={() => (window.location.href = "/")}
      >
        ⌂
      </button>
      <button
        className="diagnosis-button"
        onClick={() => (window.location.href = "/medSchool")}
      >
        MedSchool
      </button>
      <h1>Smart Diagnosis</h1>
      <div className="chatbox2">
        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={idx} className="message">
              {msg.user && (
                <div className="user-message">
                  <strong>Você: </strong>
                  {msg.user}
                </div>
              )}
              {msg.bot && (
                <div className="bot-message">
                  <img src="./src/bot-image.png" alt="Bot" />
                  <div className="bot-text">
                    <strong>Bot: </strong>
                    {msg.bot}
                  </div>
                </div>
              )}
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
            if (e.key === "Enter" && !isBotWriting) {
              handleSendMessage();
            }
          }}
          placeholder="Escreve os teus sintomas..."
        />
        <button onClick={handleSendMessage}>➤</button>
      </div>
    </div>
  );
}

export default App;
