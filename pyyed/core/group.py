import logging
import xml.etree.ElementTree as ET

from . import constants
from .node import Node
from .edge import Edge
from . import utils

LOG = logging.getLogger(__name__)


class Group:
    validShapes = ["rectangle", "rectangle3d", "roundrectangle", "diamond", "ellipse",
                   "fatarrow", "fatarrow2", "hexagon", "octagon", "parallelogram",
                   "parallelogram2", "star5", "star6", "star6", "star8", "trapezoid",
                   "trapezoid2", "triangle", "trapezoid2", "triangle"]

    def __init__(self, group_id, parent_graph, label=None, label_alignment="center", shape="rectangle",
                 closed="false", font_family="Dialog", underlined_text="false",
                 font_style="plain", font_size="12", fill="#FFCC00", transparent="false",
                 border_color="#000000", border_type="line", border_width="1.0", height=False,
                 width=False, x=False, y=False, custom_properties=None, description="", url="", node_id=None):
        """

        :param group_id:
        :param parent_graph:
        :param label:
        :param label_alignment:
        :param shape:
        :param closed:
        :param font_family:
        :param underlined_text:
        :param font_style:
        :param font_size:
        :param fill:
        :param transparent:
        :param border_color:
        :param border_type:
        :param border_width:
        :param height:
        :param width:
        :param x:
        :param y:
        :param custom_properties:
        :param description:
        :param url:
        :param node_id: If set, will allow a different name than the node_name (to allow duplicates)
        """
        self.label = label
        if label is None:
            self.label = group_id

        self.parent = None
        self.group_id = group_id

        if node_id is not None:
            self.node_id = node_id
        else:
            self.node_id = group_id

        self.nodes = {}
        self.groups = {}
        self.parent_graph = parent_graph
        self.edges = {}
        self.num_edges = 0

        # node shape
        utils.check_value("shape", shape, Group.validShapes)
        self.shape = shape

        self.closed = closed

        # label formatting options
        self.font_family = font_family
        self.underlined_text = underlined_text

        utils.check_value("font_style", font_style, constants.font_styles)
        self.font_style = font_style
        self.font_size = font_size

        utils.check_value("label_alignment", label_alignment, constants.horizontal_alignments)
        self.label_alignment = label_alignment

        self.fill = fill
        self.transparent = transparent

        self.geom = {}
        if height:
            self.geom["height"] = height
        if width:
            self.geom["width"] = width
        if x:
            self.geom["x"] = x
        if y:
            self.geom["y"] = y

        self.border_color = border_color
        self.border_width = border_width

        utils.check_value("border_type", border_type, constants.line_types)
        self.border_type = border_type

        self.description = description
        self.url = url

        # Handle Node Custom Properties
        for name, definition in Node.custom_properties_defs.items():
            if custom_properties:
                for k, v in custom_properties.items():
                    if k not in Node.custom_properties_defs:
                        raise RuntimeWarning("key %s not recognised" % k)
                    if name == k:
                        setattr(self, name, custom_properties[k])
                        break
                else:
                    setattr(self, name, definition.default_value)
            else:
                setattr(self, name, definition.default_value)

    def add_node(self, node_name, **kwargs):
        if self.parent_graph.duplicates:
            node_id = self.parent_graph._next_unique_identifier()
        else:
            if node_name in self.parent_graph.existing_entities:
                raise RuntimeWarning("Node %s already exists" % node_name)
            node_id = node_name

        node = Node(node_name, node_id=node_id, **kwargs)
        node.parent = self
        self.nodes[node_id] = node
        self.parent_graph.existing_entities[node_id] = node
        return node

    def add_group(self, group_id, **kwargs):
        if self.parent_graph.duplicates:
            node_id = self.parent_graph._next_unique_identifier()
        else:
            if group_id in self.parent_graph.existing_entities:
                raise RuntimeWarning("Node %s already exists" % group_id)
            node_id = group_id

        group = Group(group_id, self.parent_graph, node_id=node_id, allow_duplicates=self.duplicates, **kwargs)
        group.parent = self
        self.groups[node_id] = group
        self.parent_graph.existing_entities[node_id] = group
        return group

    def is_ancestor(self, node):
        return node.parent is not None and (
                node.parent is self or self.is_ancestor(node.parent))

    def add_edge(self, node1_name, node2_name, **kwargs):
        # pass node names, not actual node objects

        node1 = self.parent_graph.existing_entities.get(node1_name) or \
                self.add_node(node1_name)

        node2 = self.parent_graph.existing_entities.get(node2_name) or \
                self.add_node(node2_name)

        # http://graphml.graphdrawing.org/primer/graphml-primer.html#Nested
        # The edges between two nodes in a nested graph have to be declared in a graph,
        # which is an ancestor of both nodes in the hierarchy.

        if not (self.is_ancestor(node1) and self.is_ancestor(node2)):
            raise RuntimeWarning("Group %s is not ancestor of both %s and %s" % (self.group_id, node1_name, node2_name))

        self.parent_graph.num_edges += 1
        kwargs['edge_id'] = str(self.parent_graph.num_edges)
        edge = Edge(node1_name, node2_name, **kwargs)
        self.edges[edge.edge_id] = edge
        return edge

    def add_edge_by_obj(self, node1, node2, **kwargs):
        # pass node names, not actual node objects

        # http://graphml.graphdrawing.org/primer/graphml-primer.html#Nested
        # The edges between two nodes in a nested graph have to be declared in a graph,
        # which is an ancestor of both nodes in the hierarchy.

        if not (self.is_ancestor(node1) and self.is_ancestor(node2)):
            raise RuntimeWarning("Group %s is not ancestor of both %s and %s" % (self.group_id, node1.node_name,
                                                                                 node2.node_name))

        self.parent_graph.num_edges += 1
        kwargs['edge_id'] = str(self.parent_graph.num_edges)
        edge = Edge(node1.node_id, node2.node_id, **kwargs)
        self.edges[edge.edge_id] = edge
        return edge

    def convert(self):
        node = ET.Element("node", id=self.node_id)
        node.set("yfiles.foldertype", "group")
        data = ET.SubElement(node, "data", key="data_node")

        # node for group
        pabn = ET.SubElement(data, "y:ProxyAutoBoundsNode")
        r = ET.SubElement(pabn, "y:Realizers", active="0")
        group_node = ET.SubElement(r, "y:GroupNode")

        if self.geom:
            ET.SubElement(group_node, "y:Geometry", **self.geom)

        ET.SubElement(group_node, "y:Fill", color=self.fill, transparent=self.transparent)

        ET.SubElement(group_node, "y:BorderStyle", color=self.border_color,
                      type=self.border_type, width=self.border_width)

        label = ET.SubElement(group_node, "y:NodeLabel", modelName="internal",
                              modelPosition="t",
                              fontFamily=self.font_family, fontSize=self.font_size,
                              underlinedText=self.underlined_text,
                              fontStyle=self.font_style,
                              alignment=self.label_alignment)
        label.text = self.label

        ET.SubElement(group_node, "y:Shape", type=self.shape)

        ET.SubElement(group_node, "y:State", closed=self.closed)

        graph = ET.SubElement(node, "graph", edgedefault="directed", id=self.group_id)

        if self.url:
            url_node = ET.SubElement(node, "data", key="url_node")
            url_node.text = self.url

        if self.description:
            description_node = ET.SubElement(node, "data", key="description_node")
            description_node.text = self.description

        for node_id in self.nodes:
            n = self.nodes[node_id].convert()
            graph.append(n)

        for group_id in self.groups:
            n = self.groups[group_id].convert()
            graph.append(n)

        for edge_id in self.edges:
            e = self.edges[edge_id].convert()
            graph.append(e)

        # Node Custom Properties
        for name, definition in Node.custom_properties_defs.items():
            node_custom_prop = ET.SubElement(node, "data", key=definition.id)
            node_custom_prop.text = getattr(self, name)

        return node
        # ProxyAutoBoundsNode crap just draws bar at top of group

