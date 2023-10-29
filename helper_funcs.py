def preprocess(soup):
    ticks = soup.find_all("i", attrs={'class': 'fa fa-check'})
    for tick in ticks:
        if tick.text == "":
            tick.string = "yes"

    ticks = soup.find_all("i", attrs={'class': 'fa fa-times'})
    for tick in ticks:
        if tick.text == "":
            tick.string = "no"

def id_to_link(property_id):
    return ("https://www.openrent.co.uk/%s" % property_id)

def link_to_id(url):
    return url.split('/')[-1]
