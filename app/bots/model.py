from pydantic import BaseModel, model_validator
from dateparser import parse

class Project(BaseModel):
    title: str | None = None
    status: str | None = None
    countries: str | None = None
    sectors: str | None = None
    project_url: str | None = None
    directory: str
    date: str = None
    
    @model_validator(mode='after')
    def validate_the_model(self):
        if self.date:
            self.date = parse(self.date)
            if self.date:
                self.date = self.date.strftime('%Y-%m-%d')