
import { useState } from "react";
import { askQuestion, type QueryResponse } from "./api/client";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [rawResponse, setRawResponse] =
    useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!question.trim() || loading) return;

    setLoading(true);
    setError("");
    setAnswer("");
    setRawResponse(null);

    try {
      const data = await askQuestion(question);

      setRawResponse(data);
      setAnswer(
        typeof data.answer === "string"
          ? data.answer
          : typeof data.response === "string"
            ? data.response
            : JSON.stringify(data, null, 2)
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <header className="header">
        <div>
          <h1>LLM Playground</h1>
          <p>Local RAG experimentation environment</p>
        </div>
        <span className="status">
          <span className="status-dot" />
          Playground
        </span>
      </header>

      <section className="workspace">
        <div className="chat-panel">
          <div className="panel-heading">
            <h2>Chat</h2>
            <span>Ask your documents</span>
          </div>

          <div className="conversation">
            {!answer && !loading && !error && (
              <div className="empty-state">
                <h3>What would you like to know?</h3>
                <p>
                  Ask a question and your local RAG
                  pipeline will generate an answer.
                </p>
              </div>
            )}

            {answer && (
              <div className="message">
                <div className="message-label">Assistant</div>
                <div className="answer">{answer}</div>
              </div>
            )}

            {loading && (
              <div className="loading">
                Generating response...
              </div>
            )}

            {error && (
              <div className="error">{error}</div>
            )}
          </div>

          <form onSubmit={handleSubmit} className="input-area">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask something about your documents..."
              rows={3}
              disabled={loading}
            />

            <div className="input-footer">
              <span>Local LLM · RAG</span>
              <button
                type="submit"
                disabled={loading || !question.trim()}
              >
                {loading ? "Thinking..." : "Send question"}
              </button>
            </div>
          </form>
        </div>

        <aside className="response-panel">
          <div className="panel-heading">
            <h2>Response inspector</h2>
            <span>Raw API output</span>
          </div>

          {rawResponse ? (
            <pre className="json-viewer">
              {JSON.stringify(rawResponse, null, 2)}
            </pre>
          ) : (
            <div className="inspector-empty">
              JSON responses will appear here.
            </div>
          )}
        </aside>
      </section>
    </main>
  );
}

export default App;
