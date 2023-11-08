import requests
import re
from bs4 import BeautifulSoup
# import pandas as pd
import datetime


def get_soup(url):
    """
    Make request & return soup
    """
    r = requests.get(url, allow_redirects=False)
    if r.status_code == 200:
        return BeautifulSoup(r.content, 'lxml')
    elif r.status_code == 301:
        print('Finalizado')
        exit(0)
    else:
        print('[X] Response %s .Something went wrong.' % r.status_code)
        exit(1)

def get_rooms_info(rooms_soup):
    '''
    Iterate rooms & return object list
    '''
    rooms = list()
    try:
        for room in rooms_soup.find_all('article'):
            room = get_room_info(room, 'https://www.spareroom.co.uk')
            if room is not None:
                rooms.append(room)

    # except Exception as e:
    except IndexError as e:
        print("Catch exception: ", e)
    return rooms


def inital_search(min_price_pw=180, max_price_pw=290, entries_to_scrape=30):
    DOMAIN = 'https://www.spareroom.co.uk'
    URL_ROOMS = DOMAIN + '/flatshare'
    URL_SEARCH = URL_ROOMS + search_url

    r = requests.get(URL_SEARCH % (min_price_pw, max_price_pw))
    s = BeautifulSoup(r.content, 'lxml')
    url = r.url + 'offset=%i'
    pages = int(int(s.find("p", {"class": "navcurrent"}).findAll("strong")[1].string[:-1]) / 10)

    rooms = list()

    for i in range(0, entries_to_scrape, 10):
        print('[ ] Visited pages:%i/%i \tRooms: %i' % (i + 1, i + 10, len(rooms)))
        soup = get_soup(url % i)
        rooms.extend(get_rooms_info(soup))

    return rooms

def get_pm_price(room_soup):
    rooms = []
    room_price_lists = room_soup.find('ul', class_='room-list')

    for li in room_price_lists.find_all('li'):
        # get price from strong class="room-list__price"
        price = li.find('strong', {"class": "room-list__price"}).text.strip()
        price, interval = price.split(" ")
        price = price.replace("£", "")
        if interval == "pw":
            price = int(price) * (52 / 12)
        type = li.find('small').text.strip().replace('(', '').replace(')', '')
        rooms.append({'price': price, 'type': type})
    return rooms

def get_key_features(room_soup):
    feature_list = room_soup.find('ul', class_='key-features')
    features = {'Type': None, 'Area': None, 'Postcode': None, 'Nearest station': None}
    for i, li in enumerate(feature_list.find_all('li')):
        # check if there is a sublist, and if so only take the first element
        text = li.text.strip()
        if i == 2:
            text = text.split(" ")[0]
        elif i == 3:
            text = text.split("\n")[0]

        features[list(features.keys())[i]] = li.text.strip()
    return features

def get_features(room_soup):
    feature_list = room_soup.findAll('dl', class_='feature-list')
    features = {}
    for feature_list in feature_list:
        for dt, dd in zip(feature_list.find_all('dt'), feature_list.find_all('dd')):
            key = dt.text.replace('\n', ' ').replace('#', '').strip().capitalize()
            features[key] = dd.text.strip()
    # print('')
    # print(features)
    # print('')
    return features

def get_location_coords(room_soup):
    script_text = room_soup.head.findAll("script")
    for script in script_text:
        script_text = script.text
        if "_sr.page" in script_text:
            location_idx = script_text.find("location")
            if location_idx == -1:
                continue
            location = script_text[location_idx:location_idx + 100]
            location = location.split('{')[1].split('}')[0]
            location = location.split(',')[:-1]
            location = [float(l.split(':')[1].strip().replace('"', '')) for l in location]
            # latitude, longitude
            location = (location[0], location[1])
            return location

def get_room_info(room_soup, domain):
    # Get listing page
    url = str(domain + room_soup.find("a")['href'])
    id = int(url.split("flatshare_id=")[1].split("&")[0])
    room_soup = BeautifulSoup(requests.get(url).content, 'lxml')

    # Populate basics from the search results page
    try:
        header = room_soup.find("div", {"id": "listing_heading"})
        title = str(header.h1.text.strip()) if header.h1 else None
    except AttributeError:
        print('[X] Error parsing listing page - probably not live')
        return
    desc = str(room_soup.find("p", {"class": "detaildesc"}).text.strip().replace('\r\n', ' '))

    key_features = get_key_features(room_soup)
    # for feature in key_features:
    #     print(feature)
    # [setattr(feature, key_features[feature]) for feature in key_features]


    pm_prices = get_pm_price(room_soup)
    for i, room in enumerate(pm_prices):
        price, type = room['price'], room['type']
        # setattr(f'room_{i}_price', price)
        # setattr(f'room_{i}_type', type)
        # f'room_{i}_price' = price
        # f'room_{i}_type' = type
        print(price)
        print(type)

    features = get_features(room_soup)
    # [setattr(feature, features[feature]) for feature in features]

    # Todays date
    date_scraped = datetime.datetime.now().strftime("%d-%m-%Y")

    print(features)


#! Note that %i is used for min and max rent to be substituted with the values below
search_url = '/search.pl?nmsq_mode=normal&action=search&max_per_page=&flatshare_type=offered&search=London+Zone+1+to+2&min_rent=%i&max_rent=%i&per=pw&available_search=N&day_avail=02&mon_avail=05&year_avail=2023&min_term=0&max_term=0&days_of_wk_available=7+days+a+week&showme_rooms=Y'
min_rent_pw = 180
max_rent_pw = 290
WORK_COORDS = (51.49887,-0.17897) # (lat, long) Imperial College London coordinates
API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXX" # CityMapper API key
entries_to_scrape = 5 # Number of entries to scrape - you have 5000 free CityMapper API calls per month
# -----------------------------------------------------


rooms = inital_search(min_price_pw=180, max_price_pw=290, entries_to_scrape=5)
# print(rooms)
# for room in rooms:
#     get_room_info(room, domain = 'https://www.spareroom.co.uk')
#     print(room)