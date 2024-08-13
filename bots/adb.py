from cloudscraper import create_scraper
import model
from selectolax.parser import HTMLParser
import helper as helper
import json

def adb_parser(soup: HTMLParser, db: list):
    cards = soup.css('.list .item')
    for card in cards:
        title = card.css_first('.item-title')
        if title:
            title = title.text(strip=True)
        project_url = card.css_first('.item-title a')
        if project_url:
            project_url = project_url.attributes['href']
            project_url = f'https://www.adb.org{project_url}'
        summary = card.css_first('.item-summary')
        if summary:
            summary = summary.text(strip=True)
            match summary.split(';'):
                case [p_id, country, sector]:
                    country, sectors = country.strip(), sector.strip()
                case [p_id, country]:
                    country, sectors = country.strip(), None
                case [p_id]:
                    country, sectors = None, None
                case [_]:
                    country, sectors = None, None
        project_data = {
            'title': title,
            'project_url': project_url,
            'sectors': sectors,
            'countries': country,
            'directory': 'Adb.fr'
        }
        project_model = model.Project(**project_data)
        db.append(json.loads(project_model.model_dump_json()))
        
def start(db: list):
    num = 0
    session = create_scraper()
    while True:
        print(f'Page: {num}')
        p_url = f'https://www.adb.org/projects/status/proposed-1360/status/approved-1359?page={num}'
        response = session.get(p_url)
        soup = HTMLParser(response.text)
        print(response.status_code)
        if response.status_code == 200:
            soup = HTMLParser(response.text)
            cards = soup.css('.list .item')
            if len(cards) > 0:
                adb_parser(soup, db)
            else:
                break
        else:
            break
        num += 1

def main():
    db = helper.DB()
    start(db.projects)
    return db.projects
    