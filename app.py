from flask import Flask, jsonify, render_template, make_response
from pymongo import MongoClient
import json
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


@app.route('/monsters/<monster_id>/')
def get_monster(monster_id):
    results = monsters_collection.find_one({"_id": ObjectId(monster_id)})
    results["id"] = str(results["_id"])
    results.pop("_id", None)
    results.pop("xml", None)
    return jsonify(results)


@app.route('/monsters/<monster_id>/<return_format>/')
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


@app.route('/monsters/')
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


@app.route('/encounter/')
def generate_encounter():
    name = "Random Encounter 1"
    template = render_template('encounter.xml', battle_name=name)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
