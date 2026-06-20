from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ProjectPlaceCreate(BaseModel):
    external_place_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="The external identifier of the place",
    )
    notes: str | None = Field(None, max_length=2000, description="Personal notes for the place")


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="The name of the project")
    description: str | None = Field(None, max_length=1000, description="A brief description of the project")
    start_date: date | None = Field(None, description="The planned start date of the project")
    places: list[ProjectPlaceCreate] | None = Field(
        default=None,
        max_length=10,
        description="Optional list of places to create with the project",
    )


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255, description="The name of the project")
    description: str | None = Field(None, max_length=1000, description="A brief description of the project")
    start_date: date | None = Field(None, description="The planned start date of the project")


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="The unique identifier of the project")
    name: str = Field(..., description="The name of the project")
    description: str | None = Field(None, description="A brief description of the project")
    start_date: date | None = Field(None, description="The planned start date of the project")
    is_completed: bool = Field(..., description="Indicates whether the project is completed")

class PlaceCreate(BaseModel):
    external_place_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="The external identifier of the place",
    )
    notes: str | None = Field(None, max_length=2000, description="Personal notes for the place")


class PlaceUpdate(BaseModel):
    notes: str | None = Field(None, max_length=2000, description="Personal notes for the place")
    visited: bool | None = Field(None, description="Indicates whether the place has been visited")


class PlaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="The unique identifier of the place")
    project_id: int = Field(..., description="The ID of the project to which the place belongs")
    external_place_id: str = Field(..., description="The external identifier of the place")
    title: str = Field(..., description="The title of the place")
    notes: str | None = Field(None, description="Personal notes for the place")
    visited: bool = Field(..., description="Indicates whether the place has been visited")


class ProjectDetailResponse(ProjectResponse):
    places: list[PlaceResponse] = Field(default_factory=list, description="Places in the project")
