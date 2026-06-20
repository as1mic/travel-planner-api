from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Place, Project


MAX_PLACES_PER_PROJECT = 10


def get_project_or_404(project_id: int, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def get_place_or_404(project_id: int, place_id: int, db: Session) -> Place:
    place = db.query(Place).filter(Place.project_id == project_id, Place.id == place_id).first()
    if place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    return place


def ensure_project_can_be_deleted(project_id: int, db: Session) -> None:
    visited_place_exists = (
        db.query(Place)
        .filter(Place.project_id == project_id, Place.visited.is_(True))
        .first()
    )
    if visited_place_exists is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a project with visited places",
        )


def ensure_project_has_capacity(project_id: int, db: Session) -> None:
    places_count = db.query(Place).filter(Place.project_id == project_id).count()
    if places_count >= MAX_PLACES_PER_PROJECT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A project cannot have more than 10 places",
        )


def ensure_places_limit(places_count: int) -> None:
    if places_count > MAX_PLACES_PER_PROJECT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A project cannot have more than 10 places",
        )


def ensure_place_is_unique(project_id: int, external_place_id: str, db: Session) -> None:
    duplicate_place = (
        db.query(Place)
        .filter(
            Place.project_id == project_id,
            Place.external_place_id == external_place_id,
        )
        .first()
    )
    if duplicate_place is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This external place already exists in the project",
        )


def ensure_external_places_are_unique(external_place_ids: list[str]) -> None:
    if len(external_place_ids) != len(set(external_place_ids)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A project cannot contain duplicate external places",
        )


def update_project_completion(project: Project) -> None:
    if not project.places:
        project.is_completed = False
        return

    project.is_completed = all(place.visited for place in project.places)
