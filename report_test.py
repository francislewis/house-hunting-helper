# test_dict = {'id': 'unknown',
#        'title': 'unknown',
#        'price': 'unknown',
#        'deposit': 'unknown',
#        'bills_included': 'unknown',
#        'min_tenancy': 'unknown',
#        'description': 'unknown',
#        'available_from': 'unknown',
#        'general_location': 'unknown',
#        'exact_location': 'unknown',
#        'google_maps_link': 'unknown',
#        'nearest_station': 'unknown',
#        'tube_zone': 'unknown',
#        'furnishing': 'unknown',
#        'epc': 'unknown',
#        'has_garden': 'unknown',
#        'couples': 'unknown',
#        'student_friendly': 'unknown',
#        'dss': 'unknown',
#        'families_allowed': 'unknown',
#        'smoking_allowed': 'unknown',
#        'fireplace': 'unknown',
#        'parking': 'unknown',
#        'platform': 'unknown',
#        'last_updated': 'unknown',
#        'posted': 'unknown',
#        'url': 'unknown',
#        'image_url': 'unknown',
#        'video_viewings': 'unknown',
#        'room_type': 'unknown',
#        'bedrooms': 'unknown',
#        'bathrooms': 'unknown',
#        'pets': 'unknown',
#        'work_location': 'unknown',
#        'time_to_work_pub_trans': 'unknown',
#        'time_to_work_cycle': 'unknown',
#        'notified': 'unknown',
#        'ranking': 'unknown'
#        }
#
# html = '<html><head><title>Classified Ads</title><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css"></head><body>'
# html += '<table class="table">'
# html += '<thead><tr>'
# for field in test_dict.keys():
#     html += '<th>{field}</th>'.format(field=field.replace('_', ' ').capitalize())
# html += '</tr></thead><tbody>'
# # for i, room in enumerate(data_dict.values()):
# #     available_time = room['available_from']
# #
# #         htmlclass = 'success'
# #         html += '<tr class="{css}">'.format(css=htmlclass)
# #         for sub_field in field:
# #             if field == 'id':
# #                 url = '{location}/{endpoint}{id}'.format(location=self.location, endpoint=self.details_endpoint,
# #                                                          id=room['id'])
# #                 html += '<td><a target="_blank" href="{url}">{field}</td>'.format(url=url, field=room[field])
# #             elif field == 'images':
# #                 pics = ['<a href="{url}"><img src="{src}" height="100" width="100"></a>'.format(url=img, src=img)
# #                         for img in room['images']]
# #                 images = ''
# #                 for i in range(5):
# #                     images += pics[i] if len(pics) > i else ''
# #                 html += '<td>{images}</td>'.format(images=images)
# #             else:
# #                 html += '<td>{value}</td>'.format(value=room[field])
# #         html += '</tr>'
# #         break
#
# html += '<tbody></table><script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/js/bootstrap.min.js"></script></body></html>'
#
# with open('test.json'.replace('.json', '.html'), 'w') as f:
#        f.write(html.encode('utf-8'))

# from database import SQLiteDatabase
# from rental_platforms import RentalPlatform
#
#
# RentalPlatform.results_dict()
# db = SQLiteDatabase(RentalPlatform.final_property_dict)
#
# # Get all ids and
# all_ids = list(db.get_all_property_ids())
# assert len(all_ids) == db.get_entry_count()
# total_entries = len(all_ids)
#
# report_results = {}
#
# for id in all_ids:
#     property = db.fetch_data_by_id(id)
#     report_results[id] = property

# Replace this dictionary with your actual data
data = {
    1: {
        'image': 'path_to_image1.jpg',
        'column1': 'value1',
        'column2': 'value2',
        'column3': 'value3',
        'url': 'https://example.com/page1',
    },
    2: {
        'image': 'path_to_image2.jpg',
        'column1': 'value4',
        'column2': 'value5',
        'column3': 'value6',
        'url': 'https://example.com/page2',
    },
    # Add more rows as needed
}

# Construct the HTML
html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" integrity="sha384-B4gt1jrGC7Jh4AgTPSdUtOBvfO8sh+Wy6pZlF/nlUuGRnLJb6IbbjJSy6P6kdS1" crossorigin="anonymous">
    <title>Report</title>
</head>
<body>

<div class="container">
    <table class="table table-bordered">
        <thead>
            <tr>
                <th>ID</th>
                <th>Image</th>
                <th>Column 1</th>
                <th>Column 2</th>
                <th>Column 3</th>
                <th>URL</th>
            </tr>
        </thead>
        <tbody>
'''

for id, row in data.items():
    html_content += f'''
            <tr>
                <td>{id}</td>
                <td><img src="{row['image']}" alt="Image"></td>
                <td>{row['column1']}</td>
                <td>{row['column2']}</td>
                <td>{row['column3']}</td>
                <td><a href="{row['url']}" target="_blank">{row['url']}</a></td>
            </tr>
'''

html_content += '<table class="table">'
html_content += '<thead><tr>'

html_content += '''
        </tbody>
    </table>
</div>

</body>
</html>
'''

html_content += '<tbody></table><script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/js/bootstrap.min.js"></script></body></html>'


# Save the HTML to a file
with open('report.html', 'w') as file:
    file.write(html_content)

print("HTML report has been generated and saved to 'report.html'.")


