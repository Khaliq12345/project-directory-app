import os, pathlib, sys
current_dir = os.getcwd()
dir_to_add = pathlib.Path(current_dir).parent.as_posix()
sys.path.append(dir_to_add)
sys.path.append(f'{current_dir}/pages')
sys.path.append(f'{current_dir}/bots')
sys.path.append(f'{dir_to_add}/app')

import frontend
from fastapi import FastAPI

app = FastAPI()

@app.get('/admin')
def read_root():
    return "This is the admin page"

frontend.init(app)