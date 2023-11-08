# Try and re-write myself at this point

from datetime import datetime
from pprint import pprint
from sys import argv, exit
from time import sleep
import requests
import logging
import json

preferences = {
        'format': 'json',
        'max_rent': 2000,
        'per': 'pcm',
        'page': 1,
        'room_types': settings.TYPE,
        'rooms_for': settings.FOR,
        'max_per_page': settings.MAX_ROOMS,
        'area': 'london',
        'when': settings.WHEN,
    }


def make_get_request(SLEEP, url=None, headers=None, cookies=None, proxies=None):
    sleep(SLEEP)
    return requests.get(url, cookies=cookies, headers=headers).text

def save_rooms(rooms):
    """Saves the found rooms in the defined file."""
    print(rooms)


headers = {'User-Agent': 'SpareRoomUK 3.1'}

api_location = 'http://iphoneapp.spareroom.co.uk'
api_search_endpoint = 'flatshares'
api_details_endpoint = 'flatshares'

location = 'http://www.spareroom.co.uk'
details_endpoint = 'flatshare/flatshare_detail.pl?flatshare_id='
file_name = 'spareroom.json'
cookies = None


def get_room_info(room_id, search):

    url = '{location}/{endpoint}/{id}?format=json'.format(location=api_location,
                                                          endpoint=api_details_endpoint, id=room_id)
    try:
        room = json.loads(make_get_request(url=url, cookies=cookies, headers=headers))
    except:
        return None

    room = {}

    if 'days_of_wk_available' in room['advert_summary'] and room['advert_summary'][
        'days_of_wk_available'] != '7 days a week':
        return None

    phone = room['advert_summary']['tel'] if 'tel' in room['advert_summary'] else room['advert_summary'][
        'tel_formatted'] if 'tel_formatted' in room['advert_summary'] else False
    bills = True if 'bills_inc' in room['advert_summary'] and room['advert_summary']['bills_inc'] == 'Yes' else False
    station = room['advert_summary']['nearest_station']['station_name'] if 'nearest_station' in room[
        'advert_summary'] else "No Details"
    images = [img['large_url'] for img in room['advert_summary']['photos']] if 'photos' in room[
        'advert_summary'] else []
    available = room['advert_summary']['available'] if 'available' in room['advert_summary'] else 'Now'
    females = room['advert_summary']['number_of_females'] if 'number_of_females' in room['advert_summary'] else 0
    males = room['advert_summary']['number_of_males'] if 'number_of_males' in room['advert_summary'] else 0

    try:
        available_timestamp = datetime.now() if available == 'Now' else datetime.strptime(available, "%d %b %Y")
    except:
        available_timestamp = datetime.now()

    rooms_no = room['advert_summary']['rooms_in_property'] if 'rooms_in_property' in room['advert_summary'] else -1
    housemates = room['advert_summary']['occupants'] if 'occupants' in room['advert_summary'] else -1

    # if 'rooms' not in room['advert_summary']:
    # return None

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
        prices.append(
            room['advert_summary']['min_rent'] if 'min_rent' in room['advert_summary'] else room['advert_summary'][
                'max_rent'] if 'max_rent' in room['advert_summary'] else None)

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


def search_rooms_in(area):

    preferences['page'] = 1
    preferences['where'] = area.lower()
    params = '&'.join(['{key}={value}'.format(key=key, value=preferences[key]) for key in preferences])
    url = '{location}/{endpoint}?{params}'.format(location=api_location, endpoint=api_search_endpoint,
                                                  params=params)

    try:
        results = json.loads(make_get_request(url=url, cookies=cookies, headers=headers))

    except Exception:
        pass

        for room in results['results']:
            room_id = room['advert_id']
            get_room_info(room_id, area)


    for page in range(1, min(int(results['pages']), settings.MAX_PAGES)):
        self.preferences['page'] = page + 1
        params = '&'.join(['{key}={value}'.format(key=key, value=self.preferences[key]) for key in self.preferences])
        url = '{location}/{endpoint}?{params}'.format(location=self.api_location, endpoint=self.api_search_endpoint,
                                                      params=params)
        try:
            results = json.loads(self.make_get_request(url=url, cookies=self.cookies, headers=self.headers))
        except Exception as e:
            pass

        for room in results['results']:
            room_id = room['advert_id']

            if room_id in self.rooms:
                self.rate_room(room_id)
                continue

            self.get_room_info(room_id, area)



def get_new_rooms(AREAS):
    for area in AREAS:
        search_rooms_in(area)
        save_rooms()