#! /usr/bin/env python

# script to compute the topological sort of the graph
import networkx as nx
import score
import sys
import json
import utilsPoirel as utils

#G = nx.DiGraph()

#edges = {
#     's': ['a', 'b'],
#     'a': ['c'], 
#     'b': ['d'],
#     'c': ['b', 't'], 
#     'd': ['a', 'c', 't']
#}

if len(sys.argv) < 2:
    print "Usage: pyton topo-sort.py <network.cyjs>"
    sys.exit()

# first file is the graph JSON file
# second file is the list of sources and targets
json_data = json.load(open(sys.argv[1]))
#lines = utils.readColumns(sys.argv[2],1,2)
#sources = set([acc for acc, node_type in lines if node_type.lower() in ['source', 'receptor']])
#targets = set([acc for acc, node_type in lines if node_type.lower() in ['target', 'tf']])

G = score.buildGraph(json_data)
print nx.info(G)
sources = [n for n in G.nodes() if int(G.node[n]['y']) == -300]
targets = [n for n in G.nodes() if int(G.node[n]['y']) == 1000]
# add the super-source to source and super-target to target edges
for s in sources:
    G.add_edge('s',s)
for t in targets:
    G.add_edge(t,'t')
G.node['s']['y'] = -50000
G.node['t']['y'] = 50000

#print "Adding edges to G: ", edges
num_paths_per_edge = {}
for u,v in G.edges():
    num_paths_per_edge[(u,v)] = 0 

print "Finding the simple cycles in G"
cycles = list(nx.simple_cycles(G))
#print "Cycles:"
#for cycle in cycles:
#print cycles
print "%d cycles in the graph" % (len(cycles))
print '\t' + '\n\t'.join([str(c) for c in cycles])

#print "Paths:"
all_simple_paths = nx.all_simple_paths(G, 's', 't')
#for path in all_simple_paths:
#    print path
# now weight the graph and figure out which edges to remove to fix the cycles
for path in all_simple_paths:
    for i in range(0,len(path)-1):
        e = (path[i], path[i+1])
        num_paths_per_edge[e] += 1
#print num_paths_per_edge

#acyclicG = nx.copy(G)

# now approximate the minimum feedback arc set using the algorithm from this paper:
# http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.1.9435&rep=rep1&type=pdf
# first 
all_edges_removed = set()
while len(cycles) > 0:
    # at least one cycle will be removed every iteration. There could be more
    cycle = cycles[0]
    #print "starting cycle:", cycle
    # find the minimum cost edge in this cycle
    min_cost = float('inf')
    min_edge = ''
    for i in range(0,len(cycle)):
        edge = (cycle[i], cycle[(i+1)%len(cycle)])
        if num_paths_per_edge[edge] < min_cost:
            min_cost = num_paths_per_edge[edge]
            min_edge = edge
    #print "min:", min_cost, min_edge
    # lower all of the weights by the minimum, and then remove the edges that have a weight of 0
    edges_removed = set()
    for i in range(0,len(cycle)):
        edge = (cycle[i], cycle[(i+1)%len(cycle)])
        num_paths_per_edge[edge] = num_paths_per_edge[edge] - min_cost
        if num_paths_per_edge[edge] == 0:
            del num_paths_per_edge[edge]
            edges_removed.add(edge)

    #print "edges removed:", edges_removed
    all_edges_removed.update(edges_removed)
    # now remove all of the cycles that have at least one edge removed
    # loop through backwards so we can remove as we iterate through
    for j in reversed(xrange(len(cycles))):
        cycle = cycles[j]
        #print "checking cycle:", cycle
        broken = False
        for i in range(0,len(cycle)):
            edge = (cycle[i], cycle[(i+1)%len(cycle)])
            if edge in edges_removed:
                broken = True
                break
        # this cycle has been broken. Remove it from the list of cycles
        if broken is True:
            #print "removing cycle ", j, cycles[j]
            del cycles[j]

print "removing edges:\n\t" + '\n\t'.join([str(s) for s in all_edges_removed])
G.remove_edges_from(all_edges_removed)
# now see if you can add any edges back without creating a cycle
print "adding edges back:"
for u,v in all_edges_removed:
    # if v is reachable from u, then adding this edge would create a cycle
    if not nx.has_path(G,v,u):
        # add the edge u,v back to G
        print "\t" + str((u,v))
        G.add_edge(u,v)

# now perform the topological sort on the acyclicG
topo_sort = nx.topological_sort(G)
print "Topological sort of the graph:\n\t" + '\n\t'.join(topo_sort)

print "P98077,Q6S5L8,Q92529,P29353 incoming:", G.predecessors("P98077,Q6S5L8,Q92529,P29353")

# now set the y positions
curr_y = 1
for n in topo_sort:
    G.node[n]['y'] = curr_y
    curr_y += 1

count = 0
for source in sources:
    count += score.countDownwardPointingPaths(G, source, targets)
print "score:", count
