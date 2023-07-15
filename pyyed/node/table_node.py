import logging
import sys
import xml.etree.ElementTree as ET

from ..core.label import NodeLabel
from ..core.node import Node

LOG = logging.getLogger(__name__)


class TableNode(Node):
    custom_properties_defs = {}

    node_type = "TableNode"

    def __init__(self, node_name, table, title_background="#b7c9e3", background="#e8eef7", **style_params):
        """

        table = [
        ("Rows", "Name", "Unit"),
        ("Row 0", "toto", "str"),
        ("Row 1", 123, "int"),
        ]

        :param node_name:
        :param dict style_params: common parameters passed to Node.
        """

        self.table = table
        self.check_table()

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
    
    def check_table(self):
        if not isinstance(self.table, list):
            LOG.error(f"Input table need to be a list, got '{type(self.table)}' instead.")
            sys.exit()
        
        n_elem = None
        for line in self.table:
            line_len = len(line)
            if n_elem is None:
                n_elem = line_len
            else:
                if n_elem != line_len:
                    LOG.error(f"All lines in table need the same number of elements")
                    sys.exit()

    def make_row_header_element(self, text, id, parent):

        header_params = {"align": "center", "autoSizePolicy": "content", "font_family": "Dialog", "font_size": "12",
                         "font_style": "plain", "background_color": None, "horizontal_text_position": "center",
        "vertical_text_position": "bottom", "icon_text_gap": "4", "model_name": "custom", "xml:space": "preserve"}

        # <y:NodeLabel hasLineColor="false" height="18.701171875"   rotationAngle="270.0" textColor="#000000"
        # visible="true" width="38.013671875" x="3.0" xml:space="preserve" y="74.9931640625">Row 0<y:LabelModel><y:RowNodeLabelModel offset="3.0"/></y:LabelModel>
        # <y:ModelParameter><y:RowNodeLabelModelParameter horizontalPosition="0.0" id="row_0" inside="true"/></y:ModelParameter></y:NodeLabel>"""

        label = NodeLabel(text, **header_params)
        xml_header = label.addSubElement(parent)

        tmp = ET.SubElement(xml_header, "y:LabelModel")
        ET.SubElement(tmp, "y:RowNodeLabelModel", offset="3.0")
        tmp = ET.SubElement(xml_header, "y:ModelParameter")
        ET.SubElement(tmp, "y:RowNodeLabelModelParameter", horizontalPosition="0.0", id=id, inside="true")

        return xml_header
    def make_col_header_element(self, text, id, parent):

        header_params = {"align": "center", "autoSizePolicy": "content", "font_family": "Dialog", "font_size": "12",
                         "font_style": "plain", "background_color": None, "horizontal_text_position": "center",
        "vertical_text_position": "bottom", "icon_text_gap": "4", "model_name": "custom", "xml:space": "preserve"}

        # <y:NodeLabel hasLineColor="false" height="18.701171875" textColor="#000000" visible="true"
        # width="55.357421875" x="56.3212890625" y="33.0">Column 0<y:LabelModel><y:ColumnNodeLabelModel offset="3.0"/>
        # </y:LabelModel><y:ModelParameter><y:ColumnNodeLabelModelParameter id="column_0" inside="true" verticalPosition="0.0"/></y:ModelParameter></y:NodeLabel>

        label = NodeLabel(text, **header_params)
        xml_header = label.addSubElement(parent)

        tmp = ET.SubElement(xml_header, "y:LabelModel")
        ET.SubElement(tmp, "y:ColumnNodeLabelModel", offset="3.0")
        tmp = ET.SubElement(xml_header, "y:ModelParameter")
        ET.SubElement(tmp, "y:ColumnNodeLabelModelParameter", verticalPosition="0.0", id=id, inside="true")

        return xml_header

    def make_cell_element(self, text, parent):

        header_params = {"align": "center", "autoSizePolicy": "content", "font_family": "Dialog", "font_size": "12",
                         "font_style": "plain", "background_color": None, "horizontal_text_position": "center",
        "vertical_text_position": "bottom", "icon_text_gap": "4", "model_name": "custom", "xml:space": "preserve"}

        # <y:NodeLabel hasLineColor="false" height="18.701171875" textColor="#000000" visible="true"
        # width="23.341796875" x="30.7651515151515" y="73.5">test<y:LabelModel><y:SmartNodeLabelModel distance="4.0"/>
        # </y:LabelModel><y:ModelParameter><y:SmartNodeLabelModelParameter labelRatioX="-0.5"
        # labelRatioY="-0.5" nodeRatioX="-0.2518939393939394" nodeRatioY="-0.25" offsetX="0.0" offsetY="0.0" upX="0.0" upY="-1.0"/></y:ModelParameter></y:NodeLabel>
        label = NodeLabel(text, **header_params)
        xml_cell = label.addSubElement(parent)

        # <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain"
        # hasBackgroundColor="false" hasLineColor="false" height="18.701171875" horizontalTextPosition="center"
        # iconTextGap="4" modelName="custom" textColor="#000000" verticalTextPosition="bottom" visible="true"
        # width="30.015625" x="71.2114109848485" xml:space="preserve" y="78.5">test2<y:LabelModel>
        # <y:SmartNodeLabelModel distance="4.0"/></y:LabelModel><y:ModelParameter><y:SmartNodeLabelModelParameter
        # labelRatioX="0.5" labelRatioY="-0.5" nodeRatioX="0.31634706439393945" nodeRatioY="-0.23299319727891155"
        # offsetX="0.0" offsetY="0.0" upX="0.0" upY="-1.0"/></y:ModelParameter></y:NodeLabel>

        # <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain"
        # hasBackgroundColor="false" hasLineColor="false" height="18.701171875" horizontalTextPosition="center"
        # iconTextGap="4" modelName="custom" textColor="#000000" verticalTextPosition="bottom" visible="true"
        # width="30.015625" x="31.2348484848485" xml:space="preserve" y="177.5">test3<y:LabelModel>
        # <y:SmartNodeLabelModel distance="4.0"/></y:LabelModel><y:ModelParameter><y:SmartNodeLabelModelParameter
        # labelRatioX="-0.5" labelRatioY="0.5" nodeRatioX="-0.2481060606060606" nodeRatioY="0.167350924744898"
        # offsetX="0.0" offsetY="0.0" upX="0.0" upY="-1.0"/></y:ModelParameter></y:NodeLabel>

        # Line 1
        #   cell 1: labelRatioX="-0.5", labelRatioY="-0.5"
        #   cell 2: labelRatioX="0.5",  labelRatioY="-0.5"
        # Line 2
        #   cell 1: labelRatioX="-0.5", labelRatioY="0.5"
        #   cell 2:

        tmp = ET.SubElement(xml_cell, "y:LabelModel")
        ET.SubElement(tmp, "y:SmartNodeLabelModel", distance="4.0")
        tmp = ET.SubElement(xml_cell, "y:ModelParameter")
        ET.SubElement(tmp, "y:SmartNodeLabelModelParameter", labelRatioX="-0.5", labelRatioY="-0.5",
                      offsetX="0.0", offsetY="0.0", upX="0.0", upY="-1.0")

        return xml_cell




    def to_xml(self):
        # Generic Node conversion
        Node.to_xml(self)

        # Add attribute to node type
        self._ET_node.set("yfiles.foldertype", "group")
        
        self._ET_shape.set("configuration", "YED_TABLE_NODE")

        header = self.table[0]
        for (i, text) in enumerate(header[1:]):
            idx = f"column_{i}"
            xml_header = self.make_col_header_element(text, idx, self._ET_shape)

        for row_id, line in enumerate(self.table[1:]):
            # Row header first
            row_name = line[0]
            idx = f"row_{row_id}"
            xml_header = self.make_row_header_element(row_name, idx, self._ET_shape)
            for (i, text) in enumerate(line):

                xml_cell = self.make_row_header_element(text, idx, self._ET_shape)

                # <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18.701171875" horizontalTextPosition="center" iconTextGap="4" modelName="custom" textColor="#000000" verticalTextPosition="bottom" visible="true" width="23.341796875" x="30.7651515151515" xml:space="preserve" y="73.5">test<y:LabelModel><y:SmartNodeLabelModel distance="4.0"/></y:LabelModel><y:ModelParameter><y:SmartNodeLabelModelParameter labelRatioX="-0.5" labelRatioY="-0.5" nodeRatioX="-0.2518939393939394" nodeRatioY="-0.25" offsetX="0.0" offsetY="0.0" upX="0.0" upY="-1.0"/></y:ModelParameter></y:NodeLabel>

        desc_label_node = self.description_label.addSubElement(self._ET_shape)
        tmp = ET.SubElement(desc_label_node, "y:LabelModel")
        ET.SubElement(tmp, "y:ErdAttributesNodeLabelModel")
        tmp = ET.SubElement(desc_label_node, "y:ModelParameter")
        ET.SubElement(tmp, "y:ErdAttributesNodeLabelModelParameter")

        style_element = ET.SubElement(self._ET_shape, "y:StyleProperties")
        ET.SubElement(style_element, "y:Property", attrib={"class":"java.awt.Color", "name":"yed.table.section.color", "value":"#7192b2"})
        ET.SubElement(style_element, "y:Property", attrib={"class":"java.lang.Double", "name":"yed.table.header.height", "value":"24.0"})
        ET.SubElement(style_element, "y:Property", attrib={"class":"java.awt.Color", "name":"yed.table.lane.color.main", "value":"#c4d7ed"})
        ET.SubElement(style_element, "y:Property", attrib={"class":"java.awt.Color", "name":"yed.table.lane.color.alternating", "value":"#abc8e2"})
        ET.SubElement(style_element, "y:Property", attrib={"class":"java.awt.Color", "name":"yed.table.header.color.alternating", "value":"#abc8e2"})
        ET.SubElement(style_element, "y:Property", attrib={"class":"java.lang.String", "name":"yed.table.lane.style", "value":"lane.style.rows"})
        ET.SubElement(style_element, "y:Property", attrib={"class":"java.awt.Color", "name":"yed.table.header.color.main", "value":"#c4d7ed"})

        return self._ET_node

    @classmethod
    def set_custom_properties_defs(cls, custom_property):
        cls.custom_properties_defs[custom_property.name] = custom_property
