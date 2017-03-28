from flask import Flask, jsonify, request
import requests, json
import os
from datetime import datetime

app = Flask(__name__)
app.config['ACCESS_TOKEN'] = os.environ['TOKEN']

access_token = os.environ['TOKEN']

BASE_URL = 'https://api.yelp.com/v3/'
DAYS_OF_THE_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

@app.route('/')
def index():
    return "Hello World!"

#all businesses in area based on town location
#TODO: Parse business info properly
@app.route('/businesses/location=<location>', methods=['GET'])
def businesses_location(location):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    req = requests.get(BASE_URL + 'businesses/search?location=' + location + '&limit=30', headers=headers)

    return jsonify(req.text)

#all businesses in area based on latitude and longitude
#TODO: Parse business info properly
@app.route('/businesses/longitude=<longitude>&latitude=<latitude>', methods=['GET'])
def businesses_lat_long(latitude, longitude):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    req = requests.get(BASE_URL + 'businesses/search?longitude=' + longitude + '&latitude=' + latitude + '&limit=30', headers=headers)

    return jsonify(req.text)

#gives specific review with 3 users
@app.route('/reviews/id=<id>', methods=['GET'])
def get_reviews(id):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    req = requests.get(BASE_URL + 'businesses/' + id + '/reviews', headers=headers)
    r = json.loads(req.text)

    reviews = r['reviews']
    review = {
        'review': [

        ]
    }
    user = {}
    for x in range(0, len(reviews)):
        user_rating = reviews[x]['rating']
        name = reviews[x]['user']['name']

        user = {
            'name': name,
            'user_rating': user_rating
        }

        review['review'].append(user);

    return jsonify(review)

#gives all info about business
@app.route('/business/id=<id>', methods=['GET'])
def business_details(id):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    req = requests.get(BASE_URL + 'businesses/' + id, headers=headers)
    r = json.loads(req.text)

    rating = {
        'name': r['name'],
        'phone': r['display_phone'],
        'price': r['price'],
        'rating': r['rating'],
        'review_count': r['review_count'],
        'address': r['location']['display_address'][0] + ', ' + r['location']['display_address'][1],
        'image': r['image_url'],
        'open': r['hours'][0]['is_open_now'],
    }

    open_times = r['hours'][0]['open']
    open = {}

    for x in range(0, len(open_times)):
        day = DAYS_OF_THE_WEEK[open_times[x]['day']]
        start = open_times[x]['start'][0:2] + ':' + open_times[x]['start'][2:]
        end = open_times[x]['end'][0:2] + ':' + open_times[x]['end'][2:]
        start = datetime.strptime(start, '%H:%M').strftime("%I:%M %p")
        end = datetime.strptime(end, '%H:%M').strftime("%I:%M %p")

        if not open_times[x]['is_overnight']:
            open[day] = {
                'time': start + '-' + end
            }
        else:
            open[day] = {
                'time': end + '-' + start
            }

    rating['times'] = open

    return jsonify(rating)

if __name__ == "__main__":
    app.run(debug=True);
