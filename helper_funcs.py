import urllib.request, json


def openrent_id_to_link(property_id):
    return ("https://www.openrent.co.uk/%s" % property_id)


def spareroom_id_to_link(property_id):
    return ("https://www.spareroom.co.uk/%s" % property_id)


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
