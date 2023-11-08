from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
import math
from helper_funcs import preprocess, openrent_id_to_link
from urllib.parse import urlencode
from collections import OrderedDict
import json


def get_available_properties(preferences, max_prop=200, delay_time=2):
    """
    Get the number of available properties in the filtered search
    :param url: the url of the Openrent search page to query
    :param delay_time: time in seconds to delay before reading info from the page to allow it to load.
    May have to increase this number when internet connection is slow
    :return:
    """

    """
      location - str - search location
      distance - int - distance in kms
          Interesting fact, if you pass x.y as a float to the URL, the distance used is round(x/y)
          - might be some remote code execution on OpenRent?
      min_price - int - Minimum price per month in £GBP
      max_price - int - Maximum price per month in £GBP
      min_beds - int - Minimum number of bedrooms
      max_beds - int - Maximum number of bedrooms

      requires:
      urllib.parse.urlencode
      collections.OrderedDict
      """

    for key in ['location', 'distance', 'min_price', 'max_price', 'min_beds', 'max_beds']:
        if key not in preferences:
            raise KeyError(f"Key '{key}' not found in preferences, please include")

    query_string = urlencode(
        OrderedDict(term=preferences['location'],
                    within=str(int(preferences['distance'])),
                    prices_min=int(preferences['min_price']),
                    prices_max=int(preferences['max_price']),
                    bedrooms_min=int(preferences['min_beds']),
                    bedrooms_max=int(preferences['max_beds']),
                    isLive="true"))

    url = ("http://www.openrent.co.uk/properties-to-rent/?%s" % query_string)
    print(f'Search URL: {url}')

    # Start browser
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(url)

    # Wait to let it load
    time.sleep(delay_time)

    # Get page source after loading
    page_source = driver.page_source

    # Close the browser
    driver.quit()

    # Use BeautifulSoup on the page source
    soup = BeautifulSoup(page_source, 'html.parser')

    filter_tag = soup.find("span", attrs={'class': "filter-info"})

    # The number of available properties
    num_properties = re.search(r"\b(\d{1,3})\b", str(filter_tag)).group(1)

    print(f'{num_properties} filtered properties available')

    # return num_properties

    max_num = math.ceil(min(float(max_prop),float(num_properties)))

    # Get 20 new properties every time you scroll down and wait
    refreshes = math.ceil((int(max_num)/20))

    # Start browser
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(url)

    def scroll_to_bottom():
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay_time)

    # Scroll down and wait 3 seconds four times
    for _ in range(refreshes):
        scroll_to_bottom()

    # Get the page source after scrolling
    page_source = driver.page_source

    # Close the browser
    driver.quit()

    # Use BeautifulSoup on the page source
    soup = BeautifulSoup(page_source, 'html.parser')

    preprocess(soup)

    latest_links = [x['href'][1:] for x in soup.find_all("a", class_="pli clearfix")]

    print(f'{len(latest_links)} properties found')

    return latest_links


# # For testing:
# preferences = {
#     'location': 'London',
#     'distance': 10,
#     'min_price': 600,
#     'max_price': 2000,
#     'min_beds': 1,
#     'max_beds': 1
# }
#
# url = create_search_URL(**preferences)
# max_properties = get_initial_num_properties(url, delay_time=4)
# links = get_available_properties(url, max_num=max_properties)
#
# for link in links:
#     print(make_link(link))

def load_preferences_from_json(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            preferences = json.load(file)
        return preferences
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file_path}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Unable to decode JSON in '{json_file_path}'.")
        return {}

# # Example: Load preferences from the JSON file
# json_file_path = 'preferences.json'
# user_preferences = load_preferences_from_json(json_file_path)
#
# # Print the loaded preferences
# print("User Preferences:")
# print("Min Cost:", user_preferences.get("min_cost", "Not specified"))
# print("Max Cost:", user_preferences.get("max_cost", "Not specified"))
# print("Location:", user_preferences.get("location", "Not specified"))
