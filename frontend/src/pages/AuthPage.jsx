import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { setToken } from "../services/auth";

export default function AuthPage() {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const payload = { email, password };
      const data = mode === "login" ? await api.login(payload) : await api.signup(payload);
      setToken(data.access_token);
      navigate("/roles");
    } catch (err) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card auth-card">
      <h1>{mode === "login" ? "Welcome back" : "Create account"}</h1>
      <p className="muted">Practice role-based interviews and track readiness with AI feedback.</p>

      <form onSubmit={onSubmit} className="form-grid">
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
        </label>

        {error ? <div className="error-box">{error}</div> : null}

        <button className="primary-btn" type="submit" disabled={loading}>
          {loading ? "Please wait..." : mode === "login" ? "Login" : "Sign up"}
        </button>
      </form>

      <button type="button" className="text-btn" onClick={() => setMode(mode === "login" ? "signup" : "login")}>
        {mode === "login" ? "New user? Create an account" : "Already have an account? Login"}
      </button>
    </section>
  );
}
