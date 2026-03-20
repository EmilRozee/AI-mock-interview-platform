import { Navigate, Route, Routes } from "react-router-dom";
import Header from "./components/Header";
import AuthPage from "./pages/AuthPage";
import RolesPage from "./pages/RolesPage";
import DashboardPage from "./pages/DashboardPage";
import InterviewPage from "./pages/InterviewPage";
import { getToken } from "./services/auth";

function ProtectedRoute({ children }) {
  if (!getToken()) {
    return <Navigate to="/auth" replace />;
  }
  return children;
}

export default function App() {
  return (
    <div className="app-shell">
      <Header />
      <main className="page-wrap">
        <Routes>
          <Route path="/auth" element={<AuthPage />} />
          <Route
            path="/roles"
            element={
              <ProtectedRoute>
                <RolesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/interview"
            element={
              <ProtectedRoute>
                <InterviewPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to={getToken() ? "/roles" : "/auth"} replace />} />
        </Routes>
      </main>
    </div>
  );
}
