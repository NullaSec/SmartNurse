import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import "./Mainpage.css";

function Home() {
  const navigate = useNavigate();
  const [message, setMessage] = useState("");

  useEffect(() => {
    const text =
      "Como é que é maltinha daqui com vocês é o RIIIIIIC DA FAZERESSSS! Está tudo bem contigo ou não queres dizer ao zé ric.";
    let index = 0;

    const interval = setInterval(() => {
      setMessage(text.slice(0, index + 1));
      index++;
      if (index === text.length) clearInterval(interval);
    }, 40);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="main-container">
      <div className="image-button-container">
        <h1>Welcome to Smart Nurse</h1>
        <div className="borda">
          <img src="./src/bot-image.png" alt="Description" />
          <div className="speech-bubble">
            <div className="speech-bubble-message">{message}</div>
          </div>
        </div>
        <p>Click the button below to start the chatbot.</p>
        <button onClick={() => navigate("/chat")} className="chat-button">
          ChatBot
        </button>
      </div>
    </div>
  );
}

export default Home;
