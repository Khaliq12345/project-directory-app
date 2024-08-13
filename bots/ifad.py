from cloudscraper import create_scraper
import model
from selectolax.parser import HTMLParser
import helper as helper
import json

def ifad_parser(soup, db:list):
    cards = soup.css('.col-md.table-row.row')
    for card in cards:
        title = card.css_first('.col-md-5.title')
        if title:
            title = title.text(strip=True)
        project_url = card.css_first('a')
        if project_url:
            project_url = project_url.attributes['href']
        country = card.css_first('.col-md-3')
        if country:
            country = country.text(strip=True)
        date = card.css('.col-md-2')[-1]
        if date:
            date = date.text(strip=True)
            if len(date) == 0:
                project_data = {
                    'title': title,
                    'countries': country,
                    'status': 'Planning',
                    'project_url': project_url,
                    'directory': 'Ifad.org'
                }
                project_model = model.Project(**project_data)
                db.append(json.loads(project_model.model_dump_json()))
                         
def start(db: list):
    session = create_scraper()
    response = session.get('https://www.ifad.org/en/web/operations/projects-and-programmes')
    soup = HTMLParser(response.text)
    print(response.status_code)
    if response.status_code == 200:
        soup = HTMLParser(response.text)
        ifad_parser(soup, db)

def main():
    db = helper.DB()
    start(db.projects)
    return db.projects