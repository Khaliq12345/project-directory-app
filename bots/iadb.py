import model
import helper as helper
import pandas as pd
import json

def table_parser(tbl: pd.DataFrame, db: list):
    tbl = tbl[["Project Number", "Country", "Sector", "Title", "Project Status"]]
    tbl = tbl.rename(columns={
        "Project Number": "project_id",
        "Country": "countries",
        "Sector": "sector",
        "Title": "title",
        "Project Status": "status"
    })
    tbl['project_url'] = tbl['project_id'].map(lambda x: f'https://www.iadb.org/en/project/{x}')
    tbl['directory'] = 'Iadb.org'
    project_data = json.loads(tbl.to_json(orient='records'))
    iadb_parser(project_data, db)

def iadb_parser(jsons, db: list):
    for js in jsons:
        project_model = model.Project(**js)
        db.append(json.loads(project_model.model_dump_json()))

def start(db: list):
    url = "https://www.iadb.org/en/project-search?query=&f_project_number=&f_operation_number=&f_sector=&f_country_name=&f_project_status=&f_from=&f_to=&f_approval_date=-30+days&page=1"
    num = 0
    while True:
        print(f'Page: {num}')
        tables = pd.read_html(url)
        if 'Project Number' in tables[0].columns:
            table_parser(tables[0], db)
        else:
            break
        url = url.replace(f'page={num}', f'page={num+1}')
        num += 1
        
def main():
    db = helper.DB()
    start(db.projects)
    return db.projects
    

