from pydantic import BaseModel

class Project(BaseModel):
    title: str | None = None
    status: str | None = None
    countries: str | None = None
    sectors: str | None = None
    project_url: str | None = None
    directory: str