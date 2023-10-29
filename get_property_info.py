from collections import OrderedDict
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from helper_funcs import preprocess, id_to_link
import dateparser
from urllib.parse import urlencode


###################### Functions to extract specific features to filter by ######################
for i in range(1):
    def parse_location_table(soup):
        data = []
        table = soup.find('div', attrs={'id': 'LocalTransport'})
        if table:
            rows = table.find_all('tr')
            for row in rows[1:]:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele])

        return data


    def get_title(soup):
        return soup.find("h1", attrs={'class': "property-title"}).text.strip()


    def parse_feature_table(soup):
        def process_el(el):
            return el.text.strip()

        data = []
        tables = soup.find('div', attrs={'id': 'Features'}).find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [process_el(ele) for ele in cols]
                data.append([ele for ele in cols if ele])
        return data


    def available_from(features):
        date_text = [x[1] for x in features if x[0] == "Available From"][0]
        parsed = dateparser.parse(date_text)
        if not parsed:
            return date_text
        return str(parsed.date())


    def EPC_rating(features):
        rating = [x[1] for x in features if x[0] == "EPC Rating"]
        if rating:
            return rating[0]


    def has_garden(features):
        garden_found = [x[1] for x in features if x[0] == "Garden"]
        if garden_found:
            has_garden = None
            if garden_found[0] == "yes":
                has_garden = True
            elif garden_found[0] == "no":
                has_garden = False

            return has_garden


    def student_allowed(features):
        student_friendly = [x[1] for x in features if x[0] == "Student Friendly"]
        if student_friendly:
            student = None
            if student_friendly[0] == "yes":
                student = True
            elif student_friendly[0] == "no":
                student = False

            return student


    def bills_included(features):
        bills_included = [x[1] for x in features if x[0] == "Bills Included"]
        if bills_included:
            bills = None
            if bills_included[0] == "yes":
                bills = True
            elif bills_included[0] == "no":
                bills = False

            return bills


    def smoking_allowed(features):
        smoking_friendly = [x[1] for x in features if x[0] == "Smokers Allowed"]
        if smoking_friendly:
            smoking = None
            if smoking_friendly[0] == "yes":
                smoking = True
            elif smoking_friendly[0] == "no":
                smoking = False

            return smoking


    def families_allowed(features):
        family_friendly = [x[1] for x in features if x[0] == "Families Allowed"]
        if family_friendly:
            families = None
            if family_friendly[0] == "yes":
                families = True
            elif family_friendly[0] == "no":
                families = False

            return families


    def pets_allowed(features):
        pet_friendly = [x[1] for x in features if x[0] == "Pets Allowed"]
        if pet_friendly:
            pets = None
            if pet_friendly[0] == "yes":
                pets = True
            elif pet_friendly[0] == "no":
                pets = False

            return pets


    def furnished(features):
        furnishing = [x[1] for x in features if x[0] == "Furnishing"]
        if furnishing:
            return furnishing[0]


    def min_let(features):
        min_let = [x[1] for x in features if x[0] == "Minimum Tenancy"]
        if min_let:
            return min_let[0]


    def deposit_amount(features):
        deposit = [x[1] for x in features if x[0] == "Deposit"]
        if deposit:
            return deposit[0]


    # TODO: could maybe streamline this feature gathering process and put it into a single method which populates a dict

    # def populate_features(prop, features):
    #     """
    #
    #     :param prop: dict containing info for property
    #     :param features:
    #     :return:
    #     """
    #     garden_found = [x[1] for x in features if x[0] == "Garden"]
    #     if garden_found:
    #         has_garden = None
    #         if garden_found[0] == "yes":
    #             has_garden = True
    #         elif garden_found[0] == "no":
    #             has_garden = False
    #
    #         return has_garden

###################### Main Function ######################

def get_property_details(property_id):
    url = id_to_link(property_id)
    print(f'Gathering information on: {url}')

    # Start browser
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(url)

    # Wait to let it load
    time.sleep(1)

    # Get page source after loading
    page_source = driver.page_source

    # Close the browser
    driver.quit()

    # Use BeautifulSoup on the page source
    soup = BeautifulSoup(page_source, 'html.parser')

    preprocess(soup)

    price = soup.find_all("h3", {"class": "price-title"})[0]
    price = float(price.text[1:].replace(',', ''))

    desc = soup.find_all("div", {"class": "description"})[0]
    desc = desc.get_text().strip()
    desc.replace("\t", "")

    location = parse_location_table(soup)
    features = parse_feature_table(soup)

    prop = {'id': property_id, 'title': get_title(soup), 'location': location, 'price': price, 'description': desc,
            'available_from': available_from(features), 'EPC': EPC_rating(features), 'has_garden': has_garden(features),
            'Student Friendly': student_allowed(features), 'Furnishing': furnished(features),
            'Families Allowed': families_allowed(features), 'Pets Allowed': pets_allowed(features),
            'Smoking Allowed': smoking_allowed(features), 'Deposit': deposit_amount(features),
            'Minimum Tenancy': min_let(features), 'Bills Included': bills_included(features), 'Notified': False}

    print('Completed information gathering on listing')
    return prop

# TODO: could add google maps link, would be nicer to do by js clicking on elements though and getting proper link

# def directions_link(prop):
#     def maps_link(start_addr, end_addr):
#         query_string = urlencode(
#             OrderedDict(f="d",
#                         saddr=start_addr,
#                         daddr=end_addr,
#                         dirflg="r"))
#
#         return "http://maps.google.co.uk/?%s" % query_string
#
#     start_addr = ",".join(prop['title'].split(",")[1:])
#
#     return "Directions <{}|to {}>".format(
#         maps_link(start_addr, work_addr1), work_addr1)
# print(directions_link(prop))

# testing
# get_property_details(property_id = 1874378)