import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import "./Mainpage.css";

function Home() {
  const navigate = useNavigate();
  const [message, setMessage] = useState("");

  useEffect(() => {
    const text =
      "Sou um assistente virtual desenvolvido para esclarecer as tuas dúvidas sobre saúde e oferecer-te um diagnóstico rápido. Se tiveres questões sobre doenças, sintomas ou tratamentos, estou aqui para te ajudar de forma simples e eficaz!";
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
        </div>
        <div className="speech-bubble">
          <div className="speech-bubble-message">{message}</div>
        </div>
        <p>Click a button below to start a chatbot.</p>
        <div className="button-container">
          <button
            onClick={() => navigate("/smartDiag")}
            className="chat-button"
          >
            <img src="./src/SmartDiag.png" alt="SmartDiag" />
          </button>
          <button
            onClick={() => navigate("/medSchool")}
            className="chat-button"
          >
            <img src="./src/medSchool.png" alt="MedSchool" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default Home;
