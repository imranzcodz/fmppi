from app.services.user_service import create_user


def auth_headers(client, db, role="investigator", email=None):
    email = email or f"{role}@example.com"
    create_user(db, email=email, password="Secret1234", role=role)
    login_resp = client.post("/auth/login", json={"email": email, "password": "Secret1234"})
    assert login_resp.status_code == 200, login_resp.text
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, email


def test_create_case(client, db):
    headers, _ = auth_headers(client, db)
    resp = client.post("/cases", json={"title": "Missing person case", "status": "open"}, headers=headers)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["title"] == "Missing person case"
    assert data["status"] == "open"
    assert "id" in data
    return data


def test_list_cases(client, db):
    headers, _ = auth_headers(client, db)
    client.post("/cases", json={"title": "Case A", "status": "open"}, headers=headers)
    client.post("/cases", json={"title": "Case B", "status": "closed"}, headers=headers)
    resp = client.get("/cases", headers=headers)
    assert resp.status_code == 200, resp.text
    assert len(resp.json()) >= 2


def test_get_case(client, db):
    headers, _ = auth_headers(client, db)
    created = client.post("/cases", json={"title": "Solo", "status": "open"}, headers=headers).json()
    resp = client.get(f"/cases/{created['id']}", headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == created["id"]


def test_update_case(client, db):
    headers, _ = auth_headers(client, db)
    created = client.post("/cases", json={"title": "Old", "status": "open"}, headers=headers).json()
    resp = client.put(f"/cases/{created['id']}", json={"title": "New", "status": "in-progress"}, headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["title"] == "New"
    assert resp.json()["status"] == "in-progress"


def test_delete_case(client, db):
    headers, _ = auth_headers(client, db)
    created = client.post("/cases", json={"title": "Temp", "status": "open"}, headers=headers).json()
    resp = client.delete(f"/cases/{created['id']}", headers=headers)
    assert resp.status_code == 200, resp.text


def test_case_not_found(client, db):
    headers, _ = auth_headers(client, db)
    resp = client.get("/cases/99999", headers=headers)
    assert resp.status_code == 404, resp.text


def test_case_forbidden_reporter(client, db):
    # reporter cannot access cases they did not create
    headers_reporter, reporter_email = auth_headers(client, db, role="reporter")
    headers_admin, _ = auth_headers(client, db, role="admin", email="admin2@example.com")
    created = client.post("/cases", json={"title": "Reporter case", "status": "open"}, headers=headers_reporter).json()
    # admin can access
    resp = client.get(f"/cases/{created['id']}", headers=headers_admin)
    assert resp.status_code == 200, resp.text
    # another reporter cannot
    headers_reporter2, _ = auth_headers(client, db, role="reporter", email="reporter2@example.com")
    resp = client.get(f"/cases/{created['id']}", headers=headers_reporter2)
    assert resp.status_code == 403, resp.text


def test_add_evidence(client, db):
    headers, _ = auth_headers(client, db)
    created = client.post("/cases", json={"title": "Ev case", "status": "open"}, headers=headers).json()
    resp = client.post(
        f"/cases/{created['id']}/evidence",
        files={"file": ("photo.jpg", b"\x89PNG fakeimage", "image/jpeg")},
        data={"type": "photo", "quality_score": 0.9},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["type"] == "photo"
    assert resp.json()["quality_score"] == 0.9


def test_add_evidence_unsupported_type(client, db):
    headers, _ = auth_headers(client, db)
    created = client.post("/cases", json={"title": "Ev case", "status": "open"}, headers=headers).json()
    resp = client.post(
        f"/cases/{created['id']}/evidence",
        files={"file": ("doc.pdf", b"%PDF fake", "application/pdf")},
        data={"type": "photo"},
        headers=headers,
    )
    assert resp.status_code == 400, resp.text


def test_run_match(client, db):
    headers, _ = auth_headers(client, db)
    created = client.post("/cases", json={"title": "Match case", "status": "open"}, headers=headers).json()
    # add evidence first
    ev = client.post(
        f"/cases/{created['id']}/evidence",
        files={"file": ("photo.jpg", b"\x89PNG fake", "image/jpeg")},
        data={"type": "photo"},
        headers=headers,
    ).json()
    resp = client.post(
        f"/cases/{created['id']}/match/run",
        json={"source_evidence_id": ev["id"], "score": 0.87},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["score"] == 0.87


def test_list_matches(client, db):
    headers, _ = auth_headers(client, db)
    created = client.post("/cases", json={"title": "Match case 2", "status": "open"}, headers=headers).json()
    ev = client.post(
        f"/cases/{created['id']}/evidence",
        files={"file": ("photo.jpg", b"\x89PNG fake", "image/jpeg")},
        data={"type": "photo"},
        headers=headers,
    ).json()
    client.post(f"/cases/{created['id']}/match/run", json={"source_evidence_id": ev["id"], "score": 0.5}, headers=headers)
    resp = client.get(f"/cases/{created['id']}/matches", headers=headers)
    assert resp.status_code == 200, resp.text
    assert len(resp.json()) >= 1


def test_reporter_cases_endpoint(client, db):
    headers, reporter_email = auth_headers(client, db, role="reporter")
    created = client.post("/reporter/cases", data={"title": "Reporter case", "status": "open"}, headers=headers)
    assert created.status_code == 201, created.text
    case_id = created.json()["id"]
    resp = client.get(f"/reporter/cases/{case_id}/status", headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == case_id


def test_reporter_upload_evidence(client, db):
    headers, _ = auth_headers(client, db, role="reporter")
    created = client.post("/reporter/cases", data={"title": "Reporter case 2", "status": "open"}, headers=headers).json()
    resp = client.post(
        f"/reporter/cases/{created['id']}/evidence",
        files={"file": ("photo.jpg", b"\x89PNG fake", "image/jpeg")},
        data={"type": "cctv"},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text


def test_reporter_cannot_access_others_case(client, db):
    headers, _ = auth_headers(client, db, role="reporter")
    headers2, _ = auth_headers(client, db, role="reporter", email="reporter3@example.com")
    created = client.post("/reporter/cases", data={"title": "Owned", "status": "open"}, headers=headers).json()
    resp = client.get(f"/reporter/cases/{created['id']}/status", headers=headers2)
    assert resp.status_code == 403, resp.text


def test_reporter_create_case_uses_form(client, db):
    headers, _ = auth_headers(client, db, role="reporter")
    resp = client.post("/reporter/cases", data={"title": "Form case", "status": "open"}, headers=headers)
    assert resp.status_code == 201, resp.text
