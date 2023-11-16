# house-hunting-helper
 
Acknowledgements: 
- OpenRent Scraping modified from: [afiodorov/openrent](https://github.com/afiodorov/openrent)
- SpareRoom Scraping modified from: [eonlight/roomfinder](hhttps://github.com/eonlight/roomfinder)

Re-structure plan:
- Class for each platform with some set methods
- Unit tests for each method (with valid response and invalid response)

To-Do:
- Add notifications (email/trello/slack etc.)

Improvements:
- Headless browser currently requires Firefox to be installed, could instead:
  - Use an [undocumented API](https://github.com/TomHodson/uk_rentals_bot/blob/main/src/openrent.py)
  - Use selenium/xfb as a browser?
- Add RightMove:
  - https://github.com/toby-p/rightmove_webscraper.py
- Add location/time to work in database:
  - https://openrouteservice.org/dev/#/home?tab=1
- Add ranking by weighting different factors
- Add extra search filters (like min tenancy), before saving to database









