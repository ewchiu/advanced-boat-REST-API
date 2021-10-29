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

        if request.content_type != 'application/json':
            error = {"Error": "This MIME type is not supported by the endpoint"}
            return jsonify(error), 415

        # check if attributes are missing
        if len(content) != 3 or not content['name'] or not content['type'] or not content['length']:  
            error = {"Error": "The request object is missing at least one of the required attributes"}
            return jsonify(error), 400

        # check attributes for validity
        if not validate_name_type(content["name"]) or not validate_name_type(content["type"]) or not validate_length(content["length"]):
            error = {"Error": "Invalid attribute value"}
            return jsonify(error), 400
        elif not unique_name(content["name"]):
            error = {"Error": "Boat name is not unique"}
            return jsonify(error), 403

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

    # edit all attributes of a boat
    elif request.method == 'PUT':
        boat_key = client.key('boats', int(id))
        boat = client.get(key=boat_key)
        content = request.get_json()

        # boat id was not found 
        if not boat:
            error = {"Error": "No boat with this boat_id exists"}
            return jsonify(error), 404
        elif request.content_type != 'application/json':
            error = {"Error": "This MIME type is not supported by the endpoint"}
            return jsonify(error), 415
        # check if attributes are missing
        elif len(content) != 3 or 'name' not in content or 'type' not in content or 'length' not in content:  
            error = {"Error": "The request object is missing at least one of the required attributes"}
            return jsonify(error), 400
        # check attributes for validity
        elif not validate_name_type(content["name"]) or not validate_name_type(content["type"]) or not validate_length(content["length"]):
            error = {"Error": "Missing or invalid attribute(s)"}
            return jsonify(error), 400
        elif not unique_name(content["name"]):
            error = {"Error": "Boat name is not unique"}
            return jsonify(error), 403

        # update attributes
        boat['name'] = content['name']
        boat['type'] = content['type']
        boat['length'] = content['length']
        client.put(boat)

        return Response(status=303, location=f'{request.base_url}boats/{id}')

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


def unique_name(name):
# valdiates boat name is unique across all boats

    query = client.query(kind="boats")
    boats = list(query.fetch())

    for boat in boats:

        if name == boat['name']:
            return False

    return True

def validate_name_type(input):
    """
    Validates boat name or type input
    """
    length = len(input)

    # name must be between 3 and 20 characters
    if length > 20 or length < 3:
        return False
    # check name does not contain any chars besides letters or spaces
    elif not all(chr.isalpha() or chr.isspace() for chr in input):
        return False
    # check that first and last chars in name are not space
    elif input[0] == ' ' or input[length - 1] == ' ':
        return False
    else:
        return True

def validate_length(input):
    """
    Validates boat length input
    """
    return type(input) is int and input > 0 and input < 999999

def validate_req_attributes(req):
# validates the attributes of the request body

    pass
