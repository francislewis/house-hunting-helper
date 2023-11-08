from database import fetch_property_details_from_db

ids = [1869082, 1811237, 1871704, 1845781, 1874378]

for id in ids:
    property = fetch_property_details_from_db(id)
    print(property)