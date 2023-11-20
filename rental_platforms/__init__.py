class RentalPlatform():
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

        # Search preferences should be saved as local variables within the object

        # # Dict for the final results to ensure consistency
        # self.final_property_details = {'id': 'unknown',
        #                           'title': 'unknown',
        #                           'price': 'unknown',
        #                           'deposit': 'unknown',
        #                           'bills_included': 'unknown',
        #                           'min_tenancy': 'unknown',
        #                           'description': 'unknown',
        #                           'available_from': 'unknown',
        #                           'general_location': 'unknown',
        #                           'exact_location': 'unknown',
        #                           'nearest_station': 'unknown',
        #                           'tube_zone': 'unknown',
        #                           'furnishing': 'unknown',
        #                           'epc': 'unknown',
        #                           'has_garden': 'unknown',
        #                           'couples': 'unknown',
        #                           'student_friendly': 'unknown',
        #                           'dss': 'unknown',
        #                           'families_allowed': 'unknown',
        #                           'smoking_allowed': 'unknown',
        #                           'fireplace': 'unknown',
        #                           'parking': 'unknown',
        #                           'rental_platforms': 'unknown',
        #                           'last_updated': 'unknown',
        #                           'posted': 'unknown',
        #                           'url': 'unknown',
        #                           'image_url': 'unknown',
        #                           'video_viewings': 'unknown',
        #                           'room_type': 'unknown',
        #                           }


    def save(self, results):
        """
        results should be a dict of dict, keyed by property id
        :param results:
        :return:
        """
        print(len(results))
        print(results)
        # TODO: maybe try mongodb? could also keep SQLite option as it's more compatible?

    def main(self):
        pass
