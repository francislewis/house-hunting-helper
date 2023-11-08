import requests
import json
from time import sleep
from collections import OrderedDict
from urllib.parse import urlencode
from math import ceil
from helper_funcs import spareroom_id_to_link


def make_get_request(url=None, headers=None, cookies=None, sleep_time=1):
    sleep(sleep_time)
    return requests.get(url, cookies=cookies, headers=headers).text


def search_for_spareroom_ids(preferences, max_prop=200):
    """
    Search according to preferences and return list of spareroom ids.
    :param preferences: dict
    :param max_prop:
    :return:
    """

    # Fixed variables for scraping/API
    headers = {'User-Agent': 'SpareRoomUK 3.1'}
    cookies = {'session_id': '00000000', 'session_key': '000000000000000'}
    api_location = 'http://iphoneapp.spareroom.co.uk'
    api_search_endpoint = 'flatshares'
    api_details_endpoint = 'flatshares'

    # Check that required preferences have been passed:
    for key in ['location', 'distance', 'max_price']:
        if key not in preferences:
            raise KeyError(f"Key '{key}' not found in preferences, please include")

    if 'short_term' in preferences:
        short_term_ok = preferences['short_term']
    else:
        short_term_ok = False

    # Use search preferences
    params = OrderedDict(format='json',
                         max_rent=preferences['max_price'],
                         per='pcm',
                         page=1,
                         max_per_page=20,
                         where=preferences['location'].lower(),
                         miles_from_max=str(ceil(preferences['distance'] / 1.6)),
                         posted_by="private_landlords",
                         showme_1beds='Y',
                         # available_from='{:%Y-%m-%d}'.format(avail_from),
                         )

    # Get total number of results pages
    try:
        total_pages = json.loads(make_get_request(url='{location}/{endpoint}?{params}'.format(location=api_location,
                                                                                              endpoint=api_search_endpoint,
                                                                                              params=urlencode(params)),
                                                  cookies=cookies, headers=headers))['pages']
    except KeyError:
        total_pages = 1
    pages_left = ceil(min(max_prop / params['max_per_page'], total_pages))

    sr_id_list = []

    # Loop over each page
    for page in range(1, pages_left + 1):
        params['page'] = page
        url = '{location}/{endpoint}?{params}'.format(location=api_location,
                                                      endpoint=api_search_endpoint,
                                                      params=urlencode(params))
        try:
            results = json.loads(make_get_request(url=url,
                                                  cookies=cookies,
                                                  headers=headers))
            for room in results['results']:
                if room['days_of_wk_available'] == '7 days a week':
                    if 'short' in room['ad_title'].lower():
                        if short_term_ok:
                            room_id = room['advert_id']
                            sr_id_list.append(room_id)
                    else:
                        room_id = room['advert_id']
                        sr_id_list.append(room_id)


        except Exception as e:
            print(e)
            return None
    print(sr_id_list)
    return sr_id_list


# TODO: combine these into single function?
def has_parking(sr_prop):
    try:
        if sr_prop['advert_details'][3]['content'][1]['Parking'] == 'Yes':
            return True
        else:
            return False
    except (KeyError, TypeError, IndexError):
        return False


def smoking_ok(sr_prop):
    try:
        if sr_prop['advert_details'][4]['content'][0]['Smoking OK?'] == 'Yes':
            return True
        else:
            return False
    except (KeyError, TypeError, IndexError):
        return False


def pets_ok(sr_prop):
    try:
        if sr_prop['advert_details'][4]['content'][1]['Pets OK?'] == 'Yes':
            return True
        else:
            return False
    except (KeyError, TypeError, IndexError):
        return False


def couples_ok(sr_prop):
    try:
        if sr_prop['advert_summary']['couples'] == 'Y':
            return True
        else:
            return False
    except (KeyError, TypeError, IndexError):
        return False

def deposit_amount(sr_prop):
    try:
        deposit = int(float(sr_prop['advert_details'][2]['content'][0]['Deposit'][1:]))
        if deposit:
            return deposit
        else:
            return 'N/A'
    except (KeyError, TypeError, IndexError):
        return 'N/A'

def available_from(sr_prop):
    try:
        available = str(sr_prop['advert_details'][0]['content'][5]['Available'])
        if available:
            return available
        else:
            return 'N/A'
    except KeyError:
            return 'N/A'

def get_min_tenancy(sr_prop):
    try:
        min_tenancy = str(sr_prop['advert_details'][0]['content'][6]['Min term'])
        if min_tenancy:
            return min_tenancy
        else:
            return 'N/A'
    except KeyError:
            return 'N/A'

def get_nearest_station(sr_prop):
    try:
        nearest_station = str(sr_prop['advert_details'][0]['content'][4]['Nearest Station'])
        if nearest_station:
            return nearest_station
        else:
            return 'N/A'
    except KeyError:
            return 'N/A'





def getspareoominfo(room_id, sleep_time=1):
    """
    Pass a spareroom id and get a dict object of details back
    :param room_id:
    :param sleep_time: int (seconds), time to wait during request. Slow internet = Higher sleep time
    :return:
    """
    headers = {'User-Agent': 'SpareRoomUK 3.1'}

    api_location = 'http://iphoneapp.spareroom.co.uk'
    api_search_endpoint = 'flatshares'
    api_details_endpoint = 'flatshares'

    location = 'http://www.spareroom.co.uk'
    details_endpoint = 'flatshare/flatshare_detail.pl?flatshare_id='
    cookies = None

    url = '{location}/{endpoint}/{id}?format=json'.format(location=api_location, endpoint=api_details_endpoint,
                                                          id=room_id)

    print(f'SpareRoom: Gathering information on: {spareroom_id_to_link(room_id)}')

    sleep(sleep_time)
    request_result = requests.get(url, cookies=cookies, headers=headers).text

    sr_prop = json.loads(request_result)

    spareroom_prop = {'id': sr_prop['advert_summary']['advert_id'], 'title': sr_prop['advert_summary']['ad_title'],
                      'location': f"{sr_prop['advert_summary']['neighbourhood_name']}, {sr_prop['advert_details'][0]['content'][3]['Postcode']}",
                      'platform_location': f"{sr_prop['advert_summary']['latitude']}, {sr_prop['advert_summary']['longitude']}",
                      'price': sr_prop['advert_summary']['min_rent'],
                      'description': sr_prop['advert_details'][1]['content'],
                      'available_from': available_from(sr_prop),
                      'EPC': 'N/A',
                      'has_garden': False,
                      'Student Friendly': False,
                      'Furnishing': sr_prop['advert_details'][3]['content'][0]['Furnishings'],
                      'Families Allowed': False, 'Pets Allowed': pets_ok(sr_prop),
                      'Smoking Allowed': smoking_ok(sr_prop),
                      'Deposit': deposit_amount(sr_prop),
                      'Minimum Tenancy': get_min_tenancy(sr_prop),
                      'Bills Included': False,
                      'nearest_station': get_nearest_station(sr_prop),
                      'Notified': False, 'link': spareroom_id_to_link(sr_prop['advert_summary']['advert_id']),
                      'Fireplace': False, 'Parking': has_parking(sr_prop), 'platform': 'spareroom'
                      }

    # TODO:
    #  student friendly (from occupation - e.g 'Don't mind', but need to check the other options to turn into boolean)

    return spareroom_prop



# OpenRent has that Spareoom doesn't: garden, bill included, families allowed, fireplace, EPC
# Spareroom has that openrent doesn't: couples allowed, picture url
