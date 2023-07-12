import logging

LOG = logging.getLogger(__name__)

class XmlItem:
    # Variable to ensure unique ID of all nodes/groups/etc...
    identifier = None
    counter = 0

    def __init__(self):
        self.__class__.counter += 1
        self.__class__.identifier = self.__class__.__name__

    @property
    def id(self):
        return f"{self.identifier}_{self.counter}"
