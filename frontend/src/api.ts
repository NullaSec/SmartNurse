export const performTriage = async (symptoms: string, history = "Não informado", age = 0) => {
  const response = await fetch("http://localhost:8000/api/triage", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symptoms, history, age }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Erro na triagem");
  }

  return await response.json();
};