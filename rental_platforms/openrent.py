from rental_platforms import RentalPlatform
import requests
import json
import datetime
import re
from bs4 import BeautifulSoup
from collections import OrderedDict
from urllib.parse import urlencode
from helper_funcs import openrent_id_to_link


class OpenRent(RentalPlatform):
    def __init__(self, all_preferences):
        # Process preferences
        super().__init__(all_preferences)

    def initial_search(self):
        """
        This will create a search url from the passed preferences and scrape the results,
        saving them in self.search_results()
        :return:
        """
        query_string = urlencode(
            OrderedDict(term=preferences['location'],
                        within=str(int(self.distance)),
                        prices_min=int(self.min_beds),
                        prices_max=int(self.max_price),
                        bedrooms_min=int(self.min_beds),
                        bedrooms_max=int(self.min_beds),
                        isLive="true"))

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

        semi_processed_search_results = {}

        for k, v in unprocessed_search_results:
            same_formatting_1 = ['islivelistBool', 'prices', 'bedrooms', 'bathrooms', 'students', 'nonStudents', 'dss',
                                 'pets', 'isstudio', 'isshared', 'furnished', 'unfurnished', 'hasVideo',
                                 'videoViewingsAccepted', 'propertyTypes', 'hoursLive']
            same_formatting_2 = ['gardens', 'parkings', 'bills', 'fireplaces', 'availableFrom', 'minimumTenancy']

            if k in same_formatting_1:
                v = v.split(',')
                v[0] = v[0][3:]
                v = v[:-1]
                v = [int(i) for i in v]
                semi_processed_search_results[k] = v

            elif k in same_formatting_2:
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

        assert list(self.search_results.keys()) == property_ids, 'Error with search'

    def get_extra_details(self):
        """
        By utilising an undocumented API, we can get a few extra details for each property
        :return:
        """
        self.property_ids = list(self.search_results.keys())
        for property_id in self.property_ids:
            # The initial search is quite general, so first we filter down and remove ones that don't meet preferences
            # TODO: maybe make a method somewhere else in which certain preferences can be dealbreakers and some are ranked etc
            if self.search_results[property_id]['prices'] > preferences['max_price']:
                del self.search_results[property_id]

            elif self.search_results[property_id]['prices'] < preferences['min_price']:
                del self.search_results[property_id]

            elif self.search_results[property_id]['bedrooms'] > preferences['max_beds']:
                del self.search_results[property_id]

            elif self.search_results[property_id]['bedrooms'] < preferences['min_beds']:
                del self.search_results[property_id]

            # TODO: can use this to try filter out agents who worm their way in
            # elif 'we are proud to offer' in self.search_results[property_id]['description'].lower():

            else:
                # If the property matches the key preferences then get the extra details
                endpoint = "https://www.openrent.co.uk/search/propertiesbyid?"
                extra_info_from_id = requests.get(endpoint, params=[('ids', property_id)]).json()

                # Save this extra info
                self.search_results[property_id]['title'] = extra_info_from_id[0]['title']
                self.search_results[property_id]['description'] = extra_info_from_id[0]['description']
                self.search_results[property_id]['imageurl'] = extra_info_from_id[0]['imageUrl'][2:]
                self.search_results[property_id]['lastupdated'] = extra_info_from_id[0]['lastUpdated']

    def create_final_results(self):
        """
        The name of the keys used in the openrent responses have so far dictated how they are saved in
        self.search_results. But we want to change some of these names, along with the formats of some values in
        order to be consistent across platforms we search on. These final results are saved in self.results.

        :return:
        """
        self.results = {}
        for property_id in list(self.search_results.keys()):
            current_property = self.search_results[property_id]
            if current_property['islivelistBool'] == 1:
                self.results[property_id] = self.final_property_details.copy()
                self.results[property_id] = {'id': property_id,
                                             'title': current_property['title'],
                                             'price': current_property['prices'],
                                             'bills_included': str(bool(current_property['bills'])),
                                             'min_tenancy': current_property['minimumTenancy'],
                                             'description': current_property['description'],
                                             'available_from': (datetime.datetime.now() - datetime.timedelta(
                                                 days=current_property['availableFrom'])).strftime(
                                                 '%m-%d-%Y %H:%M:%S.%f'),
                                             'exact_location': f"{current_property['PROPERTYLISTLATITUDES']}, {current_property['PROPERTYLISTLONGITUDES']}",
                                             'furnishing': str(bool(current_property['furnished'])),
                                             'has_garden': str(bool(current_property['gardens'])),
                                             'student_friendly': str(bool(current_property['students'])),
                                             'dss': str(bool(current_property['dss'])),
                                             'fireplace': str(bool(current_property['fireplaces'])),
                                             'parking': str(bool(current_property['parkings'])),
                                             'rental_platforms': 'openrent',
                                             'last_updated': current_property['lastupdated'],
                                             'posted': (datetime.datetime.now() - datetime.timedelta(
                                                 hours=current_property['hoursLive'])).strftime('%m-%d-%Y %H:%M:%S.%f'),
                                             'url': openrent_id_to_link(property_id),
                                             'image_url': current_property['imageurl'],
                                             'video_viewings': str(bool(current_property['videoViewingsAccepted'])),
                                             'room_type': current_property['propertyTypes'],
                                             'bedrooms': current_property['bedrooms'],
                                             'bathrooms': current_property['bathrooms'],
                                             'pets': str(bool(current_property['pets']))
                                             }

    def main(self):
        self.initial_search()
        self.get_extra_details()
        self.create_final_results()
        self.save(self.results)


# Test
preferences = {
    'location': 'Southwark',
    'distance': 3,
    'min_price': 600,
    'max_price': 2000,
    'min_beds': 1,
    'max_beds': 1,
    'short_term_ok': False
}

o = OpenRent(preferences)
o.main()
