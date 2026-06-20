from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Place, Project
from app.schemas import ProjectCreate, ProjectDetailResponse, ProjectResponse, ProjectUpdate
from app.services.artic_client import ArticAPIError, get_artwork_by_id
from app.services.project_rules import (
    ensure_external_places_are_unique,
    ensure_places_limit,
    ensure_project_can_be_deleted,
    get_project_or_404,
    update_project_completion,
)


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectDetailResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        name=project_data.name,
        description=project_data.description,
        start_date=project_data.start_date,
    )

    places_to_create = project_data.places or []
    ensure_places_limit(len(places_to_create))
    ensure_external_places_are_unique([place.external_place_id for place in places_to_create])

    db.add(project)

    for place_data in places_to_create:
        try:
            artwork = get_artwork_by_id(place_data.external_place_id)
        except ArticAPIError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Art Institute of Chicago API is unavailable",
            )

        if artwork is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="External place was not found in the Art Institute of Chicago API",
            )

        place = Place(
            external_place_id=str(artwork["id"]),
            title=artwork["title"],
            notes=place_data.notes,
            project=project,
        )
        db.add(place)

    update_project_completion(project)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A project cannot contain duplicate external places",
        )

    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return get_project_or_404(project_id, db)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(project_id, db)

    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = get_project_or_404(project_id, db)
    ensure_project_can_be_deleted(project_id, db)

    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
