import os, pathlib, sys
current_dir = os.getcwd()
dir_to_add = pathlib.Path(current_dir).parent.as_posix()
sys.path.append(dir_to_add)
#---------------------------------------
from docx import Document
from dateparser import parse
import httpx
import config
from country_named_entity_recognition import find_countries
from iteration_utilities import unique_everseen
from countryguess import guess_country
from dateparser import parse
from datetime import timedelta
import bot_static

tag_dict = {
    'economic_586': [x.strip() for x in bot_static.economic.split(',')],
    'monetary policy_587': [x.strip() for x in bot_static.monetary_policy.split(',')],
    'political_588': [x.strip() for x in bot_static.political.split(',')]
}

def get_tags(text):
    tags = []
    for x in tag_dict:
        for tag_name in tag_dict[x]:
            if tag_name.lower() in text.lower():
                tags.append(x.split('_')[-1])
    tags = list(set(tags))
    return tags

def get_categories():
    print(f'Getting Categories')
    categories = []
    num = 1
    while True:
        print(f'Page: {num}')
        response = httpx.get(
        f'{config.wordpress_host}/wp-json/wp/v2/categories?per_page=100&page={num}', 
        auth=(config.wordress_pswd, config.wordress_pswd))
        json_data = response.json()
        if len(json_data) > 0:
           [categories.append(x) for x in json_data]
        else:
            break
        num += 1
    return categories

def get_country_id(c_name, categories: list):
    c_name = 'The Philippines' if c_name == 'Philippines' else c_name
    c_name = 'The Dominican Republic' if c_name == 'Dominican Republic' else c_name
    c_name = 'Cape Verde' if c_name == 'Cabo Verde' else c_name
    c_name = 'Ivory Coast' if c_name == "Cote d'Ivoire" else c_name
    c_name = 'Turkey' if c_name == 'Türkiye' else c_name
    c_name = 'Bosnia' if c_name == 'Bosnia and Herzegovina' else c_name
    c_name = 'Kyrgyzstan' if c_name == 'Kyrgyz Republic' else c_name
    for x in categories:
        if x['name'].lower() in c_name.lower():
            return str(x['id'])

def save_data(country, title, text, date, all_posts: list):
    all_posts.append({
        'categories': country,
        'title': title,
        'content': text,
        'date': date,
        'tags': get_tags(text)
    })

def parse_text_into_countries(text, date, all_posts: list):
    places = find_countries(text, is_ignore_case=True)
    countries = []
    if len(places) > 0:
        for place in places:
            try:
                country = place[0].common_name
                countries.append(country)
            except:
                country = guess_country(place[0].name, attribute='name_short')
                countries.append(country)
    else:
        country = guess_country(text, attribute='name_short')
        if country:
            countries.append(country)
    countries = list(set(countries))
    for x in countries:
        if x in bot_static.country_to_ignore:
            countries.remove(x)
    if len(countries) > 0:
        save_data(countries, countries[0], text, date, all_posts)
        
def bulk_parse_document(end_date: str, content):
    print(f'Parsing document')
    all_posts = []
    to_ignores = ["IN CIS:", "IN ASIA:", "IN MEA:", "IN LATAM:", "Good morning – Time for the daily market update"]
    num = 0
    document = Document(content)
    paragraphs = document.paragraphs
    paragraphs.reverse()
    for x in paragraphs:
        if num == 0:
            date_str = (timedelta(num) + parse(end_date))
            date_str = date_str.strftime('%Y-%m-%dT%H:%M:%S')
        to_ignore = False
        if (to_ignores[-1].lower() in x.text.lower()):
            date_str = (timedelta(num) + parse(end_date))
            if date_str.weekday() == 5:
                num -= 1
                date_str = (timedelta(num) + parse(end_date))
            elif date_str.weekday() == 6:
                num -= 2
                date_str = (timedelta(num) + parse(end_date))  
            num -= 1
            date_str = date_str.strftime('%Y-%m-%dT%H:%M:%S')
        for tg in to_ignores:
            if (tg.lower() in x.text.lower()) or (len(x.text) < 10) or (x.text.isspace()):
                to_ignore = True
                break
        if not to_ignore:
            parse_text_into_countries(x.text, date_str, all_posts)
    all_posts = list(unique_everseen(all_posts))
    return all_posts

def parse_document(start_date: str, content):
    print(f'Parsing document')
    all_posts = []
    to_ignores = ["IN CIS:", "IN ASIA:", "IN MEA:", "IN LATAM:", "Good morning – Time for the daily market update"]
    document = Document(content)
    date_str = parse(start_date) if start_date else parse('today')
    date_str = date_str.strftime('%Y-%m-%dT%H:%M:%S')
    for x in document.paragraphs:
        to_ignore = False
        for tg in to_ignores:
            if tg.lower() in x.text.lower():
                to_ignore = True
                break
        if not to_ignore:
            parse_text_into_countries(x.text, date_str, all_posts)
    all_posts = list(unique_everseen(all_posts))
    return all_posts

def send_to_wordpress(post_dict: list, categories_list):
    categories = [
        get_country_id(cat, categories_list) for cat in post_dict.get('categories')]
    while None in categories:
        categories.remove(None)
    if len(categories) > 0:
        json_data = {
            'title': post_dict.get('title'),
            'date': post_dict.get('date'),
            'content': post_dict.get('content'),
            'categories': categories,
            'status': 'publish',
            'tags': post_dict.get('tags')
        }
        response = httpx.post(
        f'{config.wordpress_host}/wp-json/wp/v2/posts', 
        auth=(config.wordress_username, config.wordress_pswd), json=json_data)
        print(response)
        if response.status_code == 201:
            print("Post sent")
        else:
            print(json_data['categories'])

def engine():
    categories = get_categories()
    with open('/media/khaliq/New Volume/Documents/Python Projects/khaliq/Upwork Projects/Fizo-webapp/DMU February 5-August 19_New.docx', 'rb') as f:
        all_posts = bulk_parse_document('August 19th 2024', f)
        # for post in all_posts[:3]:
        #     send_to_wordpress(post, categories)
        return all_posts
        
    # if len(all_posts) > 0:
    #     send_to_wordpress(all_posts)
        
        
if __name__ == '__main__':
    engine()