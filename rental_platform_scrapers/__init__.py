from databases.sqlite import SQLiteDatabase


class RentalPlatform:
    """
    Components that are shared across every rental platform (openrent, spare room etc.) during scraping/processing
    """
    final_property_dict = None

    def __init__(self, all_preferences):
        self.results = None
        self.search_results = None
        self.property_ids = None
        self.failed_fields = None

        self.all_preferences = all_preferences

        # Process the preferences that are shared between all platforms
        # Check all the required preferences have been passed
        required_preferences = ['max_price', 'location', 'distance', 'min_beds']
        for required_preference in required_preferences:
            if required_preference not in self.all_preferences:
                raise TypeError(f"Missing value for required preference: '{required_preference}'")

        self.max_price = int(all_preferences['max_price'])
        self.location = str(all_preferences['location'].lower())
        self.distance = int(all_preferences['distance'])
        self.min_beds = int(all_preferences['min_beds'])

        # Now the optional preferences
        if 'max_properties' in self.all_preferences:
            self.max_properties = self.all_preferences['max_properties']
        else:
            self.max_properties = None
        if 'max_beds' in self.all_preferences:
            self.max_beds = self.all_preferences['max_beds']
        else:
            self.max_beds = 1
        if 'min_price' in self.all_preferences:
            self.min_price = self.all_preferences['min_price']
        else:
            self.min_price = 0
        if 'short_term_ok' in self.all_preferences:
            self.short_term_ok = self.all_preferences['short_term_ok']
        else:
            self.short_term_ok = False

        # Search preferences should be saved as local variables within the object,
        # results should be saved in self.results as a dict of dict, with a copy of self.final_property_details per id

        # Save the results dict to self.final_property_details
        self.full_results_dict()
        self.final_property_details = RentalPlatform.final_property_dict

        # Create database object to save the results to disk
        self.db = SQLiteDatabase(self.final_property_details)

    # Dict for the final results to ensure consistency, @classmethod so this dict can be copied without instantiating
    # an entire RentalPlatform object.
    # TODO: a seperate dataclass might be better here
    @classmethod
    def full_results_dict(cls):
        RentalPlatform.final_property_dict = {'id': 'unknown',
                                              'title': 'unknown',
                                              'price': 'unknown',
                                              'deposit': 'unknown',
                                              'bills_included': 'unknown',
                                              'min_tenancy': 'unknown',
                                              'description': 'unknown',
                                              'available_from': 'unknown',
                                              'general_location': 'unknown',
                                              'exact_location': 'unknown',
                                              'google_maps_link': 'unknown',
                                              'nearest_station': 'unknown',
                                              'tube_zone': 'unknown',
                                              'furnishing': 'unknown',
                                              'epc': 'unknown',
                                              'has_garden': 'unknown',
                                              'couples': 'unknown',
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
                                              'pets': 'unknown',
                                              'notified': 'unknown',
                                              'ranking': 'unknown',
                                              'date_found': 'unknown',
                                              'available': 'unknown',
                                              'date_let': 'unknown',
                                              'full_json': 'unknown',
                                              'req_gender': 'unknown',
                                              'req_occupation': 'unknown'
                                              }

    def save(self, results):
        """
        results should be a dict of dict, keyed by property id
        :param results:
        :return:
        """

        for id in results:
            self.db.insert_data_into_table(results[id])

    def check_exists(self, property_id):
        """
        Check if a row exists in attached database object, return boolean

        :param property_id: str of key/id of row to check
        :return: bool
        """
        return self.db.does_row_exist(property_id)

    def main(self):
        pass
