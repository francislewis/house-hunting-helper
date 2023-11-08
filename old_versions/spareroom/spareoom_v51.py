from datetime import datetime
from pprint import pprint
from sys import exit
from time import sleep
import requests
import logging
import json
import traceback

# local settings
from types import ModuleType
settings = ModuleType("settings")

VERSION = "0.2.0"

def make_get_request(url=None, headers=None, cookies=None, proxies=None):
    if settings.DEBUG:
        print(f'Sleeping for {settings.SLEEP} seconds')
    sleep(settings.SLEEP)
    return requests.get(url, cookies=settings.cookies, headers=settings.headers).text

def save_rooms(rooms, file_name):
    try:
        with open(file_name, 'w') as f:
            f.write(json.dumps(rooms))
    except (IOError, ValueError) as e:
        logging.error(e.strerror, extra={'function': 'save_rooms'})

def get_short_room_info(room_id, search, room_details, rooms):
    if settings.VERBOSE:
        print(f'Parsing {room_id} flat short details')

    if 'days_of_wk_available' in room_details and room_details['days_of_wk_available'] != '7 days a week':
        if settings.VERBOSE:
            print(f'Room availability: {room_details["days_of_wk_available"]} -> Removing')
        return None

    bills = 'bills_inc' in room_details and room_details['bills_inc'] == 'Yes'
    rooms_no = room_details['rooms_in_property'] if 'rooms_in_property' in room_details else 100
    station = room_details['station_name'] if 'station_name' in room_details else "No Details"

    images = [room_details['main_image_square_url']] if 'main_image_square_url' in room_details else []

    deposits = prices = []
    if 'min_rent' in room_details:
        price = int(room_details['min_rent'].split('.', 1)[0])
        price = price if 'per' in room_details and room_details['per'] == 'pcm' else price * 52 / 12
        prices.append(price)

    if 'max_rent' in room_details:
        price = int(room_details['max_rent'].split('.', 1)[0])
        price = price if 'per' in room_details and room_details['per'] == 'pcm' else price * 52 / 12
        prices.append(price)

    phone = False
    available = "No Details"
    available_timestamp = datetime.now()

    housemates = males = females = 100

    rooms[room_id] = {
        'id': room_id,
        'search': search,
        'images': images,
        'station': station,
        'prices': prices,
        'available': available,
        'timestamp': str(available_timestamp),
        'deposits': deposits,
        'bills': bills,
        'rooms': rooms_no,
        'housemates': housemates,
        'females': females,
        'males': males,
        'phone': phone,
        'new': True,
    }

def get_room_info(room_id, search, rooms):
    if settings.VERBOSE:
        print(f'Getting {room_id} flat details')

    url = f'{settings.api_location}/{settings.api_details_endpoint}/{room_id}?format=json'
    try:
        room = json.loads(make_get_request(url=url, cookies=settings.cookies, headers=settings.headers))
        if settings.DEBUG:
            pprint(room)
    except:
        return None

    if 'days_of_wk_available' in room['advert_summary'] and room['advert_summary']['days_of_wk_available'] != '7 days a week':
        if settings.VERBOSE:
            print(f'Room availability: {room["advert_summary"]["days_of_wk_available"]} -> Removing')
        return None

    phone = room['advert_summary']['tel'] if 'tel' in room['advert_summary'] else room['advert_summary']['tel_formatted'] if 'tel_formatted' in room['advert_summary'] else False
    bills = 'bills_inc' in room['advert_summary'] and room['advert_summary']['bills_inc'] == 'Yes'
    station = room['advert_summary']['nearest_station']['station_name'] if 'nearest_station' in room['advert_summary'] else "No Details"
    images = [img['large_url'] for img in room['advert_summary']['photos']] if 'photos' in room['advert_summary'] else []
    available = room['advert_summary']['available'] if 'available' in room['advert_summary'] else 'Now'
    females = room['advert_summary']['number_of_females'] if 'number_of_females' in room['advert_summary'] else 0
    males = room['advert_summary']['number_of_males'] if 'number_of_males' in room['advert_summary'] else 0

    try:
        available_timestamp = datetime.now() if available == 'Now' else datetime.strptime(available, "%d %b %Y")
    except:
        available_timestamp = datetime.now()

    rooms_no = room['advert_summary']['rooms_in_property'] if 'rooms_in_property' in room['advert_summary'] else -1
    housemates = room['advert_summary']['occupants'] if 'occupants' in room['advert_summary'] else -1

    prices = deposits = []
    if 'rooms' in room['advert_summary']:
        for r in room['advert_summary']['rooms']:
            if 'security_deposit' in r and r['security_deposit']:
                deposits.append(int(r['security_deposit'].split('.', 1)[0]))
            if 'room_price' in r and r['room_price']:
                price = int(r['room_price'].split('.', 1)[0])
                price = price if r['room_per'] == 'pcm' else price * 52 / 12
                prices.append(price)
    else:
        prices.append(room['advert_summary']['min_rent'] if 'min_rent' in room['advert_summary'] else room['advert_summary']['max_rent'] if 'max_rent' in room['advert_summary'] else None)

    new = True

    rooms[room_id] = {
        'id': room_id,
        'search': search,
        'images': images,
        'station': station,
        'prices': prices,
        'available': available,
        'timestamp': str(available_timestamp),
        'deposits': deposits,
        'bills': bills,
        'rooms': rooms_no,
        'housemates': housemates,
        'females': females,
        'males': males,
        'phone': phone,
        'new': new,
    }

    return rooms[room_id]

def search_rooms_in(area, rooms):
    if settings.VERBOSE:
        print(f'Searching for {area} flats in SpareRoom')

    settings.preferences['page'] = 1
    settings.preferences['where'] = area.lower()
    params = '&'.join([f'{key}={settings.preferences[key]}' for key in settings.preferences])
    url = f'{settings.api_location}/{settings.api_search_endpoint}?{params}'

    try:
        results = json.loads(make_get_request(url=url, cookies=settings.cookies, headers=settings.headers))
        if settings.DEBUG:
            print(results)

        if settings.VERBOSE:
            print(f'Parsing page {results["page"]}/{results["pages"]} flats in {area}')

        for room in results['results']:
            room_id = room['advert_id']

            if room_id in rooms:
                rate_room(room_id, rooms)
                continue

            if settings.FAST:
                get_short_room_info(room_id, area, room, rooms)
            else:
                get_room_info(room_id, area, rooms)

            rate_room(room_id, rooms)
    except Exception as e:
        if settings.VERBOSE:
            print(traceback.format_exc())
            print(f'Error parsing first page: {str(e)}')
            exit(0)
        return None

    for page in range(1, min(int(results['pages']), settings.MAX_PAGES)):
        settings.preferences['page'] = page + 1
        params = '&'.join([f'{key}={settings.preferences[key]}' for key in settings.preferences])
        url = f'{settings.api_location}/{settings.api_search_endpoint}?{params}'
        try:
            results = json.loads(make_get_request(url=url, cookies=settings.cookies, headers=settings.headers))
        except Exception as e:
            if settings.VERBOSE:
                print(f'Error Getting {page}/{results["pages"]}: {str(e)}')

        if settings.VERBOSE:
            print(f'Parsing page {results["page"]}/{results["pages"]} flats in {area}')

        for room in results['results']:
            room_id = room['advert_id']

            if room_id in rooms:
                rate_room(room_id, rooms)
                continue

            if settings.FAST:
                get_short_room_info(room_id, area, room, rooms)
            else:
                get_room_info(room_id, area, rooms)

            rate_room(room_id, rooms)

def rate_room(room_id, rooms):
    pass  # Placeholder for rate_room implementation

def get_new_rooms(spareroom):
    for area in spareroom.AREAS:
        search_rooms_in(area, spareroom.rooms)
        save_rooms(spareroom.rooms, spareroom.file_name)

def room_finder(
    preferences="a,r,h,w,p,b,i",
    areas=None,
    max_results=100,
    max_rooms=100,
    max_pages=10,
    sleep=1,
    rent=700,
    date=None,
    min_date=None,
    gender='males',
    room_type='double',
    rate=False,
    update=False,
    fast=False,
    debug=True,
    verbose=False):

    # Setup logging configurations
    LOG_FORMAT = '%(asctime)s - %(function)s - %(message)s'
    logging.basicConfig(format=LOG_FORMAT)

    # Boolean settings
    settings.VERBOSE = verbose
    settings.DEBUG = debug
    settings.FAST = fast
    settings.UPDATE = update

    settings.PREFERENCES = preferences.split(',')
    settings.AREAS = areas

    settings.MAX_RESULTS = max_results
    settings.MAX_PAGES = max_pages
    settings.MAX_ROOMS = max_rooms
    settings.SLEEP = sleep

    settings.MAX_RENT_PM = rent
    settings.WHEN = datetime.strptime(date, "%Y-%m-%d")
    settings.MIN_AVAILABLE_TIME = datetime.strptime(min_date, "%Y-%m-%d")
    settings.FOR = gender
    settings.TYPE = room_type

    # Static vars
    settings.FIELDS = ['score', 'id', 'images', 'prices', 'station', 'available', 'phone']

    if update and not rate:
        settings.UPDATE = False

    spareroom_preferences = {
        'format': 'json',
        'max_rent': settings.MAX_RENT_PM,
        'per': 'pcm',
        'page': 1,
        'room_types': settings.TYPE,
        'rooms_for': settings.FOR,
        'max_per_page': settings.MAX_ROOMS,
        'where': 'london',
        'when': settings.WHEN,
    }

    spareroom = ModuleType("spareroom")
    spareroom.preferences = spareroom_preferences
    spareroom.AREAS = settings.AREAS
    spareroom.file_name = 'spareroom.json'
    spareroom.rooms = {}

    get_new_rooms(spareroom)

# Example usage:
room_finder(
    preferences="a,r,h,w,p,b,i",
    areas=["Southwark", "Brixton"],
    max_results=100,
    max_rooms=100,
    max_pages=10,
    sleep=1,
    rent=700,
    date="2023-11-02",
    min_date="2023-11-01",
    gender='males',
    room_type='double',
    rate=False,
    update=False,
    fast=False,
    debug=False,
    verbose=False
)

print('test')
