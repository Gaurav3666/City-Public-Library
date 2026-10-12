
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/json"
    )



def test_books_endpoint():
    response = client.get("/books/")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "count" in data
    assert "books" in data
    assert isinstance(data["books"], list)
    assert data["count"] == len(data["books"])



def test_member_profile_requires_authentication():
    response = client.get("/members/me")

    assert response.status_code == 401


def test_member_loans_require_authentication():
    response = client.get("/loans/my")

    assert response.status_code == 401


def test_partner_catalogue_requires_api_credentials():
    response = client.get("/partner/books")

    assert response.status_code == 401




def test_member_cannot_access_another_members_loans():
    from app.dependencies import get_current_member

    def fake_member():
        return {
            "member_id": 4,
            "name": "Gaurav",
            "email": "abc@gmail.com",
            "is_active": 1,
        }

    app.dependency_overrides[get_current_member] = fake_member

    try:
        response = client.get("/loans/my")

        assert response.status_code == 200

        data = response.json()
        assert "loans" in data

        for loan in data["loans"]:
            assert loan["member_id"] == 4

    finally:
        app.dependency_overrides.clear()
