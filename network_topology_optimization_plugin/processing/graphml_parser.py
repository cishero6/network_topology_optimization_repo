import xml.etree.ElementTree as ET

class GraphEdge:
    def __init__(self, source, target, value):
        self.source = source
        self.target = target
        self.value = value


def parse_graphml(path):
    ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}
    tree = ET.parse(path)
    root = tree.getroot()
    keys = {k.get('id'): k.get('attr.name') for k in root.findall('g:key', ns)}
    edges = []
    for e in root.findall('.//g:edge', ns):
        src = e.get('source')
        tgt = e.get('target')
        val = None
        for d in e.findall('g:data', ns):
            if keys.get(d.get('key')) == 'value':
                val = float(d.text)
        edges.append(GraphEdge(src, tgt, val))
    return edges