import logging
import sys

from ..core.label import NodeLabel
from .generic_node import GenericNode

LOG = logging.getLogger(__name__)


class TableNode(GenericNode):
    custom_properties_defs = {}

    node_type = "GenericNode"

    def __init__(self, node_name, table, **style_params):
        """

        Table Node only works if <html> is next to the label start. If there's a new line in between, it won't work. As
        a consequence, I had to get rid of minidom pretty print to make it work from scratch.

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

        # Add an html version of our table as a description in GenericNode
        html_txt = self.make_html_table(table)

        super().__init__(node_name, description=html_txt, **style_params)

    def make_html_table(self, table):
        html_txt = "<html>"
        html_txt += "<table border='1' style='border-collapse: collapse;'>"

        header = True
        for line in table:
            html_txt += "<tr>"

            if header:
                cell = "th"
                header = False
            else:
                cell = "td"

            for text in line:
                html_txt += f"<{cell}>{text}</{cell}>"

            html_txt += "</tr>"

        html_txt += "</table></html>"

        return html_txt

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


    def to_xml(self):
        # Generic Node conversion
        super().to_xml()

        return self._ET_node

    @classmethod
    def set_custom_properties_defs(cls, custom_property):
        cls.custom_properties_defs[custom_property.name] = custom_property
