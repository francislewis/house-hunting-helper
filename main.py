from rental_platforms.spareroom import SpareRoom
from rental_platforms.openrent import OpenRent
from ranking import rank

preferences = {
    'location': 'Southwark',
    'distance': 4,
    'min_price': 600,
    'max_price': 2000,
    'min_beds': 1,
    'max_beds': 1,
    'short_term_ok': False,
    'work_location': 'SE10BE'
}

o = OpenRent(preferences)
s = SpareRoom(preferences)
o.main()
s.main()

rank()


