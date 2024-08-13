import model
import helper as helper
import json
import httpx
from selectolax.parser import HTMLParser

def afd_parser(soup, db: list):
    cards = soup.css('.ctsearch-result-item')
    for card in cards:
        title = card.css_first('h3')
        if title:
            title = title.text(strip=True)
        project_url = card.css_first('h3 a')
        if project_url:
            project_url = project_url.attributes['href']
            project_url = f'https://www.afd.fr{project_url}'
        country = card.css_first('.ctsearch-result-item-country')
        if country:
            country = country.text(strip=True)
        sectors = card.css_first('.ctsearch-result-item-thematic')
        if sectors:
            sectors = sectors.text(strip=True)
        funding = card.css_first('.ctsearch-result-item-funding-type')
        if funding:
            funding = funding.text(strip=True)
        project_data = {
            'title': title,
            'project_url': project_url,
            'sectors': sectors,
            'countries': country,
            'directory': 'Afd.fr'
        }
        project_model = model.Project(**project_data)
        db.append(json.loads(project_model.model_dump_json()))
        
def start(db: list):
    num = 0
    while True:
        print(f'Page: {num}')
        response = httpx.get(f'https://www.afd.fr/en/carte-des-projets-list?page={num}', timeout=None)
        soup = HTMLParser(response.text, 'lxml')
        cards = soup.css('.ctsearch-result-item')
        if len(cards) > 0:
            afd_parser(soup, db)
        else:
            break
        num += 1

def main():
    db = helper.DB()
    start(db.projects)
    return db.projects