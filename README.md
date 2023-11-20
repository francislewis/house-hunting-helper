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

# When/Where information is gathered
|                  | SpareRoom (search)   | SpareRoom (id search) | OpenRent (search) | OpenRent (id search) |   |   |   |
|------------------|----------------------|-----------------------|-------------------|----------------------|---|---|---|
| id               | Y                    |                       | Y                 |                      |   |   |   |
| title            | Y                    |                       |                   | Y                    |   |   |   |
| price            | Y                    |                       | Y                 |                      |   |   |   |
| deposit          | Y                    |                       |                   |                      |   |   |   |
| bills_included   | N                    |                       | Y                 |                      |   |   |   |
| min_tenancy      | N                    |                       | Y                 |                      |   |   |   |
| description      | N  (255 chars)       |                       |                   | Y                    |   |   |   |
| available_from   | Y                    |                       | Y                 |                      |   |   |   |
| general_location | N                    |                       |                   |                      |   |   |   |
| exact_location   | Y                    |                       | Y                 |                      |   |   |   |
| nearest_station  | Y                    |                       |                   |                      |   |   |   |
| tube_zone        | Y                    |                       |                   |                      |   |   |   |
| furnishing       | N                    |                       | Y                 |                      |   |   |   |
| epc              | N                    |                       |                   |                      |   |   |   |
| has_garden       | N                    |                       | Y                 |                      |   |   |   |
| couples          | Y                    |                       |                   |                      |   |   |   |
| student_friendly | N                    |                       | Y                 |                      |   |   |   |
| dss              | N                    |                       | Y                 |                      |   |   |   |
| families_allowed | N                    |                       |                   |                      |   |   |   |
| smoking_allowed  | N                    |                       |                   |                      |   |   |   |
| fireplace        | N                    |                       |                   |                      |   |   |   |
| parking          | (search description) |                       | Y                 |                      |   |   |   |
| platform         | Auto                 |                       |                   |                      |   |   |   |
| last_updated     | N                    |                       |                   | Y                    |   |   |   |
| posted           | N                    |                       |                   |                      |   |   |   |
| url              | Auto from id         |                       | Auto from id      |                      |   |   |   |
| image_url        | Y                    |                       |                   | Y                    |   |   |   |
| video_viewings   | N                    |                       | Y                 |                      |   |   |   |
| room_type        | Y                    |                       |                   |                      |   |   |   |
| bedrooms         |                      |                       | Y                 |                      |   |   |   |
| bathrooms        |                      |                       | Y                 |                      |   |   |   |
| pets             |                      |                       | Y                 |                      |   |   |   |
|                  |                      |                       |                   |                      |   |   |   |
|                  |                      |                       |                   |                      |   |   |   |







