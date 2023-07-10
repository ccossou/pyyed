import logging

from .shape_node import ShapeNode
from .uml_node import UmlNode

LOG = logging.getLogger(__name__)


def make_node(node_name, **kwargs):
    """

    :param node_name:
    :param kwargs:
    :return:
    """
    if "UML" in kwargs.keys():
        NodeType = UmlNode
    else:
        NodeType = ShapeNode

    node = NodeType(node_name, **kwargs)

    return node