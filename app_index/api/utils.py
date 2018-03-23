def getGeocodeLocation(input_string):
    google_api_key = json.loads(open('./credentials.json').read())['Google'
    ' Maps API']['API Key']
    location_string = url_parse.quote(input_string)

    params = dict(
        address=location_string,
        key=google_api_key
    )
    url = ('https://maps.googleapis.com/maps/api/geocode/json')

    response = requests.get(url=url, params=params)
    data = json.loads(response.text)
    location = data['results'][0]['geometry']['location']
    longitude = location['lng']
    latitude = location['lat']

    ll = dict(
        longitude=longitude,
        latitude=latitude
    )

    return jsonify(ll)


def findRestaurant(address="Osaka", query="ramen", limit=1):
    """
    Returns JSON response consisting of restaurant rating, name,
    address, picture, and url.
    """
    if 'address' in request.args:
        address = request.args.get('address')
    if 'query' in request.args:
        query = request.args.get('query')
    if 'limit' in request.args:
        limit = request.args.get('limit')

    limit = int(limit)
    try:
        ll_data = json.loads(getGeocodeLocation(address).data.decode())
        ll = '%s, %s' % (ll_data['latitude'], ll_data['longitude'])
        response = json.loads(getFourSquare(query, ll,
            limit).data.decode().encode('utf-8'))
        print(response)
    except:
        raise
    results = {}
    base = response['response']['groups'][0]['items']
    for i in range(limit):
        nbase = base[i]['venue']
        results[nbase['name']] = dict(
            address = nbase['location']['address'],
            picture = 'none' if nbase['photos']['count'] == 0 else
                nbase['photos']['groups'][0],
            url = 'none' if not 'url' in nbase.keys() else nbase['url'],
            rating = 'none' if not 'rating' in nbase.keys() else
            nbase['rating']
        )

    return json.dumps(results, ensure_ascii=False, indent=4, sort_keys=True)


def getFourSquare(query='pizza', ll='Osaka', limit=1):
    url = 'https://api.foursquare.com/v2/venues/explore'

    if 'query' in request.args:
        query = request.args.get('query')
    if 'll' in request.args:
        ll = request.args.get('ll')
    if 'limit' in request.args:
        limit = request.args.get('limit')

    credentials = json.loads(open('./credentials.json', 'r').read())['Four Square API']
    client_ID = credentials['Client ID']
    client_secret = credentials['Client Secret']

    params = dict(
        client_id=client_ID,
        client_secret=client_secret,
        v='20170801',
        ll=ll,
        query=query,
        limit=limit
    )

    resp = requests.get(url=url, params=params)
    data = json.loads(resp.text)
    return jsonify(data)
