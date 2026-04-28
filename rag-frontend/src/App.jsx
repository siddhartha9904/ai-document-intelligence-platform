import { useState } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ query })
      });

      const data = await res.json();

      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (error) {
      setAnswer("Something went wrong.");
    }

    setLoading(false);
  };
  const [file, setFile] = useState(null);
  const uploadFile = async () => {
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  await fetch("http://127.0.0.1:8000/upload", {
    method: "POST",
    body: formData
  });

  alert("File uploaded successfully!");
  };


  return (
    <div className="container">
      <h1>Multi-Document AI Assistant</h1>
      <p className="subtitle">
      Ask questions from your uploaded documents
      </p>
      <div className="upload-box">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <button onClick={uploadFile}>
          Upload
        </button>
      </div>
      <div className="search-box">
        <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") askQuestion();
        }}
        placeholder="Ask anything..."

        />

        <button onClick={askQuestion} disabled={loading}>
          {loading ? "..." : "Ask"}
        </button>
      </div>

      {loading && <p className="loading">Thinking...</p>}

      {answer && (
        <div className="card">
          <h2>Answer</h2>
          <p>{answer}</p>

          <h3>Sources</h3>
          <ul>
            {sources.map((src, i) => (
              <li key={i}>{src}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;