import httpx
import model
from selectolax.parser import HTMLParser
import helper as helper
import json

def opec_parser(soup: HTMLParser, db: list):
    cards = soup.css('.list-item')
    for card in cards:
        title = card.css_first('h4').text()
        status, sector, country, date = None, None, None, None
        for x in card.css('.line'):
            if 'Status' in x.text():
                status = x.text(strip=True).replace('Status', '')
            if 'Focus Area' in x.text():
                sector = x.text(strip=True).replace('Focus Area', '')
            if 'Country' in x.text():
                country = x.text(strip=True).replace('Country', '')
            if 'Approved' in x.text():
                date = x.text(strip=True).replace('Approved', '')
        project_data = {
            'title': title,
            'status': status,
            'countries': country,
            'sectors': sector,
            'directory': 'Opec',
            'date': date
        }
        project_model = model.Project(**project_data)
        db.append(json.loads(project_model.model_dump_json()))
        
def start(db: list):
    num = 1
    while True:
        print(f'Page: {num}')
        url = f"https://opecfund.org/operations/search-operations?action=search_operations&search_operations%5Bsort%5D=default&search_operations%5Bfocus_area%5D=0&search_operations%5Bcountry_region%5D=&search_operations%5Bkeyword%5D=&search_operations%5Bfinancing_type%5D=0&search_operations%5Bstate%5D=45146&search_operations%5Bdate_from%5D=&search_operations%5Bdate_to%5D=&search_operations%5Bamount%5D=0%2C180&search_operations%5Btotal_cost%5D=0%2C13074&page={num}"
        response = httpx.get(url)
        soup = HTMLParser(response.text)
        print(response.status_code)
        if response.status_code == 200:
            soup = HTMLParser(response.text)
            cards = soup.css('.list-item')
            print(len(cards))
            if len(cards) > 0:
                opec_parser(soup, db)
            else:
                break
        else:
            break
                
        num += 1

def main():
    db = helper.DB()
    start(db.projects)
    return db.projects