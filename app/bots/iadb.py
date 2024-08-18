import model
import helper as helper
import pandas as pd
import json
from selectolax.parser import HTMLParser
from cloudscraper import create_scraper

def iadb_parser(soup: HTMLParser, db: list):
    table = soup.css_first('table')
    rows = table.css('tr')[1:]
    for row in rows:
        title = row.css_first('.views-field.views-field-title')
        if title:
            title = title.text(strip=True)
            project_url = row.css_first('.views-field.views-field-title a')
            if project_url:
                project_url = project_url.attributes['href']
            project_url = f'https://www.iadb.org{project_url}'
            sectors = row.css_first('.views-field.views-field-project-sector-name')
            if sectors:
                sectors = sectors.text(strip=True)
            country = row.css_first('.views-field.views-field-country-name-content')
            if country:
                country = country.text(strip=True)
            date = row.css_first('.views-field.views-field-field-approval-date')
            if date:
                date = date.text(strip=True)
                date = date if len(date) > 5 else None
            project_data = {
                'title': title,
                'countries': country,
                'status': 'Preparation',
                'project_url': project_url,
                'directory': 'Iadb.org',
                'date': date
            }
            project_model = model.Project(**project_data)
            db.append(json.loads(project_model.model_dump_json()))

def start(db: list):
    url = "https://www.iadb.org/en/project-search?query=&f_project_number=&f_operation_number=&f_sector=&f_country_name=&f_project_status=Implementation&f_from=&f_to=&f_approval_date=-30+days&page=1"
    num = 0
    while True:
        print(f'Page: {num}')
        session = create_scraper()
        response = session.get(url)
        print(f'Response - status code: {response.status_code}')
        soup = HTMLParser(response.text)
        checker = soup.css_first('table').css('tr')[1].css_first('.views-field.views-field-title')
        if checker:
            iadb_parser(soup, db)
        else:
            break
        url = url.replace(f'page={num}', f'page={num+1}')
        num += 1
        
def main():
    db = helper.DB()
    start(db.projects)
    return db.projects
    

