from __future__ import annotations

from pathlib import Path
import sys
import uuid

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import app


def assert_key(data: dict, key: str) -> None:
    if key not in data:
        raise AssertionError(f"Missing key '{key}' in response: {data}")


def main() -> None:
    client = TestClient(app)

    email = f"smoke_{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongPass123"

    signup = client.post("/api/v1/auth/signup", json={"email": email, "password": password})
    if signup.status_code != 200:
        raise AssertionError(f"Signup failed: {signup.status_code}, {signup.text}")

    token = signup.json().get("access_token")
    if not token:
        raise AssertionError("Signup did not return access token")

    headers = {"Authorization": f"Bearer {token}"}

    roles_resp = client.get("/api/v1/roles/")
    if roles_resp.status_code != 200:
        raise AssertionError(f"Roles fetch failed: {roles_resp.status_code}, {roles_resp.text}")

    roles = roles_resp.json()
    if len(roles) < 2:
        raise AssertionError("Expected at least 2 predefined roles")

    selected_ids = [roles[0]["id"], roles[1]["id"]]
    select_resp = client.post("/api/v1/roles/select", headers=headers, json={"role_ids": selected_ids})
    if select_resp.status_code != 200:
        raise AssertionError(f"Role selection failed: {select_resp.status_code}, {select_resp.text}")

    selected_resp = client.get("/api/v1/roles/selected", headers=headers)
    if selected_resp.status_code != 200:
        raise AssertionError(f"Selected roles fetch failed: {selected_resp.status_code}, {selected_resp.text}")

    start = client.post("/api/v1/interview/sessions/start", headers=headers, json={"role_id": selected_ids[0]})
    if start.status_code != 200:
        raise AssertionError(f"Start session failed: {start.status_code}, {start.text}")

    start_data = start.json()
    assert_key(start_data, "session_id")
    assert_key(start_data, "question")
    assert_key(start_data, "category")

    session_id = start_data["session_id"]

    submit = client.post(
        f"/api/v1/interview/sessions/{session_id}/answer",
        headers=headers,
        json={
            "question": start_data["question"],
            "answer": "I handled a cross-team delivery challenge by aligning milestones, risks, and communication with stakeholders.",
            "category": start_data["category"],
        },
    )
    if submit.status_code != 200:
        raise AssertionError(f"Submit answer failed: {submit.status_code}, {submit.text}")

    evaluation = submit.json()
    assert_key(evaluation, "score")
    assert_key(evaluation, "strengths")
    assert_key(evaluation, "weaknesses")
    assert_key(evaluation, "missing_points")
    assert_key(evaluation, "ideal_answer")

    dashboard = client.get("/api/v1/dashboard/me", headers=headers)
    if dashboard.status_code != 200:
        raise AssertionError(f"Dashboard fetch failed: {dashboard.status_code}, {dashboard.text}")

    dashboard_data = dashboard.json()
    roles_data = dashboard_data.get("roles", [])
    if not roles_data:
        raise AssertionError("Dashboard did not return role progress entries")

    first_role = roles_data[0]
    for key in [
        "readiness_score",
        "average_score",
        "consistency_sessions",
        "consistency_percent",
        "categories_covered",
        "coverage_percent",
        "trend",
        "trend_delta",
    ]:
        assert_key(first_role, key)

    role_history = client.get(f"/api/v1/dashboard/role-history/{selected_ids[0]}", headers=headers)
    if role_history.status_code != 200:
        raise AssertionError(f"Role history fetch failed: {role_history.status_code}, {role_history.text}")

    role_history_data = role_history.json()
    for key in ["role_id", "role_name", "history", "category_trends"]:
        assert_key(role_history_data, key)

    print("Smoke test passed: auth, roles, interview, evaluation, dashboard")


if __name__ == "__main__":
    main()
