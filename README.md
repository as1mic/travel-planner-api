# Travel Planner API

This project is a small REST API for managing travel projects and places to visit.

It was built as a backend technical assessment using FastAPI, SQLAlchemy, and SQLite.

## Features

- Create, update, list, get, and delete travel projects
- Create a project together with places in one request
- Add places to an existing project
- Update place notes and visited status
- Validate places using the Art Institute of Chicago API
- Automatically mark a project as completed when all places are visited

## Business Rules

- A project can contain up to 10 places
- The same external place cannot be added to the same project more than once
- A project cannot be deleted if it has at least one visited place
- A project is marked as completed when all of its places are visited

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Docker
- Pytest

## Project Structure

```text
app/
  database.py
  main.py
  models.py
  schemas.py
  routers/
    projects.py
    places.py
  services/
    artic_client.py
    project_rules.py
tests/
```

## Run Locally

1. Create and activate a virtual environment
2. Install dependencies
3. Start the application

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at:

- `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

## Run With Docker

```bash
docker compose up --build
```

The API will be available at:

- `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

## Run Tests

```bash
pytest
```

## Main Endpoints

### Projects

- `POST /projects`
- `GET /projects`
- `GET /projects/{project_id}`
- `PATCH /projects/{project_id}`
- `DELETE /projects/{project_id}`

### Places

- `POST /projects/{project_id}/places`
- `GET /projects/{project_id}/places`
- `GET /projects/{project_id}/places/{place_id}`
- `PATCH /projects/{project_id}/places/{place_id}`
- `DELETE /projects/{project_id}/places/{place_id}`

## Example Request

Create a project with places:

```json
{
  "name": "Rome Trip",
  "description": "Art and history",
  "start_date": "2026-08-01",
  "places": [
    {
      "external_place_id": "129884",
      "notes": "Main museum"
    }
  ]
}
```

## Third-Party API

This project uses the Art Institute of Chicago API to validate places before saving them:

- `https://api.artic.edu/docs/#collections`

## Notes

- SQLite is used for simplicity because it is enough for this task
- Swagger UI is available and can be used as API documentation and for manual testing