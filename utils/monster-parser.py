#!/usr/bin/env python

import xmltodict
from dicttoxml import dicttoxml
from pymongo import MongoClient


def postprocessor(path, key, value):
    try:
        return key, int(value)
    except (ValueError, TypeError):
        return key, value

source_file = 'data/Bestiary-Compendium.xml'

# Mongo Stuff
client = MongoClient()
db = client['dnd']
monsters_collection = db['monsters']

with open(source_file) as fd:
    # doc = xmltodict.parse(fd.read(), item_callback=postprocesser)
    my_xml = fd.read()

doc = xmltodict.parse(my_xml, postprocessor=postprocessor)


count = 0

for monster in doc['compendium']['monster']:
    xml = dicttoxml(monster, attr_type=False, root=False)
    # print(xml)
    monster['xml'] = "<monster>{}</monster>".format(xml)
    count += 1

print("Monster count: {}").format(count)

# result = monsters_collection.insert_many(doc['compendium']['monster'])
# print(result.inserted_ids)
