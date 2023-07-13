import logging
import xml.etree.ElementTree as ET

from . import constants
from . import utils

LOG = logging.getLogger(__name__)


class Label:
    graphML_tagName = None

    def __init__(self, text, height="18.1328125", width=None,
                 alignment="center",
                 font_family="Dialog",
                 font_size="12",
                 font_style="plain",
                 underlined_text = "false",
                 text_color="#000000",
                 icon_text_gap="4",
                 horizontal_text_position="center",
                 vertical_text_position="center",
                 visible="true",
                 border_color=None,
                 background_color=None):

        # make class abstract
        if type(self) is Label:
            raise Exception('Label is an abstract class and cannot be instantiated directly')

        self._text = text

        # Initialize dictionary for parameters
        self._params = {}
        self.updateParam("horizontalTextPosition", horizontal_text_position, constants.horizontal_alignments)
        self.updateParam("verticalTextPosition", vertical_text_position, constants.vertical_alignments)
        self.updateParam("alignment", alignment, constants.horizontal_alignments)
        self.updateParam("fontStyle", font_style, constants.font_styles)

        # TODO: Implement range checks
        self.updateParam("fontFamily", font_family)
        self.updateParam("iconTextGap", icon_text_gap)
        self.updateParam("fontSize", font_size)
        self.updateParam("textColor", text_color)
        self.updateParam("visible", visible.lower(), ["true", "false"])
        self.updateParam("underlinedText", underlined_text.lower(), ["true", "false"])
        if background_color is not None:
            has_background_color = "true"
            self.updateParam("backgroundColor", background_color)
        else:
            has_background_color = "false"
        self.updateParam("hasBackgroundColor", has_background_color.lower(), ["true", "false"])
        self.updateParam("width", width)
        self.updateParam("height", height)
        self.updateParam("borderColor", border_color)

    def updateParam(self, parameter_name, value, validValues=None):
        if value is None:
            return False
        utils.check_value(parameter_name, value, validValues)

        self._params[parameter_name] = value
        return True

    def addSubElement(self, shape):
        label = ET.SubElement(shape, self.graphML_tagName, **self._params)
        label.text = self._text


class NodeLabel(Label):
    validModelParams = {
        "internal": ["t", "b", "c", "l", "r", "tl", "tr", "bl", "br"],
        "corners": ["nw", "ne", "sw", "se"],
        "sandwich": ["n", "s"],
        "sides": ["n", "e", "s", "w"],
        "eight_pos": ["n", "e", "s", "w", "nw", "ne", "sw", "se"],
        "free": ["anywhere"],
    }

    autoSizePolicy_values = ["node_width", "node_size", "node_height", "content"]

    graphML_tagName = "y:NodeLabel"

    def __init__(self, text, model_name="internal", model_position="c", autoSizePolicy="content", **kwargs):
        super().__init__(text, **kwargs)

        self.updateParam("modelName", model_name, self.__class__.validModelParams.keys())
        self.updateParam("modelPosition", model_position, self.__class__.validModelParams[model_name])
        self.updateParam("autoSizePolicy", autoSizePolicy, self.__class__.autoSizePolicy_values)


class EdgeLabel(Label):
    validModelParams = {
        "two_pos": ["head", "tail"],
        "centered": ["center"],
        "six_pos": ["shead", "thead", "head", "stail", "ttail", "tail"],
        "three_center": ["center", "scentr", "tcentr"],
        "center_slider": None,
        "side_slider": None,
        "free": ["anywhere"],
    }

    graphML_tagName = "y:EdgeLabel"

    def __init__(self, text, model_name="centered", model_position="center", preferred_placement=None, **kwargs):
        super().__init__(text, **kwargs)

        self.updateParam("modelName", model_name, self.__class__.validModelParams.keys())
        self.updateParam("modelPosition", model_position, self.__class__.validModelParams[model_name])
        self.updateParam("preferredPlacement", preferred_placement)
