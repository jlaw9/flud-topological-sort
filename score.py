#! /usr/bin/env python

import networkx as nx
import json
import sys
#import utilsPoirel as utils


sources = []
targets = []


def main():
    global sources, targets

    print "parsing json file from %s using the sources and targets from %s" % (sys.argv[1], sys.argv[2])
    # first load the cyjs file
    json_data = json.load(open(sys.argv[1]))
    # next load the file containing the source and target nodes
    lines = readColumns(sys.argv[2],1,2)
    sources = set([acc for acc, node_type in lines if node_type.lower() in ['source', 'receptor']])
    targets = set([acc for acc, node_type in lines if node_type.lower() in ['target', 'tf']])

    # build it into a networkx graph object
    G = buildGraph(json_data)
    print nx.info(G)

    # add the super-source to source and super-target to target edges
    for s in sources:
        G.add_edge('s',s)
    for t in targets:
        G.add_edge(t,'t')
    G.node['s']['y'] = -5000
    G.node['t']['y'] = 5000

    # now count the number of paths pointing downward from the sources "triangles"
    count = 0
    for source in sources:
        count += countDownwardPointingPaths(G, source, targets)

    print "%d paths point downward" % (count)


# TODO
#def getSourcesTargets(style_json, cytoscape=False):


def buildGraph(json_data, cytoscape=False):
    G = nx.DiGraph()
    for node in json_data['elements']['nodes']:
        node_name = str(node['data']['name'])
        G.add_node(node_name)

        # store the x,y coordinates
        x,y = node['position']['x'], node['position']['y']
        G.node[node_name]['x'] = x
        G.node[node_name]['y'] = y

    # now add the edges
    if cytoscape is True:
        for edge in json_data['elements']['edges']:
            u, v = edge['data']['name'].split(' () ')
            G.add_edge(str(u), str(v))
    else:
        for edge in json_data['elements']['edges']:
            u = edge['data']['source']
            v = edge['data']['target']
            G.add_edge(str(u), str(v))
            if edge['data']['is_directed'] is False:
                G.add_edge(str(v), str(u))

    return G


# y1 is the source y, y2 is the target y
def isCorrectAngle(y1, y2):

    # the y axis is at the top
    y_angle = y1 - y2

    if y_angle < 0:
        return True
    else:
        return False


# returns count of completed directed paths
# (i.e., paths that go from the current node to the bottom)
def countDownwardPointingPaths(G, node, targets):
    if node in targets:
        # we are at the bottom
        return 1

    # now get the neighbors
    neighbors = G.neighbors(node)
    count = 0

    for neighbor in neighbors:
        if isCorrectAngle(G.node[node]['y'], G.node[neighbor]['y']):
            count += countDownwardPointingPaths(G, neighbor, targets)

    return count


def readColumns(f, *cols):
    '''
    Read multiple columns and return the items from those columns
    in each line as a tuple.

    foo.txt:
        a b c
        d e f
        g h i

    Calling "readColumns('foo.txt', 1, 3)" will return:
        [(a, c), (d, f), (g, i)]

    '''
    if len(cols)==0:
        return []
    rows = []
    for line in open(f, 'r').readlines():
        if line=='':
            continue
        if line[0]=='#':
            continue
        items = line.rstrip().split('\t')
        if len(items)<max(cols):
            continue
        rows.append(tuple([items[c-1] for c in cols]))
    return rows


if __name__ == "__main__":
    main()
