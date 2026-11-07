"""Tests for API endpoints: reporter + audit."""


class TestReporterEndpoints:
    def test_reporter_register_then_create_case(self, client, db):
        # Register reporter
        resp = client.post(
            "/auth/register",
            json={"email": "repapi@example.com", "password": "Secret1234", "role": "reporter"},
        )
        assert resp.status_code == 201

        # Login
        login = client.post(
            "/auth/login",
            json={"email": "repapi@example.com", "password": "Secret1234"},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create case via reporter endpoint
        resp = client.post(
            "/reporter/cases",
            data={"title": "Reporter API case", "status": "open"},
            headers=headers,
        )
        assert resp.status_code == 201, resp.text
        case_id = resp.json()["id"]

        # Get status
        resp = client.get(f"/reporter/cases/{case_id}/status", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == case_id

    def test_reporter_upload_evidence(self, client, db):
        client.post(
            "/auth/register",
            json={"email": "repapi2@example.com", "password": "Secret1234", "role": "reporter"},
        )
        login = client.post(
            "/auth/login",
            json={"email": "repapi2@example.com", "password": "Secret1234"},
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        case = client.post(
            "/reporter/cases",
            data={"title": "Ev case", "status": "open"},
            headers=headers,
        ).json()

        resp = client.post(
            f"/reporter/cases/{case['id']}/evidence",
            files={"file": ("photo.jpg", b"\x89PNG fake", "image/jpeg")},
            data={"type": "cctv", "quality_score": 0.7},
            headers=headers,
        )
        assert resp.status_code == 201, resp.text

    def test_non_reporter_cannot_use_reporter_endpoint(self, client, db):
        from app.services.user_service import create_user

        create_user(db, email="adminapi@example.com", password="Secret1234", role="admin")
        login = client.post(
            "/auth/login",
            json={"email": "adminapi@example.com", "password": "Secret1234"},
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.post(
            "/reporter/cases",
            data={"title": "Should fail", "status": "open"},
            headers=headers,
        )
        assert resp.status_code == 403, resp.text


class TestAuditEndpoint:
    def test_audit_list_requires_admin(self, client, db):
        from app.services.user_service import create_user

        create_user(db, email="auditreporter@example.com", password="Secret1234", role="reporter")
        login = client.post(
            "/auth/login",
            json={"email": "auditreporter@example.com", "password": "Secret1234"},
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/audit", headers=headers)
        assert resp.status_code == 403, resp.text

    def test_audit_list_admin(self, client, db):
        from app.services.user_service import create_user

        create_user(db, email="auditadmin@example.com", password="Secret1234", role="admin")
        login = client.post(
            "/auth/login",
            json={"email": "auditadmin@example.com", "password": "Secret1234"},
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/audit", headers=headers)
        assert resp.status_code == 200, resp.text
        assert isinstance(resp.json(), list)
