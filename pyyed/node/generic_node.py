import logging
import xml.etree.ElementTree as ET

from ..core.label import NodeLabel
from ..core.node import Node

LOG = logging.getLogger(__name__)


class GenericNode(Node):
    custom_properties_defs = {}

    node_type = "GenericNode"

    def __init__(self, node_name, description, title_background="#b7c9e3", background="#e8eef7", **style_params):
        """

        :param node_name:
        :param dict style_params: common parameters passed to Node.
        """
        # Update to have a default background than the default
        style_params["background"] = background

        super().__init__(node_name, **style_params)

        # modify generic title label for GenericNode specificity
        self.list_of_labels[0].updateParam("configuration", "com.yworks.entityRelationship.label.name")
        self.list_of_labels[0].updateParam("modelName", "internal")
        self.list_of_labels[0].updateParam("modelPosition", "t")
        self.list_of_labels[0].updateParam("verticalTextPosition", "bottom")
        self.list_of_labels[0].updateParam("backgroundColor", title_background)
        self.list_of_labels[0].updateParam("hasBackgroundColor", "True")

        self.label_style["alignment"] = "left"
        self.description_label = NodeLabel(description, configuration="com.yworks.entityRelationship.label.attributes",
                       verticalTextPosition="top", model_name="custom", model_position=None, **self.label_style)


        # Dans le 2e label, il faut rajouter avant la fin du noeud de label: <y:LabelModel><y:ErdAttributesNodeLabelModel/></y:LabelModel>
        # il faut aussi rajouter la configuration suivante au noeud: y:GenericNode configuration="com.yworks.entityRelationship.big_entity"
        # et enfin, il faut le placement custom, sans position
        # il faut aussi ça on dirait: <y:ModelParameter><y:ErdAttributesNodeLabelModelParameter/></y:ModelParameter>

    def add_label(self, label_text, **kwargs):
        self.list_of_labels.append(NodeLabel(label_text, **kwargs))
        return self

    def to_xml(self):
        # Generic Node conversion
        Node.to_xml(self)

        # Add attribute to node type
        self._ET_shape.set("configuration", "com.yworks.entityRelationship.big_entity")

        desc_label_node = self.description_label.addSubElement(self._ET_shape)
        tmp = ET.SubElement(desc_label_node, "y:LabelModel")
        ET.SubElement(tmp, "y:ErdAttributesNodeLabelModel")
        tmp = ET.SubElement(desc_label_node, "y:ModelParameter")
        ET.SubElement(tmp, "y:ErdAttributesNodeLabelModelParameter")

        style_element = ET.SubElement(self._ET_shape, "y:StyleProperties")
        ET.SubElement(style_element, "y:Property", attrib={"class":"java.lang.Boolean",
        "name":"y.view.ShadowNodePainter.SHADOW_PAINTING", "value":"false"})

        return self._ET_node

    @classmethod
    def set_custom_properties_defs(cls, custom_property):
        cls.custom_properties_defs[custom_property.name] = custom_property
