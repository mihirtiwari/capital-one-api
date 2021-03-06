from flask import Flask, jsonify, request
import requests, json
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['ACCESS_TOKEN'] = os.environ['TOKEN']

access_token = os.environ['TOKEN']

BASE_URL = 'https://api.yelp.com/v3/'
DAYS_OF_THE_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def parse_address(address):
    a = ""
    for x in range(0,len(address)):
        if x is not len(address) - 1:
            a += address[x] + ', '
        else:
            a += address[x]

    return a

def parse_business_info(businesses):
    info = []
    id = ''
    for x in range(0, len(businesses)):
        phone = businesses[x]['display_phone']
        if len(phone) is 0:
            phone = 'None'
        id = businesses[x]['id']
        address = parse_address(businesses[x]['location']['display_address'])
        name = businesses[x]['name']
        rating = businesses[x]['rating']
        image = businesses[x]['image_url'];
        url = businesses[x]['url'],
        closed = businesses[x]['is_closed'],
        num_reviews = businesses[x]['review_count']

        bus = {
            'name': name,
            'phone': phone,
            'id': id,
            'address': address,
            'rating': rating,
            'image': image,
            'url': url,
            'closed': closed,
            'num_reviews': num_reviews,
        }

        info.append(bus)

    return info

@app.route('/')
def index():
    return "Hello World!"

#all businesses in area based on town location
@app.route('/businesses/location=<location>', methods=['GET'])
def businesses_location(location):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    req = requests.get(BASE_URL + 'businesses/search?location=' + location + '&sort_by=rating&limit=20&categories ="food, All"', headers=headers)
    r = json.loads(req.text)

    try:
        r = parse_business_info(r['businesses'])
        return jsonify(r)
    except:
        r = {
              'name': 'Error! Please try again! ',
              'phone': 'Error! Please try again!',
              'address': 'Error! Please try again!',
              'rating': 'Error! Please try again!'
        }
        return jsonify(r);

@app.route('/filters', methods=['GET'])
def filter():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    full_url = 'businesses/search?location=' + request.values.get('location') + '&sort_by=rating&limit=20&categories ="food, All"'
    price = int(request.values.get('price'))
    radius = int(request.values.get('radius'))

    if price is not 0 and request.values.get('price') is not None:
        full_url += '&price=' + request.values.get('price')

    if request.values.get('open') is not 'false' and request.values.get('open') is not None:
        full_url += '&open_now=true'

    if request.values.get('filters') is not '' and request.values.get('filters') is not None:
        full_url += '&attributes=' + request.values.get('filters')

    if radius is not 0 and request.values.get('radius') is not None:
        full_url += '&radius=' + request.values.get('radius')

    req = requests.get(BASE_URL + full_url, headers=headers)
    r = json.loads(req.text)

    try:
        r = parse_business_info(r['businesses'])
        return jsonify(r);
    except:
        r = {
              'name': 'Error! Please try again! ',
              'phone': 'Error! Please try again!',
              'address': 'Error! Please try again!',
              'rating': 'Error! Please try again!'
        }
        return jsonify(r);


#all businesses in area based on latitude and longitude
@app.route('/businesses/longitude=<longitude>&latitude=<latitude>', methods=['GET'])
def businesses_lat_long(latitude, longitude):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    req = requests.get(BASE_URL + 'businesses/search?longitude=' + longitude + '&latitude=' + latitude + '&sort_by=rating&limit=20&categories ="food, All"', headers=headers)
    r = json.loads(req.text)

    try:
        r = parse_business_info(r['businesses'])
        return jsonify(r)
    except:
        r = {
              'name': 'Error! Please try again! ',
              'phone': 'Error! Please try again!',
              'address': 'Error! Please try again!',
              'rating': 'Error! Please try again!'
        }

        return jsonify(r);

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
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
