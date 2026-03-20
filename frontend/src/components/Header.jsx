import { Link, useLocation, useNavigate } from "react-router-dom";
import { clearToken, getToken } from "../services/auth";

export default function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const isLoggedIn = Boolean(getToken());

  const onLogout = () => {
    clearToken();
    navigate("/auth");
  };

  return (
    <header className="topbar">
      <div className="brand">Interview Forge</div>
      {isLoggedIn ? (
        <nav className="nav-links">
          <Link className={location.pathname === "/roles" ? "active" : ""} to="/roles">
            Roles
          </Link>
          <Link className={location.pathname === "/dashboard" ? "active" : ""} to="/dashboard">
            Dashboard
          </Link>
          <Link className={location.pathname === "/interview" ? "active" : ""} to="/interview">
            Interview
          </Link>
          <button type="button" className="ghost-btn" onClick={onLogout}>
            Logout
          </button>
        </nav>
      ) : (
        <nav className="nav-links">
          <Link className={location.pathname === "/auth" ? "active" : ""} to="/auth">
            Login
          </Link>
        </nav>
      )}
    </header>
  );
}
