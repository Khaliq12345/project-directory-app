import model
from dateparser import parse
import helper as helper
import json
import httpx

base_url = 'https://www.eib.org/provider-eib-plr/app/pipelines/list'

params = {
    'search': '',
    'sortColumn': 'releaseDate',
    'sortDir': 'desc',
    'pageNumber': '0',
    'itemPerPage': '100',
    'pageable': 'true',
    'language': 'EN',
    'defaultLanguage': 'EN',
    'recentlySigned': 'true',
    'orrecentlySigned': 'true',
    'yearFrom': '',
    'yearTo': '',
    'orCountries.region': 'true',
    'orCountries': 'true',
    'orSectors': 'true',
    'orStatus': 'true',
    'status': [
        'approved',
        'signed',
    ],
}

def eib_data_parser(dt, db: list):
    status = helper.key_checker(dt['additionalInformation'][0], dt)
    countries = helper.key_checker([tag['label'] for tag in dt['primaryTags'] if tag['subType'] == 'countries'], dt)
    countries = '; '.join(countries)
    sectors = helper.key_checker([tag['label'] for tag in dt['primaryTags'] if tag['subType'] == 'sectors'], dt)
    sectors = '; '.join(sectors)
    title = helper.key_checker(dt['title'], dt)
    release_date = helper.key_checker(dt['startDate'], dt)
    release_date = parse(str(release_date)).strftime("%y-%m-%d") if release_date else None 
    project_id = helper.key_checker(dt['id'], dt)
    project_url = f'https://www.eib.org/en/projects/pipelines/all/{project_id}'
    project_data = {
        'status': status,
        'countries': countries,
        'sectors': sectors,
        'title': title,
        'project_url': project_url,
        'directory': 'Eib.org'
    }
    project_model = model.Project(**project_data)
    db.append(json.loads(project_model.model_dump_json()))

def start(db: list):
    num = 0
    while True:
        print(f'Page: {num}')
        params['pageNumber'] = num
        response = httpx.get(base_url, params=params)
        json_data = response.json()
        if len(json_data['data']) > 0:
            for jt in json_data['data']:
                eib_data_parser(jt, db)
        else:
            break
        num += 1
            
def main():
    db = helper.DB()
    start(db.projects)
    return db.projects