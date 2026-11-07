from app.services.user_service import create_user


def test_register_reporter(client):
    resp = client.post(
        "/auth/register",
        json={"email": "reporter@example.com", "password": "Secret1234", "role": "reporter"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["email"] == "reporter@example.com"
    assert data["role"] == "reporter"
    assert data["is_active"] is True


def test_register_duplicate_email(client):
    client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "Secret1234", "role": "reporter"},
    )
    resp = client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "Secret1234", "role": "reporter"},
    )
    assert resp.status_code == 409, resp.text


def test_register_password_too_short(client):
    resp = client.post(
        "/auth/register",
        json={"email": "short@example.com", "password": "short", "role": "reporter"},
    )
    assert resp.status_code == 422, resp.text


def test_login_success(client, db):
    create_user(db, email="login@example.com", password="Secret1234", role="reporter")
    resp = client.post("/auth/login", json={"email": "login@example.com", "password": "Secret1234"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, db):
    create_user(db, email="pw@example.com", password="Secret1234", role="reporter")
    resp = client.post("/auth/login", json={"email": "pw@example.com", "password": "Wrong1234"})
    assert resp.status_code == 401, resp.text


def test_login_unknown_user(client):
    resp = client.post("/auth/login", json={"email": "nope@example.com", "password": "Secret1234"})
    assert resp.status_code == 401, resp.text


def test_refresh_token(client, db):
    create_user(db, email="ref@example.com", password="Secret1234", role="reporter")
    login_resp = client.post("/auth/login", json={"email": "ref@example.com", "password": "Secret1234"})
    refresh_token = login_resp.json()["refresh_token"]
    resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200, resp.text
    assert "access_token" in resp.json()


def test_refresh_invalid_token(client):
    resp = client.post("/auth/refresh", json={"refresh_token": "not.a.valid.token"})
    assert resp.status_code == 401, resp.text


def test_mfa_setup_and_verify(client, db):
    create_user(db, email="mfa@example.com", password="Secret1234", role="reporter")
    # login then setup
    login_resp = client.post("/auth/login", json={"email": "mfa@example.com", "password": "Secret1234"})
    token = login_resp.json()["access_token"]
    resp = client.post("/auth/mfa/setup", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    secret = resp.json()["secret"]
    assert resp.json()["provisioning_url"]

    import pyotp

    code = pyotp.TOTP(secret).now()
    verify_resp = client.post(
        "/auth/mfa/verify", json={"email": "mfa@example.com", "code": code}
    )
    assert verify_resp.status_code == 200, verify_resp.text
    assert "access_token" in verify_resp.json()


def test_mfa_verify_invalid_code(client, db):
    create_user(db, email="mfa2@example.com", password="Secret1234", role="reporter")
    login_resp = client.post("/auth/login", json={"email": "mfa2@example.com", "password": "Secret1234"})
    token = login_resp.json()["access_token"]
    client.post("/auth/mfa/setup", headers={"Authorization": f"Bearer {token}"})
    resp = client.post("/auth/mfa/verify", json={"email": "mfa2@example.com", "code": "000000"})
    assert resp.status_code == 401, resp.text


def test_me(client, db):
    user = create_user(db, email="me@example.com", password="Secret1234", role="reporter")
    login_resp = client.post("/auth/login", json={"email": "me@example.com", "password": "Secret1234"})
    token = login_resp.json()["access_token"]
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == user.id


def test_me_unauthenticated(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401, resp.text
