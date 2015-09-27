#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
"""
docstring
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


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
        print node
        return node
    else:
        return None

def process_child_attrib(d, node):
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


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset,
    # call the process_map procedure with pretty=False. The pretty=True option adds
    # additional spaces to the output, making it significantly larger.
    data = process_map('osm_data/perth.osm', True)
    pprint.pprint(data)

    correct_first_elem = {
        "id": "261114295",
        "visible": "true",
        "type": "node",
        "pos": [41.9730791, -87.6866303],
        "created": {
            "changeset": "11129782",
            "user": "bbmiller",
            "version": "7",
            "uid": "451048",
            "timestamp": "2012-03-28T18:31:23Z"
        }
    }

if __name__ == "__main__":
    test()