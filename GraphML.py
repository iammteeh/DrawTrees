import xml.etree.ElementTree as ET
import networkx as nx

class GraphML:
    _path = ""
    _gml = ""
    _keys = []
    _graphs = {}

    def __init__(self, path):
        self._gml = ET.parse(path)
        self._path = path

    def keys(self):
        if not self._keys:
            for key in self._gml.iter('{http://graphml.graphdrawing.org/xmlns}key'):
                self._keys.append(key.attrib['id'])

        return self._keys

    def to_graph(self, key):
        G = nx.DiGraph()

        if key not in self.keys():
            raise LookupError('Key ist nicht in der .graphml Datei enthalten')

        graph = self._gml.getroot().find('{http://graphml.graphdrawing.org/xmlns}graph')

        # Load edges, which have the current key. Skip existing edges
        for edge in graph.iter('{http://graphml.graphdrawing.org/xmlns}edge'):
            data = edge.find('{http://graphml.graphdrawing.org/xmlns}data')
            if data.attrib['key'] != key:
                continue
            if not G.has_edge(edge.attrib['source'], edge.attrib['target']):
                G.add_edge(edge.attrib['source'], edge.attrib['target'], color='b')

        return G