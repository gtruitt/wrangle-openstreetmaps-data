#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json


OSMFILE = 'data/hampton-roads_virginia_mapzen_2015-09-26.osm'

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ 'version', 'changeset', 'timestamp', 'user', 'uid']


def shape_element(element):
    node = None
    if element.tag == 'node' or element.tag == 'way':
        node = {'created': {}, 'type': element.tag}
        pos = {}
        address = {}
        node_refs = []

        for key in element.attrib.keys():
            if key in CREATED:
                node['created'][key] = element.attrib[key]
            elif key in ('lat', 'lon'):
                pos[key] = element.attrib[key]
            else:
                node[key] = element.attrib[key]

        if len(pos) == 2:
            node['pos'] = [float(pos['lat']), float(pos['lon'])]

        for tag in element.iter('tag'):
            if problemchars.search(tag.attrib['k']) or tag.attrib['k'].startswith('addr:street:'):
                continue
            if tag.attrib['k'].startswith('addr:'):
                k = tag.attrib['k'][5:]
                address[k] = tag.attrib['v']
            else:
                node[tag.attrib['k']] = tag.attrib['v']

        if len(address) > 0:
            node['address'] = address

        for nd in element.iter('nd'):
            node_refs.append(nd.attrib['ref'])

        if len(node_refs) > 0:
            node['node_refs'] = node_refs

    return node


def process_map(file_in):
    file_out = '{0}.json'.format(file_in)

    with codecs.open(file_out, 'w') as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)

            if el:
                fo.write(json.dumps(el) + '\n')

            if element.tag == 'node' or element.tag == 'way':
                element.clear()

if __name__ == '__main__':
    process_map(OSMFILE)
