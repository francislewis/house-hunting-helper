from rental_platform_scrapers import RentalPlatform
from collections import OrderedDict
import requests
from math import ceil
import json
from tqdm import tqdm
import re
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from helper_funcs import spareroom_id_to_link, google_maps_link, convert_date_to_standard, \
    find_key


class SpareRoom(RentalPlatform):
    """
    Class to run searches on the SpareRoom platform
    """

    def __init__(self, all_preferences):
        # Process search preferences that are shared between all platforms
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

    def _initial_search(self):
        """
        Run a search with the preferences and store the resulting ids of the properties in self.property_ids
        """
        print('SPAREROOM: Getting initial details')
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
                results = json.loads(requests.get(url=url,
                                                  cookies=self.cookies,
                                                  headers=self.headers).text)

                for room in results['results']:
                    if room['days_of_wk_available'] == '7 days a week':
                        if 'short' in room['ad_title'].lower():
                            if self.short_term_ok:
                                room_id = room['advert_id']
                                self.results[room_id] = self._process_intial_search_features(room)
                        else:
                            room_id = room['advert_id']
                            self.results[room_id] = self._process_intial_search_features(room)

            except Exception as e:
                print(e)

    def _get_total_num_pages(self):
        """
        Internal method only to be called by self.get_property_ids()
        sets self.pages_left based upon the total number of pages and an optional user preference
        """
        # Get the total pages from the api response
        try:
            total_pages = \
                json.loads(requests.get(url='{location}/{endpoint}?{params}'.format(location=self.api_location,
                                                                                    endpoint=self.api_search_endpoint,
                                                                                    params=urlencode(
                                                                                        self.search_params)),
                                        cookies=self.cookies, headers=self.headers).text)['pages']
        except KeyError:
            total_pages = 1

        # If there is a user set number of max properties to return, take this into account
        if self.max_properties is not None:
            self.pages_left = ceil(min(self.max_properties / self.search_params['max_per_page'], total_pages))
        else:
            self.pages_left = total_pages

    def _process_intial_search_features(self, api_result):
        """
        Here we are processing and transforming the data from the initial api response
        """
        final_property_details = self.final_property_details.copy()

        # LHS is our feature name, RHS is spareroom naming
        feature_names = {'id': 'advert_id',
                         'title': 'ad_title',
                         'price': 'min_rent',
                         'deposit': 'security_deposit',
                         'available_from': 'available_from',
                         'nearest_station': 'station_name',
                         'tube_zone': 'station_zone',
                         'couples': 'couples',
                         'image_url': 'main_image_large_url',
                         'room_type': 'accom_type'}

        # Replace names
        for new_name, original_name in feature_names.items():
            try:
                final_property_details[new_name] = api_result[original_name]
            except (KeyError, TypeError, IndexError):
                pass

        # Now we try the details that require some processing around the data format
        try:
            final_property_details['exact_location'] = f"{api_result['latitude']}, {api_result['longitude']}".replace(
                ' ', '')[:-1]
            final_property_details['google_maps_link'] = google_maps_link(final_property_details['exact_location'])
        except (KeyError, TypeError, IndexError):
            pass

        final_property_details['platform'] = 'spareroom'
        final_property_details['url'] = spareroom_id_to_link(api_result['advert_id'])

        # try:
        #     if 'parking' in api_result['ad_text_255'].lower():
        #         final_property_details['parking'] = 'yes'
        #     else:
        #         final_property_details['parking'] = 'unknown'
        # except (KeyError, TypeError, IndexError):
        #     pass

        return final_property_details

    def _get_extra_details(self):
        print(f'SPAREROOM: {len(self.results)} properties found')
        print('SPAREROOM: Getting full details')
        self.property_ids = list(self.results.keys())
        total_failed_fields = []
        for property_id in tqdm(self.results):
            failed_fields = []
            current_saved_property = self.results[property_id]
            url = '{location}/{endpoint}/{id}?format=json'.format(location=self.api_location,
                                                                  endpoint=self.api_details_endpoint,
                                                                  id=property_id)

            request_result = requests.get(url, cookies=None, headers=self.headers).text
            property_api_response = json.loads(request_result)

            current_saved_property['full_json'] = json.dumps(property_api_response)

            if "Ad not found" in str(property_api_response):
                # Skip the current entry (for now)
                continue

            assert property_api_response['advert_summary']['advert_id'] == property_id, f"{property_api_response}"
            assert property_api_response['advert_summary']['min_rent'] == current_saved_property['price'], f"{property_api_response['advert_summary']['min_rent']}, {current_saved_property['price']}, {property_id}"

            # Now we try and gather all the additional information we want
            key_mapping = {
                'min_tenancy': ['Min term', 'min_term'],
                'nearest_station': ['Nearest Station'],
                'description': ['description', 'content', 'ad_text', 'ad_text_255'],
                'furnishing': ['Furnishings', 'furnishings'],
                'parking': ['parking', 'Parking'],
                'smoking_allowed': ['smoking', 'Smoking OK?'],
                'pets': ['pets', 'Pets OK?'],
                'couples': ['couples'],
                'deposit': ['deposit', 'Deposit', 'security_deposit'],
                'dss': ['dss']
            }

            for new_key_name, potential_original_key_names in key_mapping.items():
                # Use find_keys() function to fill in details from json
                found_value = find_key(property_api_response, potential_original_key_names)
                # Check if we managed to find a correct value or not
                if found_value is not None:
                    current_saved_property[new_key_name] = found_value
                else:
                    failed_fields.append(new_key_name)

            # Now we fill in some details that require extra data processing
            current_saved_property[
                'general_location'] = f"{find_key(property_api_response, ['neighbourhood_name'])}, {find_key(property_api_response, ['postcode', 'Postcode'])}"
            if current_saved_property['general_location'] is None:
                failed_fields.append('general_location')

            available_from = find_key(property_api_response, ['available_from', 'available', 'Available'])
            current_saved_property['available_from'] = convert_date_to_standard(available_from)
            if available_from is not None:
                failed_fields.append('available_from')

            # Now we have to scrape the actual webpage to get some extra details
            listing_info = self._get_spareroom_details_from_single_webpage(spareroom_id_to_link(property_id))
            current_saved_property['deposit'] = listing_info['Deposit']
            current_saved_property['couples'] = listing_info['Couples']
            current_saved_property['req_gender'] = listing_info['Gender']
            current_saved_property['general_location'] = listing_info['General Location']
            current_saved_property['smoking_allowed'] = listing_info['Smoking']
            current_saved_property['room_type'] = listing_info['Property Type']
            current_saved_property['req_occupation'] = listing_info['Occupation']

            if listing_info['Rent Frequency'] == 'pw':
                current_saved_property['price'] = str(int(4.3*int(listing_info['Rent'])))

            total_failed_fields.append(failed_fields)

        print(f"Average number of failed fields: {sum(len(lst) for lst in total_failed_fields) / len(total_failed_fields)}")

    def _split_price_duration_info(self, string):
        # string of pattern '£int, str' gets split into int, str
        match = re.match(r'£(\d+)\s+(\w+)', string)
        return tuple(map(str.strip, match.groups())) if match else (None, None)

    def _get_price_period_details(self, soup):
        """
        The price information (amount and period  is stored in different parts of the html for pw vs pcm
        :param soup:
        :return:
        """
        # Per Week version:
        listing_details = soup.find_all('section', class_='feature')

        # Extract information from each section
        listing_info = {}
        for section in listing_details:
            feature_list = section.find('dl', class_='feature-list')
            if feature_list:
                listing_info.update({dt.text.strip(): dd.text.strip()
                                     for dt, dd in zip(feature_list.find_all('dt', class_='feature-list__key'),
                                                       feature_list.find_all('dd', class_='feature-list__value'))})

        # Extract rent amount and period
        for key, value in listing_info.items():
            if value == 'double':
                rent_amount, rent_period = self._split_price_duration_info(key)
                if rent_amount and rent_period:
                    return rent_amount, rent_period

        # Per Calendar Month version
        parent_element = soup.find(class_='feature feature--price-whole-property')
        target_element = parent_element.find(class_='feature__heading') if parent_element else None
        value = target_element.get_text(strip=True) if target_element else None
        if value:
            value = value.split('(')[0].replace(',', '')
            rent_amount, rent_period = self._split_price_duration_info(value)
            if rent_amount and rent_period:
                return rent_amount, rent_period

    def _get_spareroom_details_from_single_webpage(self, url):
        # Send a request to fetch the content of the webpage
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Parse the webpage content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all sections in the webpage
        sections = soup.find_all('section')

        # Initialize a dictionary to store the extracted information
        listing_info = {
            'Deposit': None,
            'General Location': None,
            'Couples': None,
            'Smoking': None,
            'Property Type': None,
            'Occupation': None,
            'Gender': None,
            'Rent': None,
            'Rent Frequency': None
        }

        # Function to clean text
        def clean_text(text):
            return text.strip()

        # Extract information from each section
        for section in sections:
            if section.find('ul', class_='key-features'):
                key_features = [clean_text(li.text) for li in section.find_all('li', class_='key-features__feature')]
                if key_features:
                    listing_info['Property Type'] = key_features[0] if key_features else None
                    listing_info['General Location'] = key_features[1] if len(key_features) > 1 else None
            elif section.find('dl', class_='feature-list'):
                feature_list = section.find('dl', class_='feature-list')
                for dt, dd in zip(feature_list.find_all('dt', class_='feature-list__key'),
                                  feature_list.find_all('dd', class_='feature-list__value')):
                    key = clean_text(dt.text)
                    value = clean_text(dd.text)
                    if key == 'Deposit':
                        listing_info['Deposit'] = value
                    elif key == 'Occupation':
                        listing_info['Occupation'] = value
                    elif key == 'Gender':
                        listing_info['Gender'] = value
                    elif key == 'Couples OK?':
                        listing_info['Couples'] = value
                    elif key == 'Smoking OK?':
                        listing_info['Smoking'] = value

        listing_info['Rent'], listing_info['Rent Frequency'] = self._get_price_period_details(soup)
        return listing_info

    def main(self):
        self._initial_search()
        self._get_extra_details()
        self.save(self.results)

# # Test/Example
# test_preferences = {
#     'location': 'Southwark',
#     'distance': 3,
#     'min_price': 600,
#     'max_price': 2000,
#     'min_beds': 1,
#     'max_beds': 1,
#     'short_term_ok': False
# }
# s = SpareRoom(test_preferences)
# s.main()