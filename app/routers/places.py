from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Place
from app.schemas import PlaceCreate, PlaceResponse, PlaceUpdate
from app.services.artic_client import ArticAPIError, get_artwork_by_id
from app.services.project_rules import (
    ensure_place_is_unique,
    ensure_project_has_capacity,
    get_place_or_404,
    get_project_or_404,
    update_project_completion,
)


router = APIRouter(prefix="/projects/{project_id}/places", tags=["Places"])


@router.post("", response_model=PlaceResponse, status_code=status.HTTP_201_CREATED)
def create_place(project_id: int, place_data: PlaceCreate, db: Session = Depends(get_db)):
    project = get_project_or_404(project_id, db)
    ensure_project_has_capacity(project_id, db)
    ensure_place_is_unique(project_id, place_data.external_place_id, db)

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
            detail="This external place already exists in the project",
        )

    db.refresh(place)
    return place


@router.get("", response_model=list[PlaceResponse])
def list_places(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    return db.query(Place).filter(Place.project_id == project_id).all()


@router.get("/{place_id}", response_model=PlaceResponse)
def get_place(project_id: int, place_id: int, db: Session = Depends(get_db)):
    return get_place_or_404(project_id, place_id, db)


@router.patch("/{place_id}", response_model=PlaceResponse)
def update_place(
    project_id: int,
    place_id: int,
    place_data: PlaceUpdate,
    db: Session = Depends(get_db),
):
    place = get_place_or_404(project_id, place_id, db)

    update_data = place_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(place, field, value)

    update_project_completion(place.project)
    db.commit()
    db.refresh(place)
    return place


@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_place(project_id: int, place_id: int, db: Session = Depends(get_db)):
    place = get_place_or_404(project_id, place_id, db)
    project = place.project

    db.delete(place)
    db.flush()
    update_project_completion(project)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
