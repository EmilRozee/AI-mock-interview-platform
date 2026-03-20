import { useEffect, useState } from "react";
import { api } from "../services/api";

function formatDate(value) {
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function HistorySparkline({ points }) {
  if (!points || points.length < 2) {
    return <div className="muted">Need at least 2 practice days to show trend line.</div>;
  }

  const width = 260;
  const height = 80;
  const padding = 10;
  const maxX = points.length - 1;
  const maxY = 10;

  const path = points
    .map((point, index) => {
      const x = padding + (index / maxX) * (width - padding * 2);
      const y = height - padding - (Math.max(0, Math.min(point.average_score, maxY)) / maxY) * (height - padding * 2);
      return `${index === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");

  return (
    <svg className="sparkline" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Role score trend">
      <path d={path} fill="none" stroke="#1a7f64" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

export default function DashboardPage() {
  const [roles, setRoles] = useState([]);
  const [historyMap, setHistoryMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.dashboard();
        const dashboardRoles = data.roles || [];
        setRoles(dashboardRoles);

        const historyEntries = await Promise.all(
          dashboardRoles.map(async (role) => {
            const details = await api.dashboardRoleHistory(role.role_id);
            return [role.role_id, details];
          })
        );

        setHistoryMap(Object.fromEntries(historyEntries));
      } catch (err) {
        setError(err.message || "Could not load dashboard");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  if (loading) {
    return <section className="card">Loading dashboard...</section>;
  }

  if (error) {
    return <section className="card error-box">{error}</section>;
  }

  return (
    <section className="card">
      <h1>Readiness Dashboard</h1>
      <p className="muted">Track role-wise growth, weak areas, and latest practice activity.</p>

      {roles.length === 0 ? (
        <div className="muted">No roles selected yet. Go to Roles and select at least one role.</div>
      ) : (
        <div className="stats-grid">
          {roles.map((item) => (
            <article className="stat-card" key={item.role_id}>
              <h2>{item.role_name}</h2>
              <div className="readiness">{item.readiness_score}% Ready</div>
              <div>
                <strong>Average Score:</strong> {item.average_score}/10
              </div>
              <div>
                <strong>Consistency:</strong> {item.consistency_sessions} session(s), {item.consistency_percent}%
              </div>
              <div>
                <strong>Coverage:</strong> {item.categories_covered}/4 categories, {item.coverage_percent}%
              </div>
              <div>
                <strong>Trend:</strong> {item.trend} ({item.trend_delta > 0 ? "+" : ""}
                {item.trend_delta})
              </div>
              <div>
                <strong>Weak Areas:</strong> {item.weak_areas.length ? item.weak_areas.join(", ") : "None"}
              </div>
              <div>
                <strong>Last Practiced:</strong> {formatDate(item.last_practiced_date)}
              </div>

              <div className="trend-block">
                <strong>Score Timeline</strong>
                <HistorySparkline points={historyMap[item.role_id]?.history || []} />
              </div>

              <div className="trend-block">
                <strong>Category Performance</strong>
                <div className="category-bars">
                  {(historyMap[item.role_id]?.category_trends || []).map((categoryItem) => (
                    <div key={categoryItem.category} className="category-row">
                      <span>{categoryItem.category}</span>
                      <div className="bar-track">
                        <div className="bar-fill" style={{ width: `${(categoryItem.average_score / 10) * 100}%` }} />
                      </div>
                      <span>{categoryItem.average_score}/10</span>
                    </div>
                  ))}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
