import urllib.request, json
from datetime import datetime, timedelta


def openrent_id_to_link(property_id):
    return "https://www.openrent.co.uk/%s" % property_id


def spareroom_id_to_link(property_id):
    return "https://www.spareroom.co.uk/%s" % property_id


def google_maps_link(location):
    """
    Create Google Maps link from 'latitude, longitude' string
    :param location: str, in format: latitude, longitude
    :return: str, link to location on Google Maps
    """
    # Currently removing a comma form the end, but it might be best to fix/stop this from being saved in the first place
    return f'https://maps.google.com/?q={location}'


def get_commute_time_tfl(start_loc, end_loc):
    try:
        url = f"https://api.tfl.gov.uk/Journey/JourneyResults/{start_loc}/to/{end_loc}?accessibilityPreference=NoRequirements&walkingSpeed=Fast"

        hdr = {
            # Request headers
            'Cache-Control': 'no-cache',
        }

        req = urllib.request.Request(url, headers=hdr)
        req.get_method = lambda: 'GET'
        response = urllib.request.urlopen(req)
        # print(response.getcode())
        total_duration = json.loads(response.read())['journeys'][0]['duration']
        return total_duration

    except Exception as e:
        print(e)
        return f'error: {e}'

def convert_date_to_standard(date_string):
    # Remove any spaces in input
    date_string = str(date_string).replace(' ', '')

    if date_string == 'Now':
        return datetime.now().strftime('%Y:%m:%d:%H')

    formats = [
        '%d%b%Y',
        '%d%b%Y%H:%M:%S.%f',
        '%m-%d-%Y%H:%M:%S.%f',
        '%Y:%m:%d:%H',
        '%Y-%m-%d%H:%M:%S.%f',
        '%Y-%m-%d',
        '%Y-%m-%d%H:%M:%S'
    ]

    for fmt in formats:
        try:
            # Try parsing the date string with the current format
            return datetime.strptime(date_string, fmt).strftime('%Y:%m:%d:%H')
        except ValueError:
            continue

    # If none of the formats match
    print(f"Unsupported date format: {date_string}, saving input string")
    return date_string
def convert_time_ago_to_datetime(time_string):
    # around a month ago
    # around 2 weeks ago
    parts = time_string.split()
    now = datetime.now()
    if parts[0] == 'around':
        if parts[1] == 'a':
            amount = 1
            unit = parts[2]
        else:
            amount = int(parts[1])
            unit = parts[2]

        if unit in ['second', 'seconds']:
            delta = timedelta(seconds=amount)
        elif unit in ['minute', 'minutes']:
            delta = timedelta(minutes=amount)
        elif unit in ['hour', 'hours']:
            delta = timedelta(hours=amount)
        elif unit in ['day', 'days']:
            delta = timedelta(days=amount)
        elif unit in ['week', 'weeks']:
            delta = timedelta(weeks=amount)
        elif unit in ['month', 'months']:
            delta = timedelta(days=amount * 30)  # Approximating months as 30 days
        new_time = now - delta
        return new_time.strftime('%Y:%m:%d:%H')
    else:
        return now.strftime('%Y:%m:%d:%H')


def find_key(json_object, keys):
    """
    Recursively search for the first occurrence of any key from 'keys' in the JSON object and return associated value.

    :param json_object: The JSON object to search through
    :param keys: A list of keys to search for in order of preference
    :return: The value associated with the first found key, or None if none of the keys are found
    """
    if isinstance(json_object, dict):
        for key in keys:
            if key in json_object:
                return json_object[key]
        for value in json_object.values():
            result = find_key(value, keys)
            if result is not None:
                return result
    elif isinstance(json_object, list):
        for item in json_object:
            result = find_key(item, keys)
            if result is not None:
                return result
    return None

