from google.cloud import datastore
from flask import Blueprint, request, jsonify, Response

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')

# get all/create boats
@bp.route('', methods=['POST'])
def boats_post_get():

    # method to create a new boat
    if request.method == 'POST':
        content = request.get_json()

        # check if attributes are missing
        if len(content) != 3:  
            error = {"Error": "The request object is missing at least one of the required attributes"}
            return jsonify(error), 400

        # validate name (maybe create a global method for this)

        # create new boat in Datastore
        new_boat = datastore.entity.Entity(key=client.key("boats"))
        new_boat.update({"name": content["name"], "type": content["type"],
          "length": content["length"]})
        client.put(new_boat)

        # formats response object
        new_boat["id"] = new_boat.key.id
        new_boat["self"] = f"{request.url}/{str(new_boat.key.id)}"

        return jsonify(new_boat), 201

    else:
        return 'Method not recognized'

@bp.route('/<id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def boat_id_get_delete(id):

    # get a boat by ID
    if request.method == 'GET':
        boat_key = client.key('boats', int(id))
        boat = client.get(key=boat_key)

        # boat id was not found 
        if not boat:
            error = {"Error": "No boat with this boat_id exists"}
            return jsonify(error), 404

        boat['id'] = id
        boat['self'] = request.url
        return jsonify(boat), 200

    # delete a boat
    elif request.method == 'DELETE':
        boat_key = client.key('boats', int(id))
        boat = client.get(key=boat_key)

        # boat id was not found 
        if not boat:
            error = {"Error": "No boat with this boat_id exists"}
            return jsonify(error), 404

        client.delete(boat_key)
        return Response(status=204)

    else:
        return 'Method not recognized'