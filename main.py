import time
import spareroom, openrent
from database import write_property_details_to_db, does_row_exist, initalise_db


def run_search(preferences, max_properties_per_platform):
    start_time = time.time()
    # Run initial searches to get list of suitable property ids
    or_ids = openrent.get_available_properties(preferences, max_prop=max_properties_per_platform)
    sr_ids = spareroom.search_for_spareroom_ids(preferences, max_prop=max_properties_per_platform)

    initalise_db()

    for or_id in or_ids:
        if not does_row_exist(or_id):
            property_details = openrent.get_property_details(or_id)
            write_property_details_to_db(property_details)
        else:
            print('Database entry already exists for this id - skipping')

    for sr_id in sr_ids:
        try:
            if not does_row_exist(sr_id):
                property_details = spareroom.getspareoominfo(sr_id)
                write_property_details_to_db(property_details)
            else:
                print('Database entry already exists for this id - skipping')
        except TypeError:
            print('SpareRoom: Issue encountered, likely due to non-specific Location term. Search spareroom.com for '
                  'your location term in preferences and ensure it returns a list of proprties, rather than a further '
                  'choice of location. E.g. Brixton can be Brixton - London or Brixton - Devon')

    end_time = time.time()
    elapsed_time = end_time - start_time

    if elapsed_time > 60:
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        formatted_time = f"{minutes} minute(s) and {seconds:.1f} second(s)"

    else:
        formatted_time = f"{elapsed_time:.1f} seconds"

    print(f"Search for {len(sr_ids) + len(or_ids)} completed in {formatted_time} and results saved in database.")


# For testing:
preferences = {
    'location': 'Southwark',
    'distance': 3,
    'min_price': 600,
    'max_price': 2000,
    'min_beds': 1,
    'max_beds': 1,
    'short_term_ok': False
}

run_search(preferences=preferences, max_properties_per_platform=20)
