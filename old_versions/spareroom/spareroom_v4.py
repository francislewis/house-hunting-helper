#!/usr/bin/env python
from datetime import datetime
from pprint import pprint
from sys import argv, exit
from time import sleep
import requests
import logging
import json

# argparser
import argparse

import traceback

# local settings
from types import ModuleType
settings = ModuleType("settings")

VERSION = "0.2.0"

class SearchEngine(object):

    # file to store the rooms in
    file_name = 'rooms.json'

    # preferences used to make queries to the web application
    preferences = {}

    def __init__(self, preferences=None, areas=None, cookies=None):
        """
        Create a SearchEngine object.

        preferences -- preferences to be merged with the default preferences
        areas -- areas to search rooms in
        cookies -- cookies to be used when making requests to the server
        """

        self.AREAS = areas or []
        self.cookies = cookies or {}

        # merges the preferences from the settings file
        if preferences:
            for key in preferences:
                self.preferences[key] = preferences[key]

        # will hold all the rooms found in self engine
        self.rooms = {}

    def make_get_request(self, url=None, headers=None, cookies=None, proxies=None):
        if settings.DEBUG:
            print('Sleeping for {secs} seconds'.format(secs=settings.SLEEP))
        sleep(settings.SLEEP)
        return requests.get(url, cookies=self.cookies, headers=self.headers).text

    def save_rooms(self):
        """Saves the found rooms in the defined file."""

        # save the rooms found in the file
        try:
            with open(self.file_name, 'w') as f:
                f.write(json.dumps(self.rooms))

        # catch exceptions in case it cannot create the file or something wrong
        # with json.dumps
        except (IOError, ValueError) as e:
            logging.error(e.strerror, extra={'engine': self.__class__.__name__, 'function': 'save_rooms'})

    def get_room_info(self, room_id, search):
        pass

    def update(self):
        for room in self.rooms:
            try:
                self.get_room_info(room, self.rooms[room]['search'])
            except:
                self.rooms[room]['new'] = False
                continue
        self.save_rooms()

class SpareRoom(SearchEngine):
    headers = {'User-Agent': 'SpareRoomUK 3.1'}

    api_location = 'http://iphoneapp.spareroom.co.uk'
    api_search_endpoint = 'flatshares'
    api_details_endpoint = 'flatshares'

    location = 'http://www.spareroom.co.uk'
    details_endpoint = 'flatshare/flatshare_detail.pl?flatshare_id='
    file_name = 'spareroom.json'

    preferences = {}

    def get_new_rooms(self):
        for area in self.AREAS:
            self.search_rooms_in(area)
            self.save_rooms()

    def search_rooms_in(self, area):
        if settings.VERBOSE:
            print('Searching for {area} flats in SpareRoom'.format(area=area))

        self.preferences['page'] = 1
        self.preferences['where'] = area.lower()
        params = '&'.join(['{key}={value}'.format(key=key, value=self.preferences[key]) for key in self.preferences])
        url = '{location}/{endpoint}?{params}'.format(location=self.api_location, endpoint=self.api_search_endpoint, params=params)

        try:
            results = json.loads(self.make_get_request(url=url, cookies=self.cookies, headers=self.headers))
            if settings.DEBUG:
                print(results)

            if settings.VERBOSE:
                print('Parsing page {page}/{total} flats in {area}'.format(page=results['page'], total=results['pages'], area=area))

            for room in results['results']:
                room_id = room['advert_id']

                if room_id in self.rooms:
                    self.rate_room(room_id)
                    continue

                if settings.FAST:
                    self.get_short_room_info(room_id, area, room)
                else:
                    self.get_room_info(room_id, area)

                self.rate_room(room_id)
        except Exception as e:
            if settings.VERBOSE:
                print(traceback.format_exc())
                print('Error parsing first page: {message}'.format(message=e.message))
                exit(0)
            return None

        for page in range(1, min(int(results['pages']), settings.MAX_PAGES)):
            self.preferences['page'] = page + 1
            params = '&'.join(['{key}={value}'.format(key=key, value=self.preferences[key]) for key in self.preferences])
            url = '{location}/{endpoint}?{params}'.format(location=self.api_location, endpoint=self.api_search_endpoint, params=params)
            try:
                results = json.loads(self.make_get_request(url=url, cookies=self.cookies, headers=self.headers))
            except Exception as e:
                if settings.VERBOSE:
                    print('Error Getting {page}/{total}: {message}'.format(page=page, total=results['pages'], message=e.message))

            if settings.VERBOSE:
                print('Parsing page {page}/{total} flats in {area}'.format(page=results['page'], total=results['pages'], area=area))

            for room in results['results']:
                room_id = room['advert_id']

                if room_id in self.rooms:
                    self.rate_room(room_id)
                    continue

                if settings.FAST:
                    self.get_short_room_info(room_id, area, room)
                else:
                    self.get_room_info(room_id, area)

                self.rate_room(room_id)

    def get_short_room_info(self, room_id, search, room_details):
        if settings.VERBOSE:
            print('Parsing {id} flat short details'.format(id=room_id))

        if 'days_of_wk_available' in room_details and room_details['days_of_wk_available'] != '7 days a week':
            if settings.VERBOSE:
                print('Room availability: {avail} -> Removing'.format(avail=room_details['days_of_wk_available']))
            return None

        bills = True if 'bills_inc' in room_details and room_details['bills_inc'] == 'Yes' else False
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

        self.rooms[room_id] = {
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

    def get_room_info(self, room_id, search):
        if settings.VERBOSE:
            print('Getting {id} flat details'.format(id=room_id))

        url = '{location}/{endpoint}/{id}?format=json'.format(location=self.api_location, endpoint=self.api_details_endpoint, id=room_id)
        try:
            room = json.loads(self.make_get_request(url=url, cookies=self.cookies, headers=self.headers))
            if settings.DEBUG:
                pprint(room)
        except:
            return None

        if 'days_of_wk_available' in room['advert_summary'] and room['advert_summary']['days_of_wk_available'] != '7 days a week':
            if settings.VERBOSE:
                print('Room availability: {avail} -> Removing'.format(avail=room['advert_summary']['days_of_wk_available']))
            return None

        phone = room['advert_summary']['tel'] if 'tel' in room['advert_summary'] else room['advert_summary']['tel_formatted'] if 'tel_formatted' in room['advert_summary'] else False
        bills = True if 'bills_inc' in room['advert_summary'] and room['advert_summary']['bills_inc'] == 'Yes' else False
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

        #if 'rooms' not in room['advert_summary']:
            #return None

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

        self.rooms[room_id] = {
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

        return self.rooms[room_id]

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
    debug=False,
    verbose=False):

    # Setup logging configurations
    LOG_FORMAT = '%(asctime)s - %(engine)s - %(function)s - %(message)s'
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

    spareroom = SpareRoom(spareroom_preferences, settings.AREAS)


    spareroom.get_new_rooms()


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
# if __name__ == "__main__":
#     room_finder()
