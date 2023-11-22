from database import SQLiteDatabase


class RentalPlatform():
    final_property_dict = None

    def __init__(self, all_preferences):
        self.results = None
        self.search_results = None
        self.property_ids = None

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
        if 'work_location' in self.all_preferences:
            self.work_location = self.all_preferences['work_location'].replace(' ','')
        else:
            self.work_location = 'SE18SW'  # London Waterloo Station

        # Search preferences should be saved as local variables within the object,
        # results should be saved in self.results as a dict of dict, with a copy of self.final_property_details per id

        # Save the results dict to self.final_property_details
        self.results_dict()
        self.final_property_details = RentalPlatform.final_property_dict

    # Dict for the final results to ensure consistency, @classmethod so this dict can be copied without instantiating
    # an entire RentalPlatform object.
    @classmethod
    def results_dict(self):
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
                                              'work_location': 'unknown',
                                              'time_to_work_pub_trans': 'unknown',
                                              'time_to_work_cycle': 'unknown',
                                              'notified': 'unknown',
                                              'ranking': 'unknown'
                                              }

    def save(self, results):
        """
        results should be a dict of dict, keyed by property id
        :param results:
        :return:
        """
        db = SQLiteDatabase(self.final_property_details)

        for id in results:
            db.insert_data_into_table(results[id])
        # TODO: maybe try mongodb? could also keep SQLite option as it's more compatible?

    def main(self):
        pass
