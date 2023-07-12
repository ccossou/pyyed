import logging
import xml.etree.ElementTree as ET

from . import constants
from .. import node as nodes
from .edge import Edge
from . import utils
from .item import XmlItem

LOG = logging.getLogger(__name__)


class Group(XmlItem):
    validShapes = ["rectangle", "rectangle3d", "roundrectangle", "diamond", "ellipse",
                   "fatarrow", "fatarrow2", "hexagon", "octagon", "parallelogram",
                   "parallelogram2", "star5", "star6", "star6", "star8", "trapezoid",
                   "trapezoid2", "triangle", "trapezoid2", "triangle"]

    def __init__(self, name, parent_graph, label=None, label_alignment="center", shape="rectangle",
                 closed="false", font_family="Dialog", underlined_text="false",
                 font_style="plain", font_size="12", fill="#FFCC00", transparent="false",
                 border_color="#000000", border_type="line", border_width="1.0", height=False,
                 width=False, x=False, y=False, description="", url=""):
        """

        :param name:
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
        :param description:
        :param url:
        """
        super().__init__()

        self.label = label
        if label is None:
            self.label = name

        self.parent = None
        self.name = name

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

    def add_node(self, node_name, **kwargs):
        node = nodes.make_node(node_name, **kwargs)
        node.parent = self
        self.nodes[node.id] = node
        self.parent_graph.existing_entities[node.id] = node
        return node

    def add_group(self, name, **kwargs):
        group = Group(name, self.parent_graph, **kwargs)
        group.parent = self
        self.groups[group.id] = group
        self.parent_graph.existing_entities[group.id] = group
        return group

    def is_ancestor(self, node):
        return node.parent is not None and (
                node.parent is self or self.is_ancestor(node.parent))


    def add_edge(self, node1, node2, **kwargs):
        # pass node objects

        # http://graphml.graphdrawing.org/primer/graphml-primer.html#Nested
        # The edges between two nodes in a nested graph have to be declared in a graph,
        # which is an ancestor of both nodes in the hierarchy.

        if not (self.is_ancestor(node1) and self.is_ancestor(node2)):
            raise RuntimeWarning("Group %s is not ancestor of both %s and %s" % (self.name, node1.node_name,
                                                                                 node2.node_name))

        edge = Edge(node1, node2, **kwargs)
        self.edges[edge.id] = edge
        return edge

    def to_xml(self):
        xml_node = ET.Element("node", id=self.id)
        xml_node.set("yfiles.foldertype", "group")
        data = ET.SubElement(xml_node, "data", key="data_node")

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

        graph = ET.SubElement(xml_node, "graph", edgedefault="directed", id=self.name)

        if self.url:
            url_node = ET.SubElement(xml_node, "data", key="url_node")
            url_node.text = self.url

        if self.description:
            description_node = ET.SubElement(xml_node, "data", key="description_node")
            description_node.text = self.description

        for node in self.nodes.values():
            graph.append(node.to_xml())

        for grp in self.groups.values():
            graph.append(grp.to_xml())

        for edge in self.edges.values():
            graph.append(edge.to_xml())

        return xml_node
