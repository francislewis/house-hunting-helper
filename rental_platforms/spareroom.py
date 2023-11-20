from rental_platforms import RentalPlatform
from time import sleep
from collections import OrderedDict
import requests
from math import ceil
import json
from urllib.parse import urlencode
from helper_funcs import spareroom_id_to_link

def make_get_request(url=None, headers=None, cookies=None, sleep_time=0.1):
    sleep(sleep_time)
    return requests.get(url, cookies=cookies, headers=headers).text

class SpareRoom(RentalPlatform):
    def __init__(self, all_preferences):
        # Process preferences that are shared between all platforms
        super().__init__(all_preferences)

        # Process Spareroom specific preferences
        if 'short_term' in self.all_preferences:
            self.short_term_ok = self.all_preferences['short_term']
        else:
            self.short_term_ok = False

        # Setup some fixed variables for search methods
        self.headers = {'User-Agent': 'SpareRoomUK 3.1'}
        self.cookies = {'session_id': '00000000', 'session_key': '000000000000000'}
        self.api_location = 'http://iphoneapp.spareroom.co.uk'
        self.api_search_endpoint = 'flatshares'
        self.api_details_endpoint = 'flatshares'

    def initial_search(self):
        """
        Run a search with the preferences and store the resulting ids of the properties in self.property_ids
        """
        self.results = {}
        self.search_params = OrderedDict(format='json',
                         max_rent=self.max_price,
                         per='pcm',
                         page=1,
                         max_per_page=20,
                         where=self.location,
                         miles_from_max=str(ceil(self.distance / 1.6)),
                         posted_by="private_landlords",
                         showme_1beds='Y',
                         # available_from='{:%Y-%m-%d}'.format(avail_from),
                         )

        # Set the number of pages to get
        self._get_total_num_pages()

        # Loop over each page
        for page in range(1, self.pages_left + 1):
            self.search_params['page'] = page
            url = '{location}/{endpoint}?{params}'.format(location=self.api_location,
                                                          endpoint=self.api_search_endpoint,
                                                          params=urlencode(self.search_params))
            try:
                results = json.loads(make_get_request(url=url,
                                                      cookies=self.cookies,
                                                      headers=self.headers))

                for room in results['results']:
                    # print(f'room: {room}')

                    if room['days_of_wk_available'] == '7 days a week':
                        if 'short' in room['ad_title'].lower():
                            if self.short_term_ok:
                                room_id = room['advert_id']
                                self.results[room_id] = self.process_features(room)
                        else:
                            room_id = room['advert_id']
                            self.results[room_id] = self.process_features(room)

            except Exception as e:
                print(e)

    def _get_total_num_pages(self):
        """
        Internal method only to be called by self.get_property_ids()
        sets self.pages_left based upon the total number of pages and an optional user preference
        """
        # Get the total pages from the api response
        try:
            total_pages = json.loads(make_get_request(url='{location}/{endpoint}?{params}'.format(location=self.api_location,
                                                                                                  endpoint=self.api_search_endpoint,
                                                                                                  params=urlencode(
                                                                                                      self.search_params)),
                                                      cookies=self.cookies, headers=self.headers))['pages']
        except KeyError:
            total_pages = 1

        # If there is a user set number of max properties to return, take this into account
        if self.max_properties is not None:
            self.pages_left = ceil(min(self.max_properties / self.search_params['max_per_page'], total_pages))
        else:
            self.pages_left = total_pages

    def process_features(self, api_result):
        final_property_details = {'id': 'unknown',
                                  'title': 'unknown',
                                  'price': 'unknown',
                                  'deposit': 'unknown',
                                  'bills_included': 'unknown',
                                  'min_tenancy': 'unknown',
                                  'description': 'unknown',
                                  'available_from': 'unknown',
                                  'general_location': 'unknown',
                                  'exact_location': 'unknown',
                                  'nearest_station': 'unknown',
                                  'tube_zone': 'unknown',
                                  'furnishing': 'unknown',
                                  'epc': 'unknown',
                                  'has_garden': 'unknown',
                                  'student_friendly': 'unknown',
                                  'dss': 'unknown',
                                  'families_allowed': 'unknown',
                                  'smoking_allowed': 'unknown',
                                  'fireplace': 'unknown',
                                  'parking': 'unknown',
                                  'platform': 'unknown',
                                  'last_updated': 'unknown',
                                  'posted': 'unknown',
                                  'url': 'unknown',
                                  'image_url': 'unknown',
                                  'video_viewings': 'unknown',
                                  'room_type': 'unknown',
                                  'bedrooms': 'unknown',
                                  'bathrooms': 'unknown',
                                  'pets': 'unknown'
                                  }
        try:
            final_property_details['id'] = api_result['advert_id']
            final_property_details['title'] = api_result['ad_title']
            final_property_details['price'] = api_result['min_rent']
            final_property_details['deposit'] = api_result['security_deposit']
            final_property_details['available_from'] = api_result['available_from']
            final_property_details['exact_location'] = f"{api_result['latitude']}, {api_result['longitude']}"
            final_property_details['nearest_station'] = api_result['station_name']
            final_property_details['tube_zone'] = api_result['station_zone']
            final_property_details['couples'] = api_result['couples']
            final_property_details['platform'] = 'spareroom'
            final_property_details['url'] = spareroom_id_to_link(api_result['advert_id'])
            final_property_details['image_url'] = api_result['main_image_large_url']
            final_property_details['room_type'] = api_result['accom_type']
            if 'parking' in api_result['ad_text_255'].lower():
                final_property_details['parking'] = 'yes'
            else:
                final_property_details['parking'] = 'unknown'

        except (KeyError, TypeError, IndexError):
            pass

        return final_property_details

    def get_extra_details(self):
        self.property_ids = list(self.results.keys())

        for property_id in self.results:
            current_saved_property = self.results[property_id]
            url = '{location}/{endpoint}/{id}?format=json'.format(location=self.api_location,
                                                                  endpoint=self.api_details_endpoint,
                                                                  id=property_id)

            request_result = requests.get(url, cookies=None, headers=self.headers).text
            property_api_response = json.loads(request_result)

            assert property_api_response['advert_summary']['advert_id'] == property_id
            assert property_api_response['advert_summary']['min_rent'] == current_saved_property['price']

            try:
                current_saved_property[
                    'general_location'] = f"{property_api_response['advert_summary']['neighbourhood_name']}, {property_api_response['advert_details'][0]['content'][3]['Postcode']}"
                current_saved_property['description'] = property_api_response['advert_details'][1]['content']
                current_saved_property['furnishing'] = property_api_response['advert_details'][3]['content'][0][
                    'Furnishings'],

                if property_api_response['advert_details'][3]['content'][1]['Parking'] == 'Yes':
                    current_saved_property['parking'] = 'yes'
                else:
                    current_saved_property['parking'] = 'no'

                if property_api_response['advert_details'][4]['content'][0]['Smoking OK?'] == 'Yes':
                    current_saved_property['smoking_allowed'] = 'yes'
                else:
                    current_saved_property['smoking_allowed'] = 'no'

                if property_api_response['advert_details'][4]['content'][1]['Pets OK?'] == 'Yes':
                    current_saved_property['pets'] = 'yes'
                else:
                    current_saved_property['pets'] = 'no'

                if property_api_response['advert_summary']['couples'] == 'Y':
                    current_saved_property['couples'] = 'yes'
                else:
                    current_saved_property['couples'] = 'no'

                deposit = int(float(property_api_response['advert_details'][2]['content'][0]['Deposit'][1:]))
                if deposit:
                    current_saved_property['deposit'] = deposit

                available_from = str(property_api_response['advert_details'][0]['content'][5]['Available'])
                if available_from:
                    current_saved_property['available_from'] = available_from

                min_tenancy = str(property_api_response['advert_details'][0]['content'][6]['Min term'])
                if min_tenancy:
                    current_saved_property['min_tenancy'] = min_tenancy

                nearest_station = str(property_api_response['advert_details'][0]['content'][4]['Nearest Station'])
                if nearest_station:
                    current_saved_property['nearest_station'] = nearest_station

            except (KeyError, TypeError, IndexError):
                pass

    def main(self):
        self.initial_search()
        self.get_extra_details()
        self.save(self.results)


# Test/Example
test_preferences = {
    'location': 'Southwark',
    'distance': 3,
    'min_price': 600,
    'max_price': 2000,
    'min_beds': 1,
    'max_beds': 1,
    'short_term_ok': False
}
s = SpareRoom(test_preferences)
s.main()
