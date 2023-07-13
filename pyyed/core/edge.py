import logging
import xml.etree.ElementTree as ET

from . import constants
from .label import EdgeLabel
from .item import XmlItem
from . import utils

LOG = logging.getLogger(__name__)


class Edge(XmlItem):
    def __init__(self, node1, node2, label=None, arrowhead="standard", arrowfoot="none",
                 color="#000000", line_type="line", width="1.0",
                 label_background_color="", label_border_color="",
                 source_label=None, target_label=None,
                 description="", url="", **kwargs):
        super().__init__(**kwargs)
        self.node1 = node1
        self.node2 = node2

        self.list_of_labels = []  # initialize list of labels

        if label:
            self.add_label(label, border_color=label_border_color, background_color=label_background_color)

        if source_label is not None:
            self.add_label(source_label, model_name="six_pos", model_position="shead",
                           preferred_placement="source_on_edge",
                           border_color=label_border_color, background_color=label_background_color)

        if target_label is not None:
            self.add_label(source_label, model_name="six_pos", model_position="shead",
                           preferred_placement="source_on_edge",
                           border_color=label_border_color, background_color=label_background_color)

        utils.check_value("arrowhead", arrowhead, constants.arrow_types)
        self.arrowhead = arrowhead

        utils.check_value("arrowfoot", arrowfoot, constants.arrow_types)
        self.arrowfoot = arrowfoot

        utils.check_value("line_type", line_type, constants.line_types)
        self.line_type = line_type

        self.color = color
        self.width = width

        self.description = description
        self.url = url


    def add_label(self, label_text, **kwargs):
        self.list_of_labels.append(EdgeLabel(label_text, **kwargs))
        # Enable method chaining
        return self

    def to_xml(self):
        edge = ET.Element("edge", id=str(self.id), source=str(self.node1.id), target=str(self.node2.id))
        data = ET.SubElement(edge, "data", key="data_edge")
        pl = ET.SubElement(data, "y:PolyLineEdge")

        ET.SubElement(pl, "y:Arrows", source=self.arrowfoot, target=self.arrowhead)
        ET.SubElement(pl, "y:LineStyle", color=self.color, type=self.line_type,
                      width=self.width)

        for label in self.list_of_labels:
            label.addSubElement(pl)

        if self.url:
            url_edge = ET.SubElement(edge, "data", key="url_edge")
            url_edge.text = self.url

        if self.description:
            description_edge = ET.SubElement(edge, "data", key="description_edge")
            description_edge.text = self.description

        return edge
