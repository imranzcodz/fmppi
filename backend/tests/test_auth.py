def test_admin_only_endpoint(make_client):
    assert make_client("admin").get("/rbac/admin-only").status_code == 200
    assert make_client("reporter").get("/rbac/admin-only").status_code == 403


def test_investigator_or_above(make_client):
    assert make_client("investigator").get("/rbac/investigator-or-above").status_code == 200
    assert make_client("admin").get("/rbac/investigator-or-above").status_code == 200
    assert make_client("reporter").get("/rbac/investigator-or-above").status_code == 403


def test_reporter_only(make_client):
    assert make_client("reporter").get("/rbac/reporter-only").status_code == 200
    assert make_client("admin").get("/rbac/reporter-only").status_code == 403


def test_verify_match(make_client):
    client = make_client("admin")
    assert client.post(
        "/verify", json={"probe_image": "a.jpg", "gallery_image": "a.jpg"}
    ).json() == {"match": True, "confidence": 1.0}
    assert client.post(
        "/verify", json={"probe_image": "a.jpg", "gallery_image": "b.jpg"}
    ).json() == {"match": False, "confidence": 0.0}
