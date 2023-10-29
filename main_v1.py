import os
import get_property_info, initial_search
from helper_funcs import link_to_id
from notifications import notify
import pickle
from pathlib import Path

# For testing:
preferences = {
    'location': 'London',
    'distance': 10,
    'min_price': 600,
    'max_price': 2000,
    'min_beds': 1,
    'max_beds': 1
}

url = initial_search.create_search_URL(**preferences)
max_properties = initial_search.get_initial_num_properties(url, delay_time=4)
links = initial_search.get_available_properties(url, max_num=max_properties)

for i in range(5):
    property_id = link_to_id(links[i])

    # Get the property details from OpenRent
    property_details = get_property_info.get_property_details(property_id)
    # print(property_details)

    # Create directory to save property info in
    save_folder = os.path.join(os.getcwd(), 'saved_properties')
    os.makedirs(save_folder, exist_ok=True)

    property_save_path = os.path.join(save_folder, f'{property_id}.pkl')

    # Check if property previously saved
    saved_file = Path(property_save_path)
    if saved_file.is_file():
        print('Property details already saved, skipping')
        #TODO: check if updates

    else:
        print('New Property - saving')
        with open(property_save_path, 'wb') as f:
            # Notify of new property - maybe do this somewhere else?
            notify(property_details)

            # Write to file
            pickle.dump(property_details, f)






