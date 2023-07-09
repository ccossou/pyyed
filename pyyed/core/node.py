import logging
import xml.etree.ElementTree as ET

from . import constants
from .label import NodeLabel
from . import utils

LOG = logging.getLogger(__name__)


class Node:
    custom_properties_defs = {}

    validShapes = ["rectangle", "rectangle3d", "roundrectangle", "diamond", "ellipse",
                   "fatarrow", "fatarrow2", "hexagon", "octagon", "parallelogram",
                   "parallelogram2", "star5", "star6", "star6", "star8", "trapezoid",
                   "trapezoid2", "triangle", "trapezoid2", "triangle"]

    def __init__(self, node_name, label=None, label_alignment="center", shape="rectangle", font_family="Dialog",
                 underlined_text="false", font_style="plain", font_size="12",
                 shape_fill="#FF0000", transparent="false", border_color="#000000",
                 border_type="line", border_width="1.0", height=False, width=False, x=False,
                 y=False, node_type="ShapeNode", UML=False,
                 custom_properties=None, description="", url="", node_id=None):
        """

        :param node_name:
        :param label:
        :param label_alignment:
        :param shape:
        :param font_family:
        :param underlined_text:
        :param font_style:
        :param font_size:
        :param shape_fill:
        :param transparent:
        :param border_color:
        :param border_type:
        :param border_width:
        :param height:
        :param width:
        :param x:
        :param y:
        :param node_type:
        :param UML:
        :param custom_properties:
        :param description:
        :param url:
        :param node_id: If set, will allow a different name than the node_name (to allow duplicates)
        """

        self.list_of_labels = []  # initialize list of labels
        if label:
            self.add_label(label, alignment=label_alignment,
                           font_family=font_family, underlined_text=underlined_text,
                           font_style=font_style, font_size=font_size)
        else:
            self.add_label(node_name, alignment=label_alignment,
                           font_family=font_family, underlined_text=underlined_text,
                           font_style=font_style, font_size=font_size)

        self.node_name = node_name

        if node_id is not None:
            self.node_id = node_id
        else:
            self.node_id = node_name

        self.node_type = node_type
        self.UML = UML

        self.parent = None

        # node shape
        utils.check_value("shape", shape, Node.validShapes)
        self.shape = shape

        # shape fill
        self.shape_fill = shape_fill
        self.transparent = transparent

        # border options
        self.border_color = border_color
        self.border_width = border_width

        utils.check_value("border_type", border_type, constants.line_types)
        self.border_type = border_type

        # geometry
        self.geom = {}
        if height:
            self.geom["height"] = height
        if width:
            self.geom["width"] = width
        if x:
            self.geom["x"] = x
        if y:
            self.geom["y"] = y

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

    def add_label(self, label_text, **kwargs):
        self.list_of_labels.append(NodeLabel(label_text, **kwargs))
        return self

    def to_xml(self):

        node = ET.Element("node", id=str(self.node_id))
        data = ET.SubElement(node, "data", key="data_node")
        shape = ET.SubElement(data, "y:" + self.node_type)

        if self.geom:
            ET.SubElement(shape, "y:Geometry", **self.geom)
        # <y:Geometry height="30.0" width="30.0" x="475.0" y="727.0"/>

        ET.SubElement(shape, "y:Fill", color=self.shape_fill,
                      transparent=self.transparent)

        ET.SubElement(shape, "y:BorderStyle", color=self.border_color, type=self.border_type,
                      width=self.border_width)

        for label in self.list_of_labels:
            label.addSubElement(shape)

        ET.SubElement(shape, "y:Shape", type=self.shape)

        if self.UML:
            UML = ET.SubElement(shape, "y:UML", use3DEffect="false")

            attributes = ET.SubElement(UML, "y:AttributeLabel", type=self.shape)
            attributes.text = self.UML["attributes"]

            methods = ET.SubElement(UML, "y:MethodLabel", type=self.shape)
            methods.text = self.UML["methods"]

            stereotype = self.UML["stereotype"] if "stereotype" in self.UML else ""
            UML.set("stereotype", stereotype)

        if self.url:
            url_node = ET.SubElement(node, "data", key="url_node")
            url_node.text = self.url

        if self.description:
            description_node = ET.SubElement(node, "data", key="description_node")
            description_node.text = self.description

        # Node Custom Properties
        for name, definition in Node.custom_properties_defs.items():
            node_custom_prop = ET.SubElement(node, "data", key=definition.id)
            node_custom_prop.text = getattr(self, name)

        return node

    @classmethod
    def set_custom_properties_defs(cls, custom_property):
        cls.custom_properties_defs[custom_property.name] = custom_property

