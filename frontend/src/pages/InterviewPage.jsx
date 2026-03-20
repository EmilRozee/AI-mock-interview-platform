import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";

export default function InterviewPage() {
  const [roles, setRoles] = useState([]);
  const [roleId, setRoleId] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [question, setQuestion] = useState("");
  const [category, setCategory] = useState("");
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [rolesLoaded, setRolesLoaded] = useState(false);

  useEffect(() => {
    const loadRoles = async () => {
      try {
        const data = await api.selectedRoles();
        setRoles(data || []);
      } catch (err) {
        setError(err.message || "Could not load your roles");
      } finally {
        setRolesLoaded(true);
      }
    };

    loadRoles();
  }, []);

  const selectedRole = useMemo(() => roles.find((r) => String(r.id) === String(roleId)), [roles, roleId]);

  const startSession = async () => {
    if (!roleId) {
      setError("Select a role before starting.");
      return;
    }

    setLoading(true);
    setError("");
    setFeedback(null);
    setAnswer("");

    try {
      const data = await api.startSession(Number(roleId));
      setSessionId(data.session_id);
      setQuestion(data.question);
      setCategory(data.category);
    } catch (err) {
      const message = err.message || "Could not start interview session";
      if (message.includes("Role is not selected in your profile")) {
        setError("This role is not saved in your profile. Go to Roles and click Save Roles first.");
      } else {
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!sessionId || !question || !answer.trim()) {
      setError("Enter your answer before submitting.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await api.submitAnswer(sessionId, {
        question,
        answer,
        category,
      });
      setFeedback(data);
    } catch (err) {
      setError(err.message || "Could not evaluate answer");
    } finally {
      setLoading(false);
    }
  };

  const nextQuestion = async () => {
    if (!sessionId) {
      return;
    }

    setLoading(true);
    setError("");
    setFeedback(null);
    setAnswer("");

    try {
      const data = await api.nextQuestion(sessionId);
      setQuestion(data.question);
      setCategory(data.category);
    } catch (err) {
      setError(err.message || "Could not fetch next question");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card interview-layout">
      <h1>Mock Interview Session</h1>
      <p className="muted">Question styles: HR, conceptual technical, situational, and project-based.</p>

      {error ? <div className="error-box">{error}</div> : null}

      {rolesLoaded && roles.length === 0 ? (
        <div className="ok-box">
          No roles available for interview yet. Please choose your roles and save them first.
          <div style={{ marginTop: "8px" }}>
            <Link className="link-btn" to="/roles">
              Go to Role Selection
            </Link>
          </div>
        </div>
      ) : null}

      <div className="session-controls">
        <label>
          Choose role
          <select value={roleId} onChange={(e) => setRoleId(e.target.value)}>
            <option value="">Select role</option>
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.role_name}
              </option>
            ))}
          </select>
        </label>
        <button type="button" className="primary-btn" onClick={startSession} disabled={loading || !roleId}>
          {loading ? "Starting..." : "Start Session"}
        </button>
      </div>

      {selectedRole ? <div className="muted">Active role: {selectedRole.role_name}</div> : null}

      {question ? (
        <>
          <article className="question-card">
            <div className="pill">{category}</div>
            <h2>{question}</h2>
          </article>

          <label className="full-width">
            Your Answer
            <textarea
              rows={8}
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your response here..."
            />
          </label>

          <div className="row-actions">
            <button type="button" className="primary-btn" onClick={submitAnswer} disabled={loading || !answer.trim()}>
              {loading ? "Evaluating..." : "Submit Answer"}
            </button>
            <button type="button" className="ghost-btn" onClick={nextQuestion} disabled={loading || !sessionId}>
              Next Question
            </button>
          </div>
        </>
      ) : null}

      {feedback ? (
        <section className="feedback-panel">
          <h3>AI Feedback</h3>
          <p>
            <strong>Score:</strong> {feedback.score}/10
          </p>
          <p>
            <strong>Category:</strong> {feedback.category}
          </p>
          <p>
            <strong>Strengths:</strong> {(feedback.strengths || []).join(", ") || "-"}
          </p>
          <p>
            <strong>Weaknesses:</strong> {(feedback.weaknesses || []).join(", ") || "-"}
          </p>
          <p>
            <strong>Missing points:</strong> {(feedback.missing_points || []).join(", ") || "-"}
          </p>
          <p>
            <strong>Ideal Answer Example:</strong> {feedback.ideal_answer}
          </p>
        </section>
      ) : null}
    </section>
  );
}
