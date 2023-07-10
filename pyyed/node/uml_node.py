import logging
import xml.etree.ElementTree as ET

from ..core.label import NodeLabel
from ..core.node import Node

LOG = logging.getLogger(__name__)


class UmlNode(Node):
    node_type = "UMLClassNode"

    def __init__(self, node_name, UML, **kwargs):
        """

        :param node_name:
        :param UML:
        """
        super().__init__(node_name, **kwargs)
        self.UML = UML


    def add_label(self, label_text, **kwargs):
        self.list_of_labels.append(NodeLabel(label_text, **kwargs))
        return self

    def to_xml(self):

        # Generic Node conversion
        Node.to_xml(self)

        UML = ET.SubElement(self._ET_shape, "y:UML", use3DEffect="false")

        attributes = ET.SubElement(UML, "y:AttributeLabel")
        attributes.text = self.UML["attributes"]

        methods = ET.SubElement(UML, "y:MethodLabel")
        methods.text = self.UML["methods"]

        stereotype = self.UML["stereotype"] if "stereotype" in self.UML else ""
        UML.set("stereotype", stereotype)

        return self._ET_node

    @classmethod
    def set_custom_properties_defs(cls, custom_property):
        cls.custom_properties_defs[custom_property.name] = custom_property

