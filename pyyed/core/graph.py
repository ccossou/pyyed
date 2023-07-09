import logging
import sys

import xml.etree.ElementTree as ET
from xml.dom import minidom

from . import constants
from .node import Node
from .edge import Edge
from .group import Group
from .property import CustomPropertyDefinition

LOG = logging.getLogger(__name__)


class Graph:
    def __init__(self, directed="directed", graph_id="G", allow_duplicates=True):
        """

        :param directed:
        :param graph_id:
        :param allow_duplicates: True by default to keep compatibility with past behavior. If True, text in node
        will be different than label to ensure we can add multiple nodes with the same name.
        """

        self.nodes = {}
        self.edges = {}
        self.num_edges = 0
        self.duplicates = allow_duplicates

        # Only used if duplicates = True
        self.num_nodes = 0

        self.directed = directed
        self.graph_id = graph_id
        self.existing_entities = {self.graph_id: self}

        self.groups = {}

        self.custom_properties = []

        self.graphml = ""

    def construct_graphml(self):
        # xml = ET.Element("?xml", version="1.0", encoding="UTF-8", standalone="no")

        graphml = ET.Element("graphml", xmlns="http://graphml.graphdrawing.org/xmlns")
        graphml.set("xmlns:java", "http://www.yworks.com/xml/yfiles-common/1.0/java")
        graphml.set("xmlns:sys",
                    "http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0")
        graphml.set("xmlns:x", "http://www.yworks.com/xml/yfiles-common/markup/2.0")
        graphml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        graphml.set("xmlns:y", "http://www.yworks.com/xml/graphml")
        graphml.set("xmlns:yed", "http://www.yworks.com/xml/yed/3")
        graphml.set("xsi:schemaLocation",
                    "http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd")

        node_key = ET.SubElement(graphml, "key", id="data_node")
        node_key.set("for", "node")
        node_key.set("yfiles.type", "nodegraphics")

        # Definition: url for Node
        node_key = ET.SubElement(graphml, "key", id="url_node")
        node_key.set("for", "node")
        node_key.set("attr.name", "url")
        node_key.set("attr.type", "string")

        # Definition: description for Node
        node_key = ET.SubElement(graphml, "key", id="description_node")
        node_key.set("for", "node")
        node_key.set("attr.name", "description")
        node_key.set("attr.type", "string")

        # Definition: url for Edge
        node_key = ET.SubElement(graphml, "key", id="url_edge")
        node_key.set("for", "edge")
        node_key.set("attr.name", "url")
        node_key.set("attr.type", "string")

        # Definition: description for Edge
        node_key = ET.SubElement(graphml, "key", id="description_edge")
        node_key.set("for", "edge")
        node_key.set("attr.name", "description")
        node_key.set("attr.type", "string")

        # Definition: Custom Properties for Nodes and Edges
        for prop in self.custom_properties:
            graphml.append(prop.to_xml())

        edge_key = ET.SubElement(graphml, "key", id="data_edge")
        edge_key.set("for", "edge")
        edge_key.set("yfiles.type", "edgegraphics")

        graph = ET.SubElement(graphml, "graph", edgedefault=self.directed,
                              id=self.graph_id)

        for node in self.nodes.values():
            graph.append(node.to_xml())

        for node in self.groups.values():
            graph.append(node.to_xml())

        for edge in self.edges.values():
            graph.append(edge.to_xml())

        self.graphml = graphml

    def write_graph(self, filename, pretty_print=False):
        self.construct_graphml()

        if pretty_print:
            raw_str = ET.tostring(self.graphml)
            pretty_str = minidom.parseString(raw_str).toprettyxml()
            with open(filename, 'w') as f:
                f.write(pretty_str)
        else:
            tree = ET.ElementTree(self.graphml)
            tree.write(filename)

    def get_graph(self):
        self.construct_graphml()
        # Py2/3 sigh.
        if sys.version_info.major < 3:
            return ET.tostring(self.graphml, encoding='UTF-8')
        else:
            return ET.tostring(self.graphml, encoding='UTF-8').decode()

    def add_node(self, node_name, **kwargs):

        if self.duplicates:
            node_id = self._next_unique_identifier()
        else:
            if node_name in self.existing_entities:
                raise RuntimeWarning("Node %s already exists" % node_name)
            node_id = node_name

        node = Node(node_name, node_id=node_id, **kwargs)
        self.nodes[node_id] = node
        self.existing_entities[node_id] = node
        return node

    def add_edge_by_id(self, nodeid1, nodeid2, **kwargs):
        # pass node names, not actual node objects

        self.existing_entities.get(nodeid1)
        self.existing_entities.get(nodeid2)

        self.num_edges += 1
        kwargs['edge_id'] = str(self.num_edges)
        edge = Edge(nodeid1, nodeid2, **kwargs)
        self.edges[edge.edge_id] = edge
        return edge

    def add_edge(self, node1, node2, **kwargs):
        # pass node names, not actual node objects


        self.num_edges += 1
        kwargs['edge_id'] = str(self.num_edges)
        edge = Edge(node1.node_id, node2.node_id, **kwargs)
        self.edges[edge.edge_id] = edge
        return edge

    def add_group(self, group_id, **kwargs):
        if self.duplicates:
            node_id = self._next_unique_identifier()
        else:
            if group_id in self.existing_entities:
                raise RuntimeWarning("Node %s already exists" % group_id)
            node_id = group_id

        group = Group(group_id, self, node_id=node_id, **kwargs)
        self.groups[node_id] = group
        self.existing_entities[node_id] = group
        return group

    def define_custom_property(self, scope, name, property_type, default_value):
        if scope not in constants.custom_property_scopes:
            raise RuntimeWarning("Scope %s not recognised" % scope)
        if property_type not in constants.custom_property_types:
            raise RuntimeWarning("Property Type %s not recognised" % property_type)
        if type(default_value) != str:
            raise RuntimeWarning("default_value %s needs to be a string" % default_value)
        custom_property = CustomPropertyDefinition(scope, name, property_type, default_value)
        self.custom_properties.append(custom_property)
        if scope == "node":
            Node.set_custom_properties_defs(custom_property)
        elif scope == "edge":
            Edge.set_custom_properties_defs(custom_property)

    def _next_unique_identifier(self):
        """
        Increment internal counter, then return next identifier not yet used.
        """
        self.num_nodes += 1
        node_id = str(self.num_nodes)

        return node_id
