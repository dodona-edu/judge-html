import tinycss2
from tinycss2.ast import FunctionBlock, IdentToken, Node, WhitespaceToken
from tinycss2.color4 import Color as CssColor
from tinycss2.color4 import parse_color

# Keywords and functions that are valid CSS but don't give a concrete colour here
UNRESOLVED_KEYWORDS = {"inherit", "initial", "unset", "revert", "revert-layer", "currentcolor", "auto"}
UNRESOLVED_FUNCTIONS = {
    "var",
    "env",
    "attr",
    "calc",
    "min",
    "max",
    "clamp",
    "color-mix",
    "light-dark",
    "device-cmyk",
}


class UnresolvedColor(ValueError):
    """Valid CSS that doesn't resolve to a concrete colour"""


def _to_8_bit(x: float) -> int:
    return round(min(max(x, 0.0), 1.0) * 255)


def _significant(nodes: list[Node]) -> list[Node]:
    return [node for node in nodes if not isinstance(node, WhitespaceToken)]


def _is_unresolved(nodes: list[Node]) -> bool:
    """whether a function from UNRESOLVED_FUNCTIONS or the relative `from` syntax appears anywhere in the nodes"""
    for node in nodes:
        if isinstance(node, FunctionBlock):
            arguments = _significant(node.arguments)
            if node.lower_name in UNRESOLVED_FUNCTIONS or _is_unresolved(arguments):
                return True
            if arguments and isinstance(arguments[0], IdentToken) and arguments[0].lower_value == "from":
                return True
    return False


def _is_unresolved_value(val: str) -> bool:
    nodes = _significant(tinycss2.parse_component_value_list(val, skip_comments=True))
    first = nodes[0] if nodes else None
    if isinstance(first, IdentToken) and first.lower_value in UNRESOLVED_KEYWORDS:
        return True
    return _is_unresolved(nodes)


# __eq__ compares the 8-bit channels. No __hash__ to match:
# these are only ever compared, never used as a dict key or put in a set.
class Color:  # noqa: PLW1641
    def __init__(self, val: str):
        parsed = parse_color(val)
        if not isinstance(parsed, CssColor):
            raise UnresolvedColor if _is_unresolved_value(val) else ValueError
        try:
            red, green, blue, alpha = parsed.to("srgb")
        except NotImplementedError as err:  # tinycss2 only converts hsl and hwb to sRGB
            raise UnresolvedColor from err
        self.rgba = (_to_8_bit(red), _to_8_bit(green), _to_8_bit(blue), _to_8_bit(alpha))

    @property
    def alpha(self) -> float:
        return self.rgba[3] / 255

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return self.rgba == other.rgba
