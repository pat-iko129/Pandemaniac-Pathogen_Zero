import networkx as nx
import heapq

def closeness(G, n):
    closeness = nx.closeness_centrality(G)
    nlargest_close = heapq.nlargest(n, closeness, key=closeness.get)
    return nlargest_close

def degree(graph, n):
    degree = nx.degree_centrality(graph)
    nlargest_degree = heapq.nlargest(n, degree, key=degree.get)
    return nlargest_degree

def betweenness(graph, n):
    betweenness = nx.betweenness_centrality(graph)
    nlargest_between = heapq.nlargest(n, betweenness, key=betweenness.get)
    return nlargest_between