import logging
import xml.etree.ElementTree as ET

from . import constants
from .label import NodeLabel
from .item import XmlItem
from . import utils

LOG = logging.getLogger(__name__)


class Node(XmlItem):
    node_type = None

    validShapes = ["rectangle", "rectangle3d", "roundrectangle", "diamond", "ellipse",
                   "fatarrow", "fatarrow2", "hexagon", "octagon", "parallelogram",
                   "parallelogram2", "star5", "star6", "star6", "star8", "trapezoid",
                   "trapezoid2", "triangle", "trapezoid2", "triangle"]

    def __init__(self, node_name, label_alignment="center", font_family="Dialog",
                 underlined_text="false", font_style="plain", font_size="12",
                 shape_fill="#FF0000", transparent="false", border_color="#000000",
                 border_type="line", border_width="1.0", height=False, width=False, x=False,
                 y=False,
                 description="", url=""):
        """

        :param node_name:
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
        :param description:
        :param url:
        :param node_id: If set, will allow a different name than the node_name (to allow duplicates)
        """
        super().__init__()

        self.list_of_labels = []  # initialize list of labels

        self.add_label(node_name, alignment=label_alignment,
                       font_family=font_family, underlined_text=underlined_text,
                       font_style=font_style, font_size=font_size)

        self.name = node_name

        self.parent = None

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

        # Future storage for xml object nodes
        self._ET_node = None
        self._ET_data = None
        self._ET_shape = None

    def add_label(self, label_text, **kwargs):
        self.list_of_labels.append(NodeLabel(label_text, **kwargs))
        return self

    def to_xml(self):
        """
        Init in the parent class all XML items that are common to all child classes
        """
        self._ET_node = ET.Element("node", id=str(self.id))
        self._ET_data = ET.SubElement(self._ET_node, "data", key="data_node")
        self._ET_shape = ET.SubElement(self._ET_data, "y:" + self.node_type)

        if self.geom:
            ET.SubElement(self._ET_shape, "y:Geometry", **self.geom)
        # <y:Geometry height="30.0" width="30.0" x="475.0" y="727.0"/>

        ET.SubElement(self._ET_shape, "y:Fill", color=self.shape_fill,
                      transparent=self.transparent)

        ET.SubElement(self._ET_shape, "y:BorderStyle", color=self.border_color, type=self.border_type,
                      width=self.border_width)

        for label in self.list_of_labels:
            label.addSubElement(self._ET_shape)

        if self.url:
            url_node = ET.SubElement(self._ET_node, "data", key="url_node")
            url_node.text = self.url

        if self.description:
            description_node = ET.SubElement(self._ET_node, "data", key="description_node")
            description_node.text = self.description
