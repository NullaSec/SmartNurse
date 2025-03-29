import { useNavigate } from "react-router-dom";
import "./Mainpage.css";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="main-container">
      <div className="image-button-container">
        <h1>Welcome to Smart Nurse</h1>
        <div className="borda">
          <img src="./src/bot-image.png" alt="Description" />
          <div className="speech-bubble">Hello! I'm your assistant</div>
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
