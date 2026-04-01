import pytest
from tests.conftest import auth

RECORD_PAYLOAD = {
    "amount": 1000.0,
    "type": "income",
    "category": "Salary",
    "date": "2024-06-01",
    "notes": "Test record",
}


def test_login_success(client, admin_user):
    resp = client.post("/auth/login", json={"email": "testadmin@example.com", "password": "adminpass"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client, admin_user):
    resp = client.post("/auth/login", json={"email": "testadmin@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post("/auth/login", json={"email": "nobody@example.com", "password": "x"})
    assert resp.status_code == 401


def test_me(client, admin_token):
    resp = client.get("/auth/me", headers=auth(admin_token))
    assert resp.status_code == 200
    assert resp.json()["email"] == "testadmin@example.com"


def test_me_no_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_change_password_success(client, admin_token, admin_user):
    resp = client.patch(
        "/auth/me/password",
        json={"current_password": "adminpass", "new_password": "newpass456"},
        headers=auth(admin_token),
    )
    assert resp.status_code == 204
    resp = client.post("/auth/login", json={"email": "testadmin@example.com", "password": "newpass456"})
    assert resp.status_code == 200


def test_change_password_wrong_current(client, admin_token, admin_user):
    resp = client.patch(
        "/auth/me/password",
        json={"current_password": "wrongpass", "new_password": "newpass456"},
        headers=auth(admin_token),
    )
    assert resp.status_code == 400


def test_create_record(client, admin_token):
    resp = client.post("/records", json=RECORD_PAYLOAD, headers=auth(admin_token))
    assert resp.status_code == 201
    data = resp.json()
    assert data["amount"] == 1000.0
    assert data["category"] == "Salary"
    assert "created_at" in data


def test_get_records(client, admin_token):
    resp = client.get("/records", headers=auth(admin_token))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_single_record(client, admin_token):
    create = client.post("/records", json=RECORD_PAYLOAD, headers=auth(admin_token))
    record_id = create.json()["id"]
    resp = client.get(f"/records/{record_id}", headers=auth(admin_token))
    assert resp.status_code == 200
    assert resp.json()["id"] == record_id


def test_update_record(client, admin_token):
    create = client.post("/records", json=RECORD_PAYLOAD, headers=auth(admin_token))
    record_id = create.json()["id"]
    resp = client.patch(f"/records/{record_id}", json={"amount": 2000.0}, headers=auth(admin_token))
    assert resp.status_code == 200
    assert resp.json()["amount"] == 2000.0


def test_soft_delete_record(client, admin_token):
    create = client.post("/records", json=RECORD_PAYLOAD, headers=auth(admin_token))
    record_id = create.json()["id"]
    resp = client.delete(f"/records/{record_id}", headers=auth(admin_token))
    assert resp.status_code == 204
    resp = client.get(f"/records/{record_id}", headers=auth(admin_token))
    assert resp.status_code == 404


def test_get_record_not_found(client, admin_token):
    resp = client.get("/records/99999", headers=auth(admin_token))
    assert resp.status_code == 404


def test_filter_by_type(client, admin_token):
    client.post("/records", json={**RECORD_PAYLOAD, "type": "expense", "category": "Rent"}, headers=auth(admin_token))
    resp = client.get("/records?type=expense", headers=auth(admin_token))
    assert resp.status_code == 200
    assert all(r["type"] == "expense" for r in resp.json())


def test_filter_by_category_partial(client, admin_token):
    client.post("/records", json={**RECORD_PAYLOAD, "category": "Groceries"}, headers=auth(admin_token))
    resp = client.get("/records?category=groc", headers=auth(admin_token))
    assert resp.status_code == 200
    assert all("groc" in r["category"].lower() for r in resp.json())


def test_create_record_negative_amount(client, admin_token):
    resp = client.post("/records", json={**RECORD_PAYLOAD, "amount": -100}, headers=auth(admin_token))
    assert resp.status_code == 422


def test_create_record_missing_field(client, admin_token):
    resp = client.post("/records", json={"amount": 100, "type": "income"}, headers=auth(admin_token))
    assert resp.status_code == 422


def test_viewer_cannot_create_record(client, viewer_token):
    resp = client.post("/records", json=RECORD_PAYLOAD, headers=auth(viewer_token))
    assert resp.status_code == 403


def test_viewer_cannot_delete_record(client, admin_token, viewer_token):
    create = client.post("/records", json=RECORD_PAYLOAD, headers=auth(admin_token))
    record_id = create.json()["id"]
    resp = client.delete(f"/records/{record_id}", headers=auth(viewer_token))
    assert resp.status_code == 403


def test_viewer_can_read_records(client, viewer_token):
    resp = client.get("/records", headers=auth(viewer_token))
    assert resp.status_code == 200


def test_viewer_cannot_access_dashboard(client, viewer_token):
    resp = client.get("/dashboard/summary", headers=auth(viewer_token))
    assert resp.status_code == 403


def test_viewer_cannot_access_weekly_trends(client, viewer_token):
    resp = client.get("/dashboard/weekly", headers=auth(viewer_token))
    assert resp.status_code == 403


def test_unauthenticated_cannot_access_records(client):
    resp = client.get("/records")
    assert resp.status_code == 401


def test_analyst_can_read_records(client, analyst_token):
    resp = client.get("/records", headers=auth(analyst_token))
    assert resp.status_code == 200


def test_analyst_cannot_create_record(client, analyst_token):
    resp = client.post("/records", json=RECORD_PAYLOAD, headers=auth(analyst_token))
    assert resp.status_code == 403


def test_analyst_can_access_dashboard(client, analyst_token):
    resp = client.get("/dashboard/summary", headers=auth(analyst_token))
    assert resp.status_code == 200


def test_analyst_can_access_weekly_trends(client, analyst_token):
    resp = client.get("/dashboard/weekly", headers=auth(analyst_token))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_admin_can_register_user(client, admin_token):
    resp = client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "full_name": "New User", "password": "pass123", "role": "analyst"},
        headers=auth(admin_token),
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "analyst"


def test_duplicate_email_rejected(client, admin_token, admin_user):
    resp = client.post(
        "/auth/register",
        json={"email": "testadmin@example.com", "full_name": "Dup", "password": "pass123", "role": "viewer"},
        headers=auth(admin_token),
    )
    assert resp.status_code == 409


def test_viewer_cannot_register_user(client, viewer_token):
    resp = client.post(
        "/auth/register",
        json={"email": "another@example.com", "full_name": "X", "password": "pass123", "role": "viewer"},
        headers=auth(viewer_token),
    )
    assert resp.status_code == 403
