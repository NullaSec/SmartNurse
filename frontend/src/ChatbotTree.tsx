import { useState, useEffect, useRef } from "react";
import "./ChatbotTree.css";
import { performTriage } from "./api";

// Definindo os tipos de dados
interface Message {
  user: string;
  bot: string;
}

interface Diagnosis {
  category: string;
  urgency: string;
  alerts: string[];
  specialty_id?: string; // Adicionado para compatibilidade com o backend
}

interface MedicalInfo {
  relevant_info: Array<{
    text: string;
    confidence: number;
  }>;
  sources: string[];
  recommendation: string;
}

interface TriageData {
  diagnosis: Diagnosis;
  medical_info: MedicalInfo;
  ai_explanation: string;
  status?: string; // Opcional para compatibilidade
}

function ChatbotTree() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [isBotWriting, setIsBotWriting] = useState<boolean>(false);
  const [initialMessageSent, setInitialMessageSent] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [triageData, setTriageData] = useState<TriageData | null>(null);

  useEffect(() => {
    if (!initialMessageSent) {
      const initialMessage =
        "Olá! Sou o assistente do Smart Diagnosis. Descreva seus sintomas principais (ex: 'dor de cabeça intensa com náuseas') e eu farei uma triagem médica.";
      setMessages([{ user: "", bot: initialMessage }]);
      setInitialMessageSent(true);
    }
  }, [initialMessageSent]);

  useEffect(() => {
    const testConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/test-connection');
        const data = await response.json();
        if (!data.connected) {
          setMessages([{
            user: "",
            bot: "⚠️ Sistema offline: Não foi possível conectar à base de dados médicos. Contate o suporte."
          }]);
        }
      } catch (error) {
        setMessages([{
          user: "",
          bot: "🚨 Erro crítico: O serviço médico está indisponível no momento."
        }]);
      }
    };
    
    testConnection();
  }, []);

  const simulateTyping = (response: string, callback?: () => void) => {
    let index = 0;
    const interval = setInterval(() => {
      setMessages((prevMessages) => {
        const updatedMessages = [...prevMessages];
        updatedMessages[updatedMessages.length - 1].bot = response.slice(
          0,
          index + 1
        );
        return updatedMessages;
      });
      index += 1;
      if (index === response.length) {
        clearInterval(interval);
        setIsBotWriting(false);
        if (callback) callback();
      }
    }, 30);
  };

  const handleSendMessage = async () => {
    if (input && !isBotWriting) {
      setMessages((prev) => [...prev, { user: input, bot: "" }]);
      setInput("");
      setIsBotWriting(true);

      try {
        simulateTyping("Analisando seus sintomas...", async () => {
          try {
            const data: TriageData = await performTriage(input);
            setTriageData(data);

            let botResponse = `🔍 Diagnóstico: ${data.diagnosis.category}\n`;
            botResponse += `🚨 Nível de Urgência: ${data.diagnosis.urgency}\n\n`;

            if (data.diagnosis.alerts.length > 0) {
              botResponse += "⚠️ Alertas:\n";
              data.diagnosis.alerts.forEach((alert: string) => {
                botResponse += `• ${alert}\n`;
              });
              botResponse += "\n";
            }

            botResponse += `📌 Recomendação: ${data.medical_info.recommendation}\n\n`;
            botResponse += `💡 Explicação:\n${data.ai_explanation}`;

            setMessages((prev) => [...prev, { user: "", bot: "" }]);
            simulateTyping(botResponse);
          } catch (error: unknown) {
            const errorMessage =
              error instanceof Error
                ? error.message
                : "Ocorreu um erro na triagem";
            setMessages((prev) => [
              ...prev,
              { user: "", bot: `❌ Erro: ${errorMessage}` },
            ]);
            setIsBotWriting(false);
          }
        });
      } catch (error: unknown) {
        const errorMessage =
          error instanceof Error ? error.message : "Erro ao processar";
        simulateTyping(`❌ ${errorMessage}`);
      }
    }
  };

  const deleteMessage = () => {
    if (!isBotWriting) {
      setMessages([]);
      setTriageData(null);
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
                    <strong>Assistente: </strong>
                    {msg.bot.split("\n").map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
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
          placeholder="Descreva seus sintomas..."
          disabled={isBotWriting}
        />
        <button onClick={handleSendMessage} disabled={isBotWriting}>
          {isBotWriting ? "..." : "➤"}
        </button>
      </div>

      {triageData && (
        <div className="triage-details">
          <ul>
            {triageData.medical_info.sources.map(
              (source: string, idx: number) => (
                <li key={idx}>{source}</li>
              )
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ChatbotTree;
