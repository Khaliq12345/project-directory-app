from sqlalchemy import create_engine
from app_model import Base
import os, pathlib, sys
current_dir = os.getcwd()
dir_to_add = pathlib.Path(current_dir).parent.as_posix()
sys.path.append(dir_to_add)
sys.path.append(f'{current_dir}/app')
import config

engine = create_engine(config.connection_string)
Base.metadata.create_all(engine)