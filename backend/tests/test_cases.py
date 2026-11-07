def test_create_and_list_case(make_client):
    client = make_client("investigator")
    response = client.post(
        "/cases", json={"case_number": "CASE-001", "title": "Missing person"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["case_number"] == "CASE-001"
    assert data["title"] == "Missing person"
    assert data["status"] == "open"
    assert "id" in data

    response = client.get("/cases")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_case_not_found(make_client):
    client = make_client("reporter")
    response = client.get("/cases/999")
    assert response.status_code == 404


def test_duplicate_case_number_conflict(make_client):
    client = make_client("admin")
    client.post(
        "/cases", json={"case_number": "CASE-DUP", "title": "first"}
    )
    response = client.post(
        "/cases", json={"case_number": "CASE-DUP", "title": "second"}
    )
    assert response.status_code == 409


def test_add_evidence(make_client):
    client = make_client("investigator")
    client.post(
        "/cases", json={"case_number": "CASE-EV", "title": "evidence case"}
    )
    response = client.post(
        "/cases/1/evidences",
        json={"file_name": "img.jpg", "file_type": "image/jpeg", "size_bytes": 1024},
    )
    assert response.status_code == 201
    assert response.json()["file_name"] == "img.jpg"


def test_reporter_cannot_add_evidence(make_client):
    investigator = make_client("investigator")
    investigator.post(
        "/cases", json={"case_number": "CASE-REP", "title": "reporter case"}
    )
    reporter = make_client("reporter")
    response = reporter.post(
        "/cases/1/evidences",
        json={"file_name": "img.jpg", "file_type": "image/jpeg", "size_bytes": 1024},
    )
    assert response.status_code == 403
