import requests
import json
from pprint import pprint
from random import sample, choice as rchoice, shuffle
from bs4 import BeautifulSoup

base_url = 'https://ogwarriorbeat.com/wp-json/wp/v2'
local_url = "http://localhost:5000/api/"

roles = [
    "photographer",
    "staff_writer",
    "graphic_designer",
    "digital_editor",
    "lead_designer",
    "co_editor"
]

# Defaults
default_media = "https://secure.gravatar.com/avatar/163cc0701726a2936ed69f79ac7aafbe?s=96&d=mm&r=g"
default_desc = "Deep Patel is a senior at Oak Grove High School and is a first year staff photographer and programer for the Warrior Beat. He enjoys playing outdoors and watching action packed shows. Do not be afraid of his red dot and yellow U on his forehead."

# Data
user_desc = None
user_media = None
random_ids = None

# Logger
log = None


def scrape_media():
    page = requests.get('https://ogwarriorbeat.com/staff/').text
    soup = BeautifulSoup(page, 'html.parser')
    media = []
    for l in soup.find_all('img'):
        src = l.get('src')
        name = l.get('alt')
        if 'IMG_' in src:
            user = {
                'title': name,
                'source': src
            }
            media.append(user)
    return media


def scrape_desc():
    page = requests.get('https://ogwarriorbeat.com/staff/').text
    soup = BeautifulSoup(page, 'html.parser')
    anchors = soup.find_all('a')
    desc_refs = [i.get('href') for i in anchors if "?writer=" in i.get('href')]
    desc = []
    for ref in desc_refs:
        page = requests.get(ref).text
        soup = BeautifulSoup(page, 'html.parser')
        div = soup.find("div", "staffprofile")
        desc.append(div.get_text())
    return desc


def parse_render(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()


def get_desc(name):
    desc = next((i for i in user_desc if name in i), default_desc)
    return desc


def get_profile_image(name):
    default = {
        'title': name,
        'source': default_media,
    }
    profile = next((i for i in user_media if i['title'] == name), default)
    medID = rchoice(random_ids)
    random_ids.remove(medID)
    profile['mediaId'] = str(medID)
    profile['type'] = "profile-image"
    requests.post(local_url + 'media', json=json.dumps(profile))
    return profile


def get_cover_image(id, title):
    wp = requests.get(f"{base_url}/media/{id}").json()
    capt = wp['caption']['rendered']
    cover_image = {
        "mediaId": str(wp['id']),
        "source": wp['media_details']['sizes']['full']['source_url'],
        "title": parse_render(title),
        "credits": "Photo Courtesy of John Adam",
        "caption": parse_render(capt) if len(capt) > 0 else "A Photo Caption"
    }
    requests.post(local_url + 'media', json=json.dumps(cover_image))
    return cover_image


def make_author(id):
    wp = requests.get(f"{base_url}/users/{id}").json()
    author = {
        "authorId": str(id),
        "name": wp['name'],
        "title": sample(roles, 2),
        "description": get_desc(wp['name']),
        "profile_image": get_profile_image(wp['name'])['mediaId'],
        "grade_year": str(sample(range(9, 13), 1)[0]),
        "staff_year": str(sample(range(1, 5), 1)[0])
    }
    author_data = json.dumps(author)
    requests.post(local_url + 'authors', json=author_data)
    return author


def get_category(id):
    wp = requests.get(f"{base_url}/categories/{id}").json()
    if wp['id'] == 1 or wp['id'] == 2:
        return {}
    wp['id'] = 30 if wp['id'] == 34 else wp['id']
    category = {
        "categoryId": str(wp['id']),
        "name": wp["name"]
    }
    cat_data = json.dumps(category)
    requests.post(local_url + "categories", json=cat_data)
    return category


def make_post(wp):
    post = {
        "postId": str(wp['id']),
        "title": parse_render(wp['title']['rendered']),
        "date": wp['date'],
        "content": wp['content']['rendered'],
        "type": "article",
        "author": make_author(wp['author'])['authorId'],
        "cover_image": get_cover_image(wp['featured_media'], wp['title']['rendered'])['mediaId'],
        "categories": [get_category(i).get('categoryId', None) for i in wp['categories']]
    }
    post['categories'] = [i for i in post['categories'] if i is not None]
    post['categories'] = [
        7
    ] if len(post['categories']) == 0 else post['categories']
    return post


def create_post(post, prog):
    post = json.dumps(post)
    req = requests.post(local_url + "posts", json=post)
    try:
        req.raise_for_status()
    except requests.HTTPError as e:
        print(f'\n{str(e)}')
        print('\n POST DATA: ')
        pprint(json.loads(post))
        raise
    log.info(
        f"Request Made: $[{prog[0]}]$[/{prog[1]}] || Status: $[{req.status_code}]")
    return req


def scrape_data():
    wp_posts = requests.get(base_url + '/posts').json()
    posts = list(map(make_post, wp_posts))
    cur_req = 0
    for p in posts:
        cur_req += 1
        create_post(p, (cur_req, len(posts)))


def upload_scraped_data(logger=None):
    global user_desc, user_media, random_ids, log
    log = logger
    user_media = scrape_media()
    user_desc = scrape_desc()
    random_ids = sample(range(4000, 5000), len(user_media) + 10)
    shuffle(random_ids)
    scrape_data()
