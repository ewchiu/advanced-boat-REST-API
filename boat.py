from google.cloud import datastore
from flask import Blueprint, request, jsonify, Response, make_response
from json2html import *

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')

def unique_name(name):
    """
    valdiates boat name is unique across all boats
    """
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

    # name must be between 3 and 26 characters
    if length > 26 or length < 3:
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
    """
    validates required attributes are present in request body
    """
    return 'name' not in req or 'type' not in req or 'length' not in req


# get all/create boats
@bp.route('', methods=['POST', 'PUT', 'DELETE'])
def boats_post_get():

    # method to create a new boat
    if request.method == 'POST':
        content = request.get_json()

        if request.content_type != 'application/json':
            error = {"Error": "This MIME type is not supported by the endpoint"}
            return jsonify(error), 415

        # check if attributes are missing
        elif len(content) != 3 or not content['name'] or not content['type'] or not content['length'] or validate_req_attributes(content):  
            error = {"Error": "The request object is missing at least one of the required attributes"}
            return jsonify(error), 400

        # check attributes for validity
        elif not validate_name_type(content["name"]) or not validate_name_type(content["type"]) or not validate_length(content["length"]):
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

    elif request.method == 'PUT' or request.method == 'DELETE':
        error = {"Error": "Method not recognized"}
        return jsonify(error), 405

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

        # handlers for different kinds of MIME types
        if 'application/json' in request.accept_mimetypes:
            return jsonify(boat), 200
    
        elif 'text/html' in request.accept_mimetypes:
            res = make_response(json2html.convert(json = boat))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 200
            return res
        else:
            error = {"Error": "You specified an unsupported response MIME type"}
            return jsonify(error), 406

    # edit one or more attributes of boat
    elif request.method == 'PATCH':
        boat_key = client.key('boats', int(id))
        boat = client.get(key=boat_key)
        content = request.get_json()
        boat_attributes = ['name', 'type', 'length']

        # boat id was not found 
        if not boat:
            error = {"Error": "No boat with this boat_id exists"}
            return jsonify(error), 404

        elif request.content_type != 'application/json':
            error = {"Error": "This MIME type is not supported by the endpoint"}
            return jsonify(error), 415

        for key in content:

            # validate content 
            if key not in boat_attributes:
                error = {"Error": "You can only edit attributes name, type, and length"}
                return jsonify(error), 400

            elif key == 'name' or key == 'type':
                if not validate_name_type(content[key]):
                    error = {"Error": "Invalid attribute value"}
                    return jsonify(error), 400
                elif key == 'name':
                    if not unique_name(content[key]):
                        error = {"Error": "Boat name is not unique"}
                        return jsonify(error), 403
                
            elif key == 'length':
                if not validate_length(content[key]):
                    error = {"Error": "Invalid attribute value"}
                    return jsonify(error), 400

            else:
                error = {"Error": "Invalid attribute value"}
                return jsonify(error), 400

            boat[key] = content[key]
        
        client.put(boat)

        # format response object
        boat["id"] = id
        boat["self"] = str(request.url)
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
        elif len(content) != 3 or not content['name'] or not content['type'] or not content['length'] or validate_req_attributes(content):  
            error = {"Error": "The request object is missing at least one of the required attributes"}
            return jsonify(error), 400

        # check attributes for validity
        if not validate_name_type(content["name"]) or not validate_name_type(content["type"]) or not validate_length(content["length"]):
            error = {"Error": "Invalid attribute value"}
            return jsonify(error), 400

        elif not unique_name(content["name"]):
            error = {"Error": "Boat name is not unique"}
            return jsonify(error), 403

        # check that user isn't trying to update value of ID

        # format response object
        boat["id"] = id
        boat['name'] = content['name']
        boat['type'] = content['type']
        boat['length'] = content['length']
        boat["self"] = str(request.url)
        client.put(boat)

        response = make_response(jsonify(boat))
        response.headers.set("Location", f"{request.url}/{str(id)}")
        response.status_code = 303
        return response

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


