import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./Mainpage";
import Chatbot from "./Chatbot";
import ChatbotTree from "./ChatbotTree";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/medSchool" element={<Chatbot />} />
        <Route path="/smartDiag" element={<ChatbotTree />} />
      </Routes>
    </Router>
  );
}

export default App;
