# house-hunting-helper
 
Acknowledgements: 
- OpenRent Scraping modified from [TomHodson/uk_rentals_bot](https://github.com/TomHodson/uk_rentals_bot/tree/main) and [afiodorov/openrent](https://github.com/afiodorov/openrent) 
- SpareRoom Scraping modified from: [eonlight/roomfinder](https://github.com/eonlight/roomfinder)

To-Do:
- add unit tests (can test with both valid/invalid api/json responses to ensure it's safe)
- Add notifications (email/trello/slack etc.)
- Some work is needed on consistent types/structure of values being written to the db, since they have to be consistent across platforms in order for the ranking to be effective

Improvements:
- Add RightMove:
  - https://github.com/toby-p/rightmove_webscraper.py
- Add location/time to work in database:
  - https://openrouteservice.org/dev/#/home?tab=1
  - https://api.tfl.gov.uk/swagger/ui/index.html?url=/swagger/docs/v1#!/Journey/Journey_JourneyResults
- Add extra search filters (like min tenancy), before saving to database?
- Add html generation for a basic UI
- Add Google Sheets integration

# When/Where information is gathered
TODO: this needs to be updated

room_type for openrent needs to be processed further:
- 1 = 
- 2 = 1 bed flat
- 3 = room in shared house

|                         | SpareRoom (search)   | SpareRoom (id search) | OpenRent (search) | OpenRent (id search) |   |   |   |
|-------------------------|----------------------|-----------------------|-------------------|----------------------|---|---|---|
| id                      | Y                    |                       | Y                 |                      |   |   |   |
| title                   | Y                    |                       |                   | Y                    |   |   |   |
| price                   | Y                    |                       | Y                 |                      |   |   |   |
| deposit                 | Y                    |                       |                   |                      |   |   |   |
| bills_included          | N                    |                       | Y                 |                      |   |   |   |
| min_tenancy             | N                    |                       | Y                 |                      |   |   |   |
| description             | N  (255 chars)       | Y                     |                   | Y                    |   |   |   |
| available_from          | Y                    |                       | Y                 |                      |   |   |   |
| general_location        | N                    |                       |                   |                      |   |   |   |
| exact_location          | Y                    |                       | Y                 |                      |   |   |   |
| nearest_station         | Y                    |                       |                   |                      |   |   |   |
| tube_zone               | Y                    |                       |                   |                      |   |   |   |
| furnishing              | N                    |                       | Y                 |                      |   |   |   |
| epc                     | N                    |                       |                   |                      |   |   |   |
| has_garden              | N                    |                       | Y                 |                      |   |   |   |
| couples                 | Y                    |                       |                   |                      |   |   |   |
| student_friendly        | N                    |                       | Y                 |                      |   |   |   |
| dss                     | N                    |                       | Y                 |                      |   |   |   |
| families_allowed        | N                    |                       |                   |                      |   |   |   |
| smoking_allowed         | N                    |                       |                   |                      |   |   |   |
| fireplace               | N                    |                       |                   |                      |   |   |   |
| parking                 | (search description) |                       | Y                 |                      |   |   |   |
| platform                | Auto                 |                       |                   |                      |   |   |   |
| last_updated            | N                    |                       |                   | Y                    |   |   |   |
| posted                  | N                    |                       |                   |                      |   |   |   |
| url                     | Auto from id         |                       | Auto from id      |                      |   |   |   |
| image_url               | Y                    |                       |                   | Y                    |   |   |   |
| video_viewings          | N                    |                       | Y                 |                      |   |   |   |
| room_type               | Y                    |                       |                   |                      |   |   |   |
| bedrooms                |                      |                       | Y                 |                      |   |   |   |
| bathrooms               |                      |                       | Y                 |                      |   |   |   |
| pets                    |                      |                       | Y                 |                      |   |   |   |
| work_location           |                      |                       |                   |                      |   |   |   |
| time_to_works_pub_trans |                      |                       |                   |                      |   |   |   |
| time_to_work_cycle      |                      |                       |                   |                      |   |   |   |
| notified                |                      |                       |                   |                      |   |   |   |








