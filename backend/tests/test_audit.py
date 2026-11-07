from app.services.user_service import create_user


def headers_for(client, db, role="admin", email=None):
    email = email or f"{role}@example.com"
    create_user(db, email=email, password="Secret1234", role=role)
    login_resp = client.post("/auth/login", json={"email": email, "password": "Secret1234"})
    assert login_resp.status_code == 200, login_resp.text
    return {"Authorization": f"Bearer {login_resp.json()['access_token']}"}


def test_audit_list_admin(client, db):
    headers = headers_for(client, db, "admin")
    resp = client.get("/audit", headers=headers)
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)


def test_audit_filters(client, db):
    headers = headers_for(client, db, "admin")
    resp = client.get("/audit?case_id=1&actor_id=1", headers=headers)
    assert resp.status_code == 200, resp.text


def test_audit_forbidden_non_admin(client, db):
    headers = headers_for(client, db, "reporter")
    resp = client.get("/audit", headers=headers)
    assert resp.status_code == 403, resp.text
