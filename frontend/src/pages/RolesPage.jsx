import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";

export default function RolesPage() {
  const [roles, setRoles] = useState([]);
  const [selected, setSelected] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const [allRoles, selectedRoles] = await Promise.all([api.listRoles(), api.selectedRoles()]);
        setRoles(allRoles);
        setSelected(new Set((selectedRoles || []).map((role) => role.id)));
      } catch (err) {
        setError(err.message || "Could not load roles");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const selectedCount = useMemo(() => selected.size, [selected]);

  const toggleRole = (roleId) => {
    const next = new Set(selected);
    if (next.has(roleId)) {
      next.delete(roleId);
    } else {
      next.add(roleId);
    }
    setSelected(next);
  };

  const onSave = async () => {
    setSaving(true);
    setMessage("");
    setError("");
    try {
      await api.selectRoles(Array.from(selected));
      setMessage("Roles saved successfully.");
    } catch (err) {
      setError(err.message || "Could not save roles");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <section className="card">Loading roles...</section>;
  }

  return (
    <section className="card">
      <h1>Select your target roles</h1>
      <p className="muted">Pick multiple roles. Your readiness score is tracked separately for each role.</p>

      {error ? <div className="error-box">{error}</div> : null}
      {message ? <div className="ok-box">{message}</div> : null}

      <div className="roles-grid">
        {roles.map((role) => (
          <button
            key={role.id}
            type="button"
            className={`role-chip ${selected.has(role.id) ? "selected" : ""}`}
            onClick={() => toggleRole(role.id)}
          >
            {role.role_name}
          </button>
        ))}
      </div>

      <div className="row-actions">
        <span className="muted">{selectedCount} role(s) selected</span>
        <button className="primary-btn" type="button" onClick={onSave} disabled={saving || selectedCount === 0}>
          {saving ? "Saving..." : "Save Roles"}
        </button>
      </div>

      <div className="row-actions">
        <Link className="link-btn" to="/dashboard">
          View Dashboard
        </Link>
        <Link className="link-btn" to="/interview">
          Start Interview
        </Link>
      </div>
    </section>
  );
}
