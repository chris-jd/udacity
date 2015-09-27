#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from pymongo import MongoClient
"""
docstring
"""

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
# Regex to find incompatible names
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
client = MongoClient()
db = client['udacity']


def shape_element(element):

    node = {}
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        node['type'] = element.tag
        node = process_node_attrib(element.attrib, node)
        for child in element:
            if child.tag == 'tag':
                node = process_child_attrib(child.attrib, node)
            elif child.tag == 'nd':
                if 'node_refs' not in node.keys():
                    node['node_refs'] = [child.attrib['ref']]
                else:
                    node['node_refs'].append(child.attrib['ref'])
        # print node
        return node
    else:
        return None

def process_child_attrib(d, node):
    """
    Processes the attributes dictionary of a 'node' or 'way' tag.

    Will split address items into an 'address' sub-dictionary
    Remaining items will keep their key, value pair

    :param d: Input dictionary of form {'k': key, 'v': value}
    :param node: The output dictionary for the node.
    :return: node dictionary with item added appropriately.
    """
    try:
        k, v = d['k'], d['v']
    except KeyError:
        return node
    if k[:5] == 'addr:':
        ks = k.split(':')
        if len(ks) > 2:
            return node
        if 'address' not in node.keys():
            node['address'] = {}
        node['address'][ks[-1]] = v
    else:
        node[k] = v
    return node

def process_node_attrib(d, node):
    """
    Processes all the attributes in a 'node' or 'way' tag.

    :param d: Dictionary with all the attributes
    :param node: The output dictionary for the node.
    :return: Node output dictionary for the node.
    """
    if ('lat' in d.keys()) and ('lon' in d.keys()):
        node['pos'] = [float(d['lat']), float(d['lon'])]
    for k,v in d.iteritems():
        if k in CREATED:
            if 'created' not in node.keys():
                node['created'] = {}
            node['created'][k] = v
        elif k in ['lat', 'lon']:
            pass #Handling these seperately
        else:
            node[k] = v
    return node


def process_map(file_in, write_collection):
    # You do not need to change this file
    for _, element in ET.iterparse(file_in):
        el = shape_element(element)
        if el:
            write_collection.insert_one(el)

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset,
    # call the process_map procedure with pretty=False. The pretty=True option adds
    # additional spaces to the output, making it significantly larger.
    data = process_map('osm_data/perth.osm', True)

if __name__ == "__main__":
    test()