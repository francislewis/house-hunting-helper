from rental_platform_scrapers.spareroom import SpareRoom
from rental_platform_scrapers.openrent import OpenRent
from ranking.simple import SimpleRank

preferences = {
    'location': 'Swansea',
    'distance': 4,
    'min_price': 600,
    'max_price': 2000,
    'min_beds': 1,
    'max_beds': 1,
    'short_term_ok': False
}

o = OpenRent(preferences)
s = SpareRoom(preferences)
o.main()
s.main()

rank = SimpleRank()


