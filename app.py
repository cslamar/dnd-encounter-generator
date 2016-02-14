from flask import Flask, jsonify, render_template, make_response, request
from pymongo import MongoClient
import json
import redis
from bson.objectid import ObjectId

# MongoDB Stuff
client = MongoClient()
db = client['dnd']
monsters_collection = db['monsters']

app = Flask(__name__)


@app.route('/')
def hello_world():
    results = monsters_collection.find_one({"name": "Kobold"})
    results["id"] = str(results["_id"])
    results.pop("_id", None)
    return jsonify(results)


@app.route('/api/v1/monsters/<monster_id>/')
def get_monster(monster_id):
    results = monsters_collection.find_one({"_id": ObjectId(monster_id)})
    results["id"] = str(results["_id"])
    results.pop("_id", None)
    results.pop("xml", None)
    return jsonify(results)


@app.route('/api/v1/monsters/<monster_id>/<return_format>/')
def get_monster_xml(monster_id, return_format):
    results = monsters_collection.find_one({"_id": ObjectId(monster_id)})
    if return_format == 'json':
        results["id"] = str(results["_id"])
        results.pop("_id", None)
        results.pop("xml", None)
        return jsonify(results)
    if return_format == 'xml':
        return app.response_class(results['xml'], mimetype='application/xml')
    else:
        return 'No Monster found.  Something went wrong...'


@app.route('/api/v1/monsters/')
def get_monster_names():
    monster_list = []
    for monster in monsters_collection.find():
        monster_list.append(
            {
                "name": monster['name'],
                "id": str(monster['_id'])
            }
        )
    return jsonify({"monsters": monster_list})


@app.route('/api/v1/encounter/<name>.xml')
def get_encounter(name):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    print(name)
    template = r.get(name)
    print(template)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response


@app.route('/api/v1/generate-encounter/<name>', methods=['POST', 'PUT'])
def generate_encounter(name):

    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    bad_guys = request.get_json()
    print(bad_guys['monsters'])
    template = render_template('encounter.xml', battle_name=name, bad_guys=bad_guys['monsters'])
    # print(template)
    r.set(name, template)

    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'
    # response.mimetype = 'application/xml'
    return 'hi there'


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
