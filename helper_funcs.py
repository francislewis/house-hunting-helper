def preprocess(soup):
    ticks = soup.find_all("i", attrs={'class': 'fa fa-check'})
    for tick in ticks:
        if tick.text == "":
            tick.string = "yes"

    ticks = soup.find_all("i", attrs={'class': 'fa fa-times'})
    for tick in ticks:
        if tick.text == "":
            tick.string = "no"

def openrent_id_to_link(property_id):
    return ("https://www.openrent.co.uk/%s" % property_id)

def openrent_link_to_id(url):
    return url.split('/')[-1]

def spareroom_id_to_link(property_id):
    return ("https://www.spareroom.co.uk/%s" % property_id)