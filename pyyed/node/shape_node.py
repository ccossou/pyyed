import logging
import xml.etree.ElementTree as ET

from . import constants
from .label import NodeLabel
from . import utils
from ..core import Node

LOG = logging.getLogger(__name__)


class ShapeNode(Node):
    custom_properties_defs = {}

    node_type = "ShapeNode"

    validShapes = ["rectangle", "rectangle3d", "roundrectangle", "diamond", "ellipse",
                   "fatarrow", "fatarrow2", "hexagon", "octagon", "parallelogram",
                   "parallelogram2", "star5", "star6", "star6", "star8", "trapezoid",
                   "trapezoid2", "triangle", "trapezoid2", "triangle"]

    def __init__(self, shape="rectangle", **kwargs):
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
        super().__init__(self, **kwargs)

        # node shape
        utils.check_value("shape", shape, Node.validShapes)
        self.shape = shape

    def add_label(self, label_text, **kwargs):
        self.list_of_labels.append(NodeLabel(label_text, **kwargs))
        return self

    def to_xml(self):
        # Generic Node conversion
        Node.to_xml(self)

        ET.SubElement(self.ET_shape, "y:Shape", type=self.shape)

        return self._ET_node

    @classmethod
    def set_custom_properties_defs(cls, custom_property):
        cls.custom_properties_defs[custom_property.name] = custom_property

