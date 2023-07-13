import logging

LOG = logging.getLogger(__name__)

class XmlItem:
    """
    Generic class to whom all graph object derive (node, group and edges)
    """
    # Variable to ensure unique ID of all nodes/groups/etc...
    identifier = None
    _class_counter = 0

    def __init__(self, parent):
        self.__class__._class_counter += 1
        self.counter = self.__class__._class_counter

        self.__class__.identifier = self.__class__.__name__

        self.parent = parent
        self.parent_graph = parent.parent_graph

    @property
    def id(self):
        return f"{self.identifier}_{self.counter}"
