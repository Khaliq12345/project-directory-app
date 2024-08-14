
from cloudscraper import create_scraper
import model
from selectolax.parser import HTMLParser
import helper as helper
import json

base_url = 'https://mapafrica.afdb.org/api/v11/activities'

params = {
    'status': '1,2',
    'lang': 'en',
    'per_page': '100',
    'page': '0',
    'ascending': 'false',
    'order_by': 'activity_date_planned_start',
}

def mapafrica_parser(json_data, db: list):
    for x in json_data['results']:
        title = x.get('title')
        country = x.get('country')
        status = x.get('activity_status')
        date = x.get('activity_date_planned_start')
        if status == '1':
            status = 'Approved'
        elif status == '2':
            status = 'Ongoing'
        sectors = x.get('sector_group_en')
        p_id = x.get('iati_identifier')
        project_url = f'https://mapafrica.afdb.org/en/projects/{p_id}' if p_id else None
        project_data = {
            'title': title,
            'countries': country,
            'status': status,
            'sectors': sectors,
            'project_url': project_url,
            'directory': 'MapAfrica Afdb.org',
            'date': date,
        }
        project_model = model.Project(**project_data)
        db.append(json.loads(project_model.model_dump_json()))

def start(db: list):
    num = 1
    session = create_scraper()
    while True:
        print(f'Page: {num}')
        params['page'] = num
        response = session.get(base_url, params=params)
        json_data = response.json()
        if len(json_data['results']) > 0:
            mapafrica_parser(json_data, db)
        else:
            break
        num += 1
            
def main():
    db = helper.DB()
    start(db.projects)
    return db.projects