import adb, afd, caf, eib, iadb, ifad, mapafrica, opec, worldbank
from sqlalchemy import create_engine, DATE
import pandas as pd
import os, pathlib, sys
current_dir = os.getcwd()
dir_to_add = pathlib.Path(current_dir).parent.as_posix()
sys.path.append(dir_to_add)

import config
engine = create_engine(config.connection_string)


def start_scripts(scripts: list[str], all_projects:list):
    for idx, x in enumerate(scripts):
        try:
            x = eval(x)
            name = str(x.__name__)
            print(f'Name: {name}')
            projects = x.main()
            _ = [all_projects.append(p) for p in projects]
        except Exception as e:
            print(f'Error: {e} | Scraper: {name}')
            
def save_data(dataframe: pd.DataFrame):
    dataframe.drop_duplicates(subset=['title'], inplace=True)
    with engine.connect() as con:
        dataframe.to_sql('project', con=con, index=False, if_exists='replace', dtype={'date': DATE})
        print("DONE!")
        
if __name__ == '__main__':
    all_projects = []
    scripts = ['iadb']
    start_scripts(scripts, all_projects)
    df = pd.DataFrame(all_projects)
    save_data(df)