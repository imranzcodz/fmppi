from app.services.user_service import create_user


def admin_client(client, db, role="admin"):
    user = create_user(db, email=f"{role}@example.com", password="Secret1234", role=role)
    login_resp = client.post("/auth/login", json={"email": f"{role}@example.com", "password": "Secret1234"})
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"], user


def test_list_users_admin(client, db):
    token, _ = admin_client(client, db)
    resp = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)


def test_create_user_admin(client, db):
    token, _ = admin_client(client, db)
    resp = client.post(
        "/users",
        json={"email": "newuser@example.com", "password": "Secret1234", "role": "reviewer", "is_active": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["role"] == "reviewer"


def test_get_user_admin(client, db):
    token, user = admin_client(client, db)
    resp = client.get(f"/users/{user.id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == user.id


def test_update_user_admin(client, db):
    token, user = admin_client(client, db)
    resp = client.put(
        f"/users/{user.id}",
        json={"role": "investigator", "is_active": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["role"] == "investigator"


def test_delete_user_admin(client, db):
    token, user = admin_client(client, db)
    # create another user to delete
    target = create_user(db, email="todelete@example.com", password="Secret1234", role="reporter")
    resp = client.delete(f"/users/{target.id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text


def test_cannot_delete_self(client, db):
    token, user = admin_client(client, db)
    resp = client.delete(f"/users/{user.id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400, resp.text


def test_users_forbidden_non_admin(client, db):
    token, _ = admin_client(client, db, role="reporter")
    resp = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403, resp.text


def test_users_unauthenticated(client):
    resp = client.get("/users")
    assert resp.status_code == 401, resp.text
