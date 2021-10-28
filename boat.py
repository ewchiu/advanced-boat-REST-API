from google.cloud import datastore
from flask import Blueprint, request, jsonify, Response

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')

# get all/create boats
@bp.route('', methods=['POST', 'GET'])
def boats_post_get():

    # method to create a new boat
    if request.method == 'POST':
        content = request.get_json()

        # check if attributes are missing
        if len(content) != 3:  
            error = {"Error": "The request object is missing at least one of the required attributes"}
            return jsonify(error), 400

        # create new boat in Datastore
        new_boat = datastore.entity.Entity(key=client.key("boats"))
        new_boat.update({"name": content["name"], "type": content["type"],
          "length": content["length"], "loads": []})
        client.put(new_boat)

        # formats response object
        new_boat["id"] = new_boat.key.id
        new_boat["self"] = f"{request.url}/{str(new_boat.key.id)}"

        return jsonify(new_boat), 201

    # method to get all boats
    elif request.method == 'GET':
        query = client.query(kind="boats")
        limit = int(request.args.get('limit', '3'))
        offset = int(request.args.get('offset', '0'))
        iterator = query.fetch(limit=limit, offset=offset)
        pages = iterator.pages
        results = list(next(pages))

        if iterator.next_page_token:
            next_offset = limit + offset
            next_url = f"{request.base_url}?limit={limit}&offset={next_offset}"
        else:
            next_url = None

        for boat in results:
            boat['id'] = boat.key.id
        
        output = {"boats": results}

        if next_url:
            output['next'] = next_url

        return jsonify(output), 200

    else:
        return 'Method not recognized'