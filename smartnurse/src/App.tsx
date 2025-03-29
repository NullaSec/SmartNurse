import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./Mainpage";
import Chatbot from "./ChatBot";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chat" element={<Chatbot />} />
      </Routes>
    </Router>
  );
}

export default App;
