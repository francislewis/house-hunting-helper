# house-hunting-helper

The aim of this project is to make the process of finding a flat to rent easier for tenants. Currently, it's mostly
focused around finding 1/2 beds in London, since this is what I'm aiming to use it for myself, and I have some domina knowledge.
This is still **very much a work in progress** but I thought I'd open source it along the way in case it helps others.


 ### Immediate Plan:
- Allow for more minimal data collection with key features:
  - Link/id, price per month, number of beds, location (post code?), first seen/available, last seen/not available.
- Add some extra searches to try and fill in all of the possible information (I think it'll have to involve scraping individual web pages directly)
  - Should complete the scraping side so the data is good
- Add in a scheduler so I can run a set query on schedule with a flag or something and collect data
- At some point all of the rental_platform_scrapers could do with refactoring but for now if it works I want to focus on new features
- Re-think the DB schema to have a searches table, all properties from searches will go into same table

### Future Improvement Ideas:
- Additional platforms
  - Add RightMove:
    - https://github.com/toby-p/rightmove_webscraper.py
  - Zoopla
    - They actually have an API
      - https://developer.zoopla.co.uk/docs/
  - https://www.primelocation.com/
  - On the market
- Add location/time to work functionality in searches (functions exist in helper_funcs.py):
  - https://openrouteservice.org/dev/#/home?tab=1
  - https://api.tfl.gov.uk/swagger/ui/index.html?url=/swagger/docs/v1#!/Journey/Journey_JourneyResults
- Frontend
- Add extra search filters (like min tenancy)?
- Add Google Sheets integration

### General notes/todo
- add unit tests (can test with both valid/invalid api/json responses to ensure it's safe)
- Add notifications (email/trello/slack etc.)
- Some work is needed on consistent types/structure of values being written to the db, since they have to be consistent across platforms in order for the ranking to be effective
- Being able to track historic prices would be good, but only if we have prior info
  - The use case here is gathering data on which properties get let very quickly (proxy for desirable property)
    - Could do some ML stuff with enough data
  - Instead of only finding available properties, if a property is unavailable, first check to see if we have a previous db entry for it, if so then save it with the date it was let
- Save if a property is posted by an agent etc. (using the start of the description trick too)
- Sometimes get `HTTP Error 429: Too Many Requests` - should catch this and deal with it properly, maybe introduce a slower rate if it's hit. Think it's only happening on spareroom currently
- https://findmyarea.co.uk/ this is basically very similar, but apparently only uses rightmove and only ranks the areas (still very useful)
  -https://github.com/lukas-slezevicius/london-apartment-rental-data/blob/main/scripts/get_area_data.py this is using an api from findmyarea
- Batch Running:
  - Going to add a feature flag for scheduled running
  - When run on schedule, we need to ignore time frames for currently listed properties if we don't know when they were first posted
  - For new properties that haven't been seen, we can take the date it's posted as the start date and the day it gets removed/marked as let as the end time

### Acknowledgements: 
- OpenRent Scraping modified from [TomHodson/uk_rentals_bot](https://github.com/TomHodson/uk_rentals_bot/tree/main) and [afiodorov/openrent](https://github.com/afiodorov/openrent) 
- SpareRoom Scraping modified from: [eonlight/roomfinder](https://github.com/eonlight/roomfinder)


### When/Where information is gathered
TODO: this needs to be updated

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
| notified                |                      |                       |                   |                      |   |   |   |
| full_json               |                      |                       |                   |                      |   |   |   |

room_type for openrent needs to be processed further:
- 1 = 
- 2 = 1 bed flat?
- 3 = room in shared house?

DB design:
properties table - maybe one just for London for now? this shouldn't include bits on travel to work time etc.

Then want to be able to run custom searches (I think this is going to have to run some live searches). 
Do these live searches end up in properties table and then query from there? So we have a big ever growing properties table?








