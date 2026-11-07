from app.services.user_service import create_user


def headers_for(client, db, role, email=None, permission_role=None):
    email = email or f"{role}@example.com"
    create_user(db, email=email, password="Secret1234", role=role)
    login_resp = client.post("/auth/login", json={"email": email, "password": "Secret1234"})
    assert login_resp.status_code == 200, login_resp.text
    return {"Authorization": f"Bearer {login_resp.json()['access_token']}"}


def test_verify_local(client, db):
    headers = headers_for(client, db, "investigator")
    resp = client.post(
        "/verify/local",
        files={"file": ("face.jpg", b"\x89PNG fakeface", "image/jpeg")},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    assert "matches" in resp.json()


def test_verify_global(client, db):
    headers = headers_for(client, db, "investigator")
    resp = client.post(
        "/verify/global",
        files={"file": ("face.jpg", b"\x89PNG fakeface", "image/jpeg")},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text


def test_verify_kinship(client, db):
    headers = headers_for(client, db, "investigator")
    resp = client.post(
        "/verify/kinship",
        files={"file_a": ("a.jpg", b"\x89PNG facea", "image/jpeg"), "file_b": ("b.jpg", b"\x89PNG faceb", "image/jpeg")},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "score" in data
    assert "is_kin" in data
    assert "confidence" in data


def test_verify_local_forbidden_reporter(client, db):
    headers = headers_for(client, db, "reporter")
    resp = client.post(
        "/verify/local",
        files={"file": ("face.jpg", b"\x89PNG fakeface", "image/jpeg")},
        headers=headers,
    )
    assert resp.status_code == 403, resp.text


def test_ml_endpoints(client, db):
    headers = headers_for(client, db, "investigator")
    for path in ["/ml/detect", "/ml/embed", "/ml/search"]:
        resp = client.post(path, files={"file": ("face.jpg", b"\x89PNG fake", "image/jpeg")}, headers=headers)
        assert resp.status_code == 200, f"{path}: {resp.text}"
    resp = client.post(
        "/ml/verify",
        files={"file_a": ("a.jpg", b"\x89PNG a", "image/jpeg"), "file_b": ("b.jpg", b"\x89PNG b", "image/jpeg")},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text


def test_empty_file_rejected(client, db):
    headers = headers_for(client, db, "investigator")
    resp = client.post(
        "/verify/local",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
        headers=headers,
    )
    assert resp.status_code == 400, resp.text
