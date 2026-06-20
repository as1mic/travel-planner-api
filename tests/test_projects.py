from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.routers import places as places_router


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_travel_planner.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_create_project():
    response = client.post(
        "/projects",
        json={
            "name": "Paris Trip",
            "description": "Museums and galleries",
            "start_date": "2026-07-01",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] > 0
    assert data["name"] == "Paris Trip"
    assert data["description"] == "Museums and galleries"
    assert data["start_date"] == "2026-07-01"
    assert data["is_completed"] is False
    assert data["places"] == []


def test_get_projects_list():
    create_response = client.post(
        "/projects",
        json={
            "name": "New York Trip",
            "description": "Art and culture",
            "start_date": "2026-08-15",
        },
    )
    assert create_response.status_code == 201

    response = client.get("/projects")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] > 0
    assert data[0]["name"] == "New York Trip"
    assert data[0]["description"] == "Art and culture"
    assert data[0]["start_date"] == "2026-08-15"
    assert data[0]["is_completed"] is False


def test_get_project_detail():
    create_response = client.post(
        "/projects",
        json={
            "name": "Tokyo Trip",
            "description": "Temples and gardens",
            "start_date": "2026-09-10",
        },
    )
    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Tokyo Trip"
    assert data["description"] == "Temples and gardens"
    assert data["start_date"] == "2026-09-10"
    assert data["is_completed"] is False
    assert data["places"] == []


def test_cannot_delete_project_with_visited_places():
    original_get_artwork_by_id = places_router.get_artwork_by_id
    places_router.get_artwork_by_id = lambda external_place_id: {
        "id": external_place_id,
        "title": "Test Artwork",
    }

    create_response = client.post(
        "/projects",
        json={
            "name": "London Trip",
            "description": "Historical sites",
            "start_date": "2026-10-05",
        },
    )
    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    place_response = client.post(
        f"/projects/{project_id}/places",
        json={
            "external_place_id": "12345",
            "notes": "Must visit the museum",
        },
    )
    assert place_response.status_code == 201

    place_id = place_response.json()["id"]

    try:
        update_place_response = client.patch(
            f"/projects/{project_id}/places/{place_id}",
            json={"visited": True},
        )
        assert update_place_response.status_code == 200

        delete_project_response = client.delete(f"/projects/{project_id}")
        assert delete_project_response.status_code == 400
        assert delete_project_response.json()["detail"] == "Cannot delete a project with visited places"
    finally:
        places_router.get_artwork_by_id = original_get_artwork_by_id


def test_project_is_completed_when_all_places_are_visited():
    original_get_artwork_by_id = places_router.get_artwork_by_id
    places_router.get_artwork_by_id = lambda external_place_id: {
        "id": external_place_id,
        "title": "Test Artwork",
    }

    try:
        create_response = client.post(
            "/projects",
            json={
                "name": "Rome Trip",
                "description": "Ancient landmarks",
                "start_date": "2026-11-01",
            },
        )
        assert create_response.status_code == 201

        project_id = create_response.json()["id"]

        first_place_response = client.post(
            f"/projects/{project_id}/places",
            json={
                "external_place_id": "111",
                "notes": "Visit first",
            },
        )
        assert first_place_response.status_code == 201

        second_place_response = client.post(
            f"/projects/{project_id}/places",
            json={
                "external_place_id": "222",
                "notes": "Visit second",
            },
        )
        assert second_place_response.status_code == 201

        first_place_id = first_place_response.json()["id"]
        second_place_id = second_place_response.json()["id"]

        first_update_response = client.patch(
            f"/projects/{project_id}/places/{first_place_id}",
            json={"visited": True},
        )
        assert first_update_response.status_code == 200

        second_update_response = client.patch(
            f"/projects/{project_id}/places/{second_place_id}",
            json={"visited": True},
        )
        assert second_update_response.status_code == 200

        project_response = client.get(f"/projects/{project_id}")
        assert project_response.status_code == 200

        data = project_response.json()
        assert data["is_completed"] is True
        assert len(data["places"]) == 2
    finally:
        places_router.get_artwork_by_id = original_get_artwork_by_id