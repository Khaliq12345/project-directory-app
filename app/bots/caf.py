import model
import helper as helper
import json
import httpx
from selectolax.parser import HTMLParser

def caf_parser(soup: HTMLParser, db: list):
    cards = soup.css('.row.justify-content-center.caf_container_list.my-5')
    for card in cards:
        country = card.css_first('.caf_etiqueta2.caf_color_home_int_3')
        if country:
            country = country.text(strip=True)
        title = card.css_first('.caf_etiqueta1.pr-lg-4 span')
        if title:
            title = title.attributes['title']
        date = card.css_first('p.caf_fechas')
        date = date.text(strip=True).replace('Last update', '').replace(':', '') if date else None
        project_data = {
            'title': title,
            'countries': country,
            'status': 'Approved',
            'directory': 'Caf.com',
            'date': date
        }
        project_model = model.Project(**project_data)
        db.append(json.loads(project_model.model_dump_json()))
        
def start(db: list):
    num = 0
    while True:
        print(f'Page: {num}')
        response = httpx.get(
        f'https://www.caf.com/en/projects/?ps=aprobado&sd=&ed=&sb=fAct&so=desc&reset=false&page={num}')
        soup = HTMLParser(response.text, 'lxml')
        cards = soup.css('.row.justify-content-center.caf_container_list.my-5')
        if len(cards) > 6:
            caf_parser(soup, db)
        else:
            caf_parser(soup, db)
            break
        num += 1

def main():
    db = helper.DB()
    start(db.projects)
    return db.projects