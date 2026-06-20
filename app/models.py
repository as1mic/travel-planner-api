from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    start_date = Column(Date)
    is_completed = Column(Boolean, default=False, nullable=False)
    places = relationship(
        "Place",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class Place(Base):
    __tablename__ = "places"
    __table_args__ = (
        UniqueConstraint("project_id", "external_place_id", name="uq_project_external_place"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    external_place_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False, index=True)
    notes = Column(Text)
    visited = Column(Boolean, default=False, nullable=False)
    project = relationship("Project", back_populates="places")
