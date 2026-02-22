from unittest import result
from . import app
import os
import json
import pymongo
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from pymongo import MongoClient
from bson import json_util
from pymongo.errors import OperationFailure
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
import sys

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

# client = MongoClient(f"mongodb://{app.config['MONGO_USERNAME']}:{app.config['MONGO_PASSWORD']}@localhost")
mongodb_service = os.environ.get('MONGODB_SERVICE')
mongodb_username = os.environ.get('MONGODB_USERNAME')
mongodb_password = os.environ.get('MONGODB_PASSWORD')
# mongodb_port = os.environ.get('MONGODB_PORT')

print(f'The value of MONGODB_SERVICE is: {mongodb_service}')

if mongodb_service == None:
    app.logger.error('Missing MongoDB server in the MONGODB_SERVICE variable')
    abort(500, 'Missing MongoDB server in the MONGODB_SERVICE variable')
    sys.exit(1)

if mongodb_username and mongodb_password:
    url = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_service}"
else:
    url = f"mongodb://{mongodb_service}"


print(f"connecting to url: {url}")

try:
    client = MongoClient(url)
except OperationFailure as e:
    app.logger.error(f"Authentication error: {str(e)}")

db = client.songs
db.songs.drop()
db.songs.insert_many(songs_list)

def parse_json(data):
    return json.loads(json_util.dumps(data))

######################################################################
# INSERT CODE HERE
######################################################################

# #RETURN HEALTH OF THE APP
@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

@app.route("/count")
def count():
    """return length of data"""
    count = db.songs.count_documents({})
    return {"count": count }, 200

#GET ALL SONGS
@app.route("/songs", methods=["GET"])
def get_songs():
    results = list(db.songs.find({}))
    print(results[0])
    return {"results": parse_json(results)}, 200

#GET A SONG
@app.route("/songs/<int:id>", methods=["GET"])
def get_song_by_id(id):
    song = db.songs.find_one({"id":id})
    if not song:
        return {"message": f"song with {id} not found"}, 404
    return {"results": parse_json(song)}, 200

#CREATE A SONG
@app.route("/songs", methods=["POST"])
def create_song():
    # get data from the json body
    song_in = request.get_json()
    print(song_in['id'])
    song = db.songs.find_one({"id": song_in["id"]})
    if song:
        return {"message": f"song with id {song_in['id']} already present"}, 409
    result = db.songs.insert_one(song_in)
    return {"message": parse_json(result.inserted_id)}, 201
    

#UPDATE A SONG
@app.route("/songs/<int:id>",methods=["PUT"])
def update_song(id):
    song_in = request.get_json()
    song = db.songs.find_one({"id": id})
    if song == None:
        return {"message": f"song with id {id} not found"}, 404
    if not song_in:
        return {"message": "Invalid input parameter"}, 400
    result = db.songs.update_one(
        {"id":id}, 
        {"$set": song_in}
        )
    if result.modified_count == 0:
        return {"message": "song found, but no changes made"}, 200
    return parse_json(db.songs.find_one({"id": id})), 201
    

#DELETE A SONG
@app.route("/songs/<int:id>", methods = ["DELETE"])
def delete_song(id):
    result = db.songs.delete_one({"id": id})
    if result.deleted_count == 0:
        return {"message": "song not found"}, 404
    else:
        return "", 204
