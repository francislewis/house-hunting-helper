import get_property_info, initial_search
from helper_funcs import openrent_link_to_id
from database import write_property_details_to_db

# For testing:
preferences = {
    'location': 'London',
    'distance': 10,
    'min_price': 600,
    'max_price': 2000,
    'min_beds': 1,
    'max_beds': 1
}


links = initial_search.get_available_properties(preferences, max_prop=250)

for i in range(5):
    property_id = openrent_link_to_id(links[i])

    # Get the property details from OpenRent
    property_details = get_property_info.get_property_details(property_id)
    # print(property_details)

    write_property_details_to_db(property_details)

    # if does_row_exist(property_id):
    #     print('Property details already saved, skipping')
    # else:
    #     notify(property_details)
    #     write_property_details_to_db(property_details)






