from fastapi import FastAPI

from app.database import engine, Base
from app.models import Project, Place
from app.routers.places import router as places_router
from app.routers.projects import router as projects_router


app = FastAPI(
    title="Travel Planner API",
    version="1.0.0",
    description="API for managing travel projects and project places.",
)

Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Travel Planner API is running"}


app.include_router(projects_router)
app.include_router(places_router)
