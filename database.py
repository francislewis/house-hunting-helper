import sqlite3

def initalise_db():
    # Connect to a database (or create it if it doesn't exist)
    conn = sqlite3.connect('saved_properties.db')

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Create a table for properties
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS properties (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    location TEXT,
                    platform_location TEXT,
                    price REAL,
                    description TEXT,
                    available_from TEXT,
                    EPC TEXT,
                    has_garden BOOLEAN,
                    student_friendly BOOLEAN,
                    furnishing TEXT,
                    families_allowed BOOLEAN,
                    pets_allowed BOOLEAN,
                    smoking_allowed BOOLEAN,
                    deposit REAL,
                    min_tenancy TEXT,
                    bills_included BOOLEAN,
                    nearest_station TEXT,
                    notified BOOLEAN,
                    link TEXT,
                    fireplace BOOLEAN,
                    parking BOOLEAN,
                    rental_platforms TEXT
                )
            ''')

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

def write_property_details_to_db(prop):
    """
    Write a dict of details (for a single property) to a SQLite database located in saved_properties/database.db
    :param prop: dict of property details
    :return:
    """
    if prop is None:
        print('Error with page')
        return 0
    # Check entry for id doesn't already exist:
    if not does_row_exist(prop['id']):

        # Connect to a database (or create it if it doesn't exist)
        conn = sqlite3.connect('saved_properties.db')

        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        # Create a table for properties
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                location TEXT,
                platform_location TEXT,
                price REAL,
                description TEXT,
                available_from TEXT,
                EPC TEXT,
                has_garden BOOLEAN,
                student_friendly BOOLEAN,
                furnishing TEXT,
                families_allowed BOOLEAN,
                pets_allowed BOOLEAN,
                smoking_allowed BOOLEAN,
                deposit REAL,
                min_tenancy TEXT,
                bills_included BOOLEAN,
                nearest_station TEXT,
                notified BOOLEAN,
                link TEXT,
                fireplace BOOLEAN,
                parking BOOLEAN,
                rental_platforms TEXT
            )
        ''')

        # Insert data from the 'prop' dictionary into the 'properties' table
        cursor.execute('''
            INSERT INTO properties (
                id, title, location, platform_location, price, description, available_from, EPC,
                has_garden, student_friendly, furnishing, families_allowed,
                pets_allowed, smoking_allowed, deposit, min_tenancy, bills_included, nearest_station, 
                notified, link, fireplace, parking, rental_platforms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prop['id'], prop['title'], str(prop['location']), str(prop['platform_location']),
            prop['price'], prop['description'],
            prop['available_from'], prop['EPC'], int(prop['has_garden']),
            int(prop['Student Friendly']), prop['Furnishing'], int(prop['Families Allowed']),
            int(prop['Pets Allowed']), int(prop['Smoking Allowed']), prop['Deposit'],
            prop['Minimum Tenancy'], int(prop['Bills Included']), str(prop['nearest_station']),
            (prop['Notified']), str(prop['link']), int(prop['Fireplace']), int(prop['Parking']),
            str(prop['rental_platforms'])
        ))

        # Commit the changes
        conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

    else:
        print('Database entry already exists for this id - skipping')


def fetch_property_details_from_db(property_id):
    """
    From a property id, check if it is saved in the SQLite database saved_properties/database.db and if so return a dict
    of property details from the database row
    :param property_id:
    :return:
    """
    # Connect to the database
    conn = sqlite3.connect('saved_properties.db')
    cursor = conn.cursor()

    # Fetch property data from the 'properties' table
    cursor.execute('''
        SELECT * FROM properties WHERE id = ?
    ''', (property_id,))

    # Retrieve the first result (assuming property_id is unique)
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # If no result found, return None
    if result is None:
        return None

    # Create a dictionary from the retrieved values
    prop = {
        'id': result[0],
        'title': result[1],
        'location': result[2],
        'platform_location': result[3],
        'price': result[4],
        'description': result[5],
        'available_from': result[6],
        'EPC': result[7],
        'has_garden': bool(result[8]),
        'student_friendly': bool(result[9]),
        'furnishing': result[10],
        'families_allowed': bool(result[11]),
        'pets_allowed': bool(result[12]),
        'smoking_allowed': bool(result[13]),
        'deposit': result[14],
        'min_tenancy': result[15],
        'bills_included': bool(result[16]),
        'nearest_station': result[17],
        'notified': bool(result[18]),
        'link': result[19],
        'fireplace': bool(result[20]),
        'parking': bool(result[21]),
        'rental_platforms': result[22]
    }

    return prop


def does_row_exist(property_id):
    # Connect to the database
    conn = sqlite3.connect('saved_properties.db')
    cursor = conn.cursor()

    # Check if a row with the specified ID exists in the 'properties' table
    cursor.execute('''
        SELECT 1 FROM properties WHERE id = ? LIMIT 1
    ''', (property_id,))

    # Fetch the result
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Return True if a row exists, False otherwise
    return result is not None


def get_all_property_ids():
    # Connect to the database
    conn = sqlite3.connect('saved_properties.db')
    cursor = conn.cursor()

    # Fetch all IDs from the 'properties' table
    cursor.execute('''
        SELECT id FROM properties
    ''')

    # Retrieve the results
    results = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Extract the IDs from the results and return as a list
    return [result[0] for result in results]


def get_unnotified_property_ids():
    # Connect to the database
    conn = sqlite3.connect('saved_properties.db')
    cursor = conn.cursor()

    # Fetch IDs of properties with notified set to False
    cursor.execute('''
        SELECT id, rental_platforms FROM properties WHERE notified = 0
    ''')

    # Retrieve the results
    results = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Extract the IDs from the results and return as a list
    # return [result[0] for result in results]
    return results

