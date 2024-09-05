from rental_platform_scrapers import RentalPlatform
import requests
import datetime
import re
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections import OrderedDict
from urllib.parse import urlencode
from utils.helper_funcs import openrent_id_to_link, google_maps_link, convert_date_to_standard, convert_time_ago_to_datetime


class OpenRent(RentalPlatform):
    def __init__(self, all_preferences):
        # Process preferences
        super().__init__(all_preferences)

    def _initial_search(self):
        """
        This will create a search url from the passed preferences and scrape the results,
        saving them in self.search_results()
        :return:
        """
        print('OPENRENT: Getting initial details')
        query_string = urlencode(
            OrderedDict(term=self.location,
                        within=str(int(self.distance)),
                        prices_min=int(self.min_beds),
                        prices_max=int(self.max_price),
                        bedrooms_min=int(self.min_beds),
                        bedrooms_max=int(self.min_beds)))

        url = ("http://www.openrent.co.uk/properties-to-rent/?%s" % query_string)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Find the script tag that contains the data we want
        # Criteria is that it has a line that read "var PROPERTYIDS =  ..."
        # This is how we avoid having to scroll the page to get all the properties
        search_response = soup.find(lambda tag: tag.name == "script" and "PROPERTYIDS" in tag.text).text

        # Pull out all the var name = [...] lines from the script using a regex
        unprocessed_search_results = re.findall(r"var\s(\S+)\s?=\s?(\[[^\]]*\])", search_response)

        num_total_properties = int(re.search(r'var NUMBEROFPROPERTIES = (\d+);', search_response).group(1))
        print(f'OPENRENT: {num_total_properties} properties found')

        semi_processed_search_results = {}

        for k, v in unprocessed_search_results:
            if k in ['islivelistBool', 'prices', 'bedrooms', 'bathrooms', 'students', 'nonStudents', 'dss',
                                 'pets', 'isstudio', 'isshared', 'furnished', 'unfurnished', 'hasVideo',
                                 'videoViewingsAccepted', 'propertyTypes', 'hoursLive']:
                v = v.split(',')
                v[0] = v[0][3:]
                v = v[:-1]
                v = [int(i) for i in v]
                semi_processed_search_results[k] = v

            elif k in ['gardens', 'parkings', 'bills', 'fireplaces', 'availableFrom', 'minimumTenancy']:
                v = v[1:-1]
                v = v.split(',')
                v = [int(i) for i in v]
                semi_processed_search_results[k] = v

            elif k == 'PROPERTYIDS':
                v = v[2:-2]
                v = v.split(',')
                v = [int(i) for i in v]
                semi_processed_search_results[k] = v

            elif k == 'PROPERTYLISTLATITUDES':
                v = v[3:]
                v = v.split(',')
                del v[-1]
                semi_processed_search_results[k] = v

            elif k == 'PROPERTYLISTLONGITUDES':
                v = v.split('-')[1:]
                v = [f'-{i}' for i in v]
                semi_processed_search_results[k] = v

        for v in semi_processed_search_results.values():
            assert len(v) == num_total_properties, 'Error with search'

        property_ids = semi_processed_search_results['PROPERTYIDS']
        num_elements = len(property_ids)

        # This is variable that will store the final results in the correct structure
        self.search_results = {}

        # Need to now process data to get into correct structure
        for i in range(num_elements):
            key_values = {}
            current_id = property_ids[i]
            for key, values_list in semi_processed_search_results.items():
                if key == 'PROPERTYIDS':
                    continue  # Skip the 'ids' key itself
                key_values[key] = values_list[i]
            self.search_results[current_id] = key_values

        assert list(self.search_results.keys()) == property_ids, 'Error with initial openrent search'

    def _get_extra_details(self):
        """
        By utilising an undocumented API, we can get a few extra details for each property
        :return:
        """
        print('OPENRENT: Getting full details')
        self.property_ids = list(self.search_results.keys())
        for property_id in tqdm(self.property_ids):
            # The initial search is quite general, so first we filter down and remove ones that don't meet preferences
            # TODO: maybe make a method somewhere else in which certain preferences can be dealbreakers and some are ranked etc
            if self.search_results[property_id]['prices'] > self.max_price:
                del self.search_results[property_id]

            elif self.search_results[property_id]['prices'] < self.min_price:
                del self.search_results[property_id]

            elif self.search_results[property_id]['bedrooms'] > self.max_beds:
                del self.search_results[property_id]

            elif self.search_results[property_id]['bedrooms'] < self.min_beds:
                del self.search_results[property_id]

            # TODO: can use this to try filter out agents who worm their way in
            # elif 'we are proud to offer' in self.search_results[property_id]['description'].lower():

            else:
                # If the property matches the key preferences then get the extra details
                endpoint = "https://www.openrent.co.uk/search/propertiesbyid?"
                extra_info_from_id = requests.get(endpoint, params=[('ids', property_id)]).json()

                # Save the full json result
                self.search_results[property_id]['full_json'] = str(json.dumps(extra_info_from_id))

                # Save this extra info
                self.search_results[property_id]['title'] = extra_info_from_id[0]['title']
                self.search_results[property_id]['description'] = extra_info_from_id[0]['description']
                self.search_results[property_id]['imageurl'] = extra_info_from_id[0]['imageUrl'][2:]
                self.search_results[property_id]['lastupdated'] = extra_info_from_id[0]['lastUpdated']

    def _create_final_results(self):
        """
        The name of the keys used in the openrent responses have so far dictated how they are saved in
        self.search_results. But we want to change some of these names, along with the formats of some values in
        order to be consistent across platforms we search on. These final results are saved in self.results.

        :return:
        """
        self.results = {}
        for property_id in list(self.search_results.keys()):
            current_property = self.search_results[property_id]
            # We are now filling out self.results (the final results), by transforming the data in self.search_results
            if current_property['islivelistBool'] == 1:
                self.results[property_id] = self.final_property_details.copy()

                self.results[property_id]['id'] = property_id
                self.results[property_id]['platform'] = 'openrent'

                # These keys are just mapped 1-2-1
                simple_mapping = {
                    'full_json': 'full_json',
                    'title': 'title',
                    'price': 'prices',
                    'min_tenancy': 'minimumTenancy',
                    'description': 'description',
                    'room_type': 'propertyTypes',
                    'bedrooms': 'bedrooms',
                    'bathrooms': 'bathrooms',
                    'image_url': 'imageurl'
                }

                # These values are given as bool: (0,1)
                bool_vals_mapping = {
                    'bills_included': 'bills',
                    'has_garden': 'gardens',
                    'student_friendly': 'students',
                    'dss': 'dss',
                    'fireplace': 'fireplaces',
                    'parking': 'parkings',
                    'video_viewings': 'videoViewingsAccepted',
                    'pets': 'pets'
                }

                # Combine dicts (need Python 3.9+)
                total_mapping = simple_mapping | bool_vals_mapping

                # Iterate over every key to swap
                for key, value in total_mapping.items():
                    # Process the ones that are bools
                    if key in bool_vals_mapping.keys():
                        if current_property[value] == 0:
                            self.results[property_id][key] = 'False'
                        elif current_property[value] == 1:
                            self.results[property_id][key] = 'True'
                    # Process all the other ones
                    else:
                        self.results[property_id][key] = current_property[value]

                self.results[property_id]['available_from'] = convert_date_to_standard(
                            datetime.datetime.now() - datetime.timedelta(days=current_property['availableFrom']))
                self.results[property_id][
                    'exact_location'] = f"{current_property['PROPERTYLISTLATITUDES']}, {current_property['PROPERTYLISTLONGITUDES']}".replace(' ', '')[:-1]
                self.results[property_id]['google_maps_link'] = google_maps_link(self.results[property_id]['exact_location'])
                self.results[property_id]['last_updated'] = convert_time_ago_to_datetime(
                    current_property['lastupdated'])
                self.results[property_id]['posted'] = convert_time_ago_to_datetime(
                    str(datetime.datetime.now() - datetime.timedelta(
                        hours=current_property['hoursLive'])))
                self.results[property_id]['url'] = openrent_id_to_link(property_id)

                if bool(current_property['furnished']) == True:
                    self.results[property_id]['furnishing'] = 'Furnished'
                elif bool(current_property['furnished']) == False:
                    self.results[property_id]['furnishing'] = 'Unfurnished'

            elif current_property['islivelistBool'] == 0:
                pass
                # TODO: Check if the listing currently exists in the db and write the date it got let if so
                # Or today's date if this is running on a regular schedule

    def main(self):
        self._initial_search()
        self._get_extra_details()
        self._create_final_results()
        self.save(self.results)

# # Test
# preferences = {
#     'location': 'Southwark',
#     'distance': 3,
#     'min_price': 600,
#     'max_price': 2000,
#     'min_beds': 1,
#     'max_beds': 1,
#     'short_term_ok': False
# }
#
# o = OpenRent(preferences)
# o.main()
