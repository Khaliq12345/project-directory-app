from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy import Text, ARRAY

class Base(DeclarativeBase):
    pass

class Project(Base):
    __tablename__ = 'project'

    title = mapped_column(Text, primary_key=True)
    sectors = mapped_column(Text)
    countries = mapped_column(Text)
    status = mapped_column(Text)
    project_url = mapped_column(Text)
    directory = mapped_column(Text)