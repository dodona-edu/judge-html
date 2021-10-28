"""Provide RGB color constants and a colors dictionary with
elements formatted: colors[colorname] = CONSTANT"""
from collections import namedtuple, OrderedDict
from typing import Optional, Tuple

"""
from util.color_converter import colors, RGB

>>> colors['aliceblue'].hex_format()
#F0F8FF

"""

name_hex = {
    "aliceblue": "#f0f8ff",
    "antiquewhite": "#faebd7",
    "aqua": "#00ffff",
    "aquamarine": "#7fffd4",
    "azure": "#f0ffff",
    "beige": "#f5f5dc",
    "bisque": "#ffe4c4",
    "black": "#000000",
    "blanchedalmond": "#ffebcd",
    "blue": "#0000ff",
    "blueviolet": "#8a2be2",
    "brown": "#a52a2a",
    "burlywood": "#deb887",
    "cadetblue": "#5f9ea0",
    "chartreuse": "#7fff00",
    "chocolate": "#d2691e",
    "coral": "#ff7f50",
    "cornflowerblue": "#6495ed",
    "cornsilk": "#fff8dc",
    "crimson": "#dc143c",
    "cyan": "#00ffff",
    "darkblue": "#00008b",
    "darkcyan": "#008b8b",
    "darkgoldenrod": "#b8860b",
    "darkgray": "#a9a9a9",
    "darkgreen": "#006400",
    "darkgrey": "#a9a9a9",
    "darkkhaki": "#bdb76b",
    "darkmagenta": "#8b008b",
    "darkolivegreen": "#556b2f",
    "darkorange": "#ff8c00",
    "darkorchid": "#9932cc",
    "darkred": "#8b0000",
    "darksalmon": "#e9967a",
    "darkseagreen": "#8fbc8f",
    "darkslateblue": "#483d8b",
    "darkslategray": "#2f4f4f",
    "darkslategrey": "#2f4f4f",
    "darkturquoise": "#00ced1",
    "darkviolet": "#9400d3",
    "deeppink": "#ff1493",
    "deepskyblue": "#00bfff",
    "dimgray": "#696969",
    "dimgrey": "#696969",
    "dodgerblue": "#1e90ff",
    "firebrick": "#b22222",
    "floralwhite": "#fffaf0",
    "forestgreen": "#228b22",
    "fuchsia": "#ff00ff",
    "gainsboro": "#dcdcdc",
    "ghostwhite": "#f8f8ff",
    "goldenrod": "#daa520",
    "gold": "#ffd700",
    "gray": "#808080",
    "green": "#008000",
    "greenyellow": "#adff2f",
    "grey": "#808080",
    "honeydew": "#f0fff0",
    "hotpink": "#ff69b4",
    "indianred": "#cd5c5c",
    "indigo": "#4b0082",
    "ivory": "#fffff0",
    "khaki": "#f0e68c",
    "lavenderblush": "#fff0f5",
    "lavender": "#e6e6fa",
    "lawngreen": "#7cfc00",
    "lemonchiffon": "#fffacd",
    "lightblue": "#add8e6",
    "lightcoral": "#f08080",
    "lightcyan": "#e0ffff",
    "lightgoldenrodyellow": "#fafad2",
    "lightgray": "#d3d3d3",
    "lightgreen": "#90ee90",
    "lightgrey": "#d3d3d3",
    "lightpink": "#ffb6c1",
    "lightsalmon": "#ffa07a",
    "lightseagreen": "#20b2aa",
    "lightskyblue": "#87cefa",
    "lightslategray": "#778899",
    "lightslategrey": "#778899",
    "lightsteelblue": "#b0c4de",
    "lightyellow": "#ffffe0",
    "lime": "#00ff00",
    "limegreen": "#32cd32",
    "linen": "#faf0e6",
    "magenta": "#ff00ff",
    "maroon": "#800000",
    "mediumaquamarine": "#66cdaa",
    "mediumblue": "#0000cd",
    "mediumorchid": "#ba55d3",
    "mediumpurple": "#9370db",
    "mediumseagreen": "#3cb371",
    "mediumslateblue": "#7b68ee",
    "mediumspringgreen": "#00fa9a",
    "mediumturquoise": "#48d1cc",
    "mediumvioletred": "#c71585",
    "midnightblue": "#191970",
    "mintcream": "#f5fffa",
    "mistyrose": "#ffe4e1",
    "moccasin": "#ffe4b5",
    "navajowhite": "#ffdead",
    "navy": "#000080",
    "oldlace": "#fdf5e6",
    "olive": "#808000",
    "olivedrab": "#6b8e23",
    "orange": "#ffa500",
    "orangered": "#ff4500",
    "orchid": "#da70d6",
    "palegoldenrod": "#eee8aa",
    "palegreen": "#98fb98",
    "paleturquoise": "#afeeee",
    "palevioletred": "#db7093",
    "papayawhip": "#ffefd5",
    "peachpuff": "#ffdab9",
    "peru": "#cd853f",
    "pink": "#ffc0cb",
    "plum": "#dda0dd",
    "powderblue": "#b0e0e6",
    "purple": "#800080",
    "rebeccapurple": "#663399",
    "red": "#ff0000",
    "rosybrown": "#bc8f8f",
    "royalblue": "#4169e1",
    "saddlebrown": "#8b4513",
    "salmon": "#fa8072",
    "sandybrown": "#f4a460",
    "seagreen": "#2e8b57",
    "seashell": "#fff5ee",
    "sienna": "#a0522d",
    "silver": "#c0c0c0",
    "skyblue": "#87ceeb",
    "slateblue": "#6a5acd",
    "slategray": "#708090",
    "slategrey": "#708090",
    "snow": "#fffafa",
    "springgreen": "#00ff7f",
    "steelblue": "#4682b4",
    "tan": "#d2b48c",
    "teal": "#008080",
    "thistle": "#d8bfd8",
    "tomato": "#ff6347",
    "turquoise": "#40e0d0",
    "violet": "#ee82ee",
    "wheat": "#f5deb3",
    "white": "#ffffff",
    "whitesmoke": "#f5f5f5",
    "yellow": "#ffff00",
    "yellowgreen": "#9acd32"
}

name_rgb = {
    "aliceblue": "240, 248, 255",
    "antiquewhite": "250, 235, 215",
    "aqua": "0, 255, 255",
    "aquamarine": "127, 255, 212",
    "azure": "240, 255, 255",
    "beige": "245, 245, 220",
    "bisque": "255, 228, 196",
    "black": "0, 0, 0",
    "blanchedalmond": "255, 235, 205",
    "blue": "0, 0, 255",
    "blueviolet": "138, 43, 226",
    "brown": "165, 42, 42",
    "burlywood": "222, 184, 135",
    "cadetblue": "95, 158, 160",
    "chartreuse": "127, 255, 0",
    "chocolate": "210, 105, 30",
    "coral": "255, 127, 80",
    "cornflowerblue": "100, 149, 237",
    "cornsilk": "255, 248, 220",
    "crimson": "220, 20, 60",
    "cyan": "0, 255, 255",
    "darkblue": "0, 0, 139",
    "darkcyan": "0, 139, 139",
    "darkgoldenrod": "184, 134, 11",
    "darkgray": "169, 169, 169",
    "darkgreen": "0, 100, 0",
    "darkgrey": "169, 169, 169",
    "darkkhaki": "189, 183, 107",
    "darkmagenta": "139, 0, 139",
    "darkolivegreen": "85, 107, 47",
    "darkorange": "255, 140, 0",
    "darkorchid": "153, 50, 204",
    "darkred": "139, 0, 0",
    "darksalmon": "233, 150, 122",
    "darkseagreen": "143, 188, 143",
    "darkslateblue": "72, 61, 139",
    "darkslategray": "47, 79, 79",
    "darkslategrey": "47, 79, 79",
    "darkturquoise": "0, 206, 209",
    "darkviolet": "148, 0, 211",
    "deeppink": "255, 20, 147",
    "deepskyblue": "0, 191, 255",
    "dimgray": "105, 105, 105",
    "dimgrey": "105, 105, 105",
    "dodgerblue": "30, 144, 255",
    "firebrick": "178, 34, 34",
    "floralwhite": "255, 250, 240",
    "forestgreen": "34, 139, 34",
    "fuchsia": "255, 0, 255",
    "gainsboro": "220, 220, 220",
    "ghostwhite": "248, 248, 255",
    "gold": "255, 215, 0",
    "goldenrod": "218, 165, 32",
    "gray": "128, 128, 128",
    "green": "0, 128, 0",
    "greenyellow": "173, 255, 47",
    "grey": "128, 128, 128",
    "honeydew": "240, 255, 240",
    "hotpink": "255, 105, 180",
    "indianred": "205, 92, 92",
    "indigo": "75, 0, 130",
    "ivory": "255, 255, 240",
    "khaki": "240, 230, 140",
    "lavender": "230, 230, 250",
    "lavenderblush": "255, 240, 245",
    "lawngreen": "124, 252, 0",
    "lemonchiffon": "255, 250, 205",
    "lightblue": "173, 216, 230",
    "lightcoral": "240, 128, 128",
    "lightcyan": "224, 255, 255",
    "lightgoldenrodyellow": "250, 250, 210",
    "lightgray": "211, 211, 211",
    "lightgreen": "144, 238, 144",
    "lightgrey": "211, 211, 211",
    "lightpink": "255, 182, 193",
    "lightsalmon": "255, 160, 122",
    "lightseagreen": "32, 178, 170",
    "lightskyblue": "135, 206, 250",
    "lightslategray": "119, 136, 153",
    "lightslategrey": "119, 136, 153",
    "lightsteelblue": "176, 196, 222",
    "lightyellow": "255, 255, 224",
    "lime": "0, 255, 0",
    "limegreen": "50, 205, 50",
    "linen": "250, 240, 230",
    "magenta": "255, 0, 255",
    "maroon": "128, 0, 0",
    "mediumaquamarine": "102, 205, 170",
    "mediumblue": "0, 0, 205",
    "mediumorchid": "186, 85, 211",
    "mediumpurple": "147, 112, 219",
    "mediumseagreen": "60, 179, 113",
    "mediumslateblue": "123, 104, 238",
    "mediumspringgreen": "0, 250, 154",
    "mediumturquoise": "72, 209, 204",
    "mediumvioletred": "199, 21, 133",
    "midnightblue": "25, 25, 112",
    "mintcream": "245, 255, 250",
    "mistyrose": "255, 228, 225",
    "moccasin": "255, 228, 181",
    "navajowhite": "255, 222, 173",
    "navy": "0, 0, 128",
    "oldlace": "253, 245, 230",
    "olive": "128, 128, 0",
    "olivedrab": "107, 142, 35",
    "orange": "255, 165, 0",
    "orangered": "255, 69, 0",
    "orchid": "218, 112, 214",
    "palegoldenrod": "238, 232, 170",
    "palegreen": "152, 251, 152",
    "paleturquoise": "175, 238, 238",
    "palevioletred": "219, 112, 147",
    "papayawhip": "255, 239, 213",
    "peachpuff": "255, 218, 185",
    "peru": "205, 133, 63",
    "pink": "255, 192, 203",
    "plum": "221, 160, 221",
    "powderblue": "176, 224, 230",
    "purple": "128, 0, 128",
    "red": "255, 0, 0",
    "rosybrown": "188, 143, 143",
    "royalblue": "65, 105, 225",
    "saddlebrown": "139, 69, 19",
    "salmon": "250, 128, 114",
    "sandybrown": "244, 164, 96",
    "seagreen": "46, 139, 87",
    "seashell": "255, 245, 238",
    "sienna": "160, 82, 45",
    "silver": "192, 192, 192",
    "skyblue": "135, 206, 235",
    "slateblue": "106, 90, 205",
    "slategray": "112, 128, 144",
    "slategrey": "112, 128, 144",
    "snow": "255, 250, 250",
    "springgreen": "0, 255, 127",
    "steelblue": "70, 130, 180",
    "tan": "210, 180, 140",
    "teal": "0, 128, 128",
    "thistle": "216, 191, 216",
    "tomato": "255, 99, 71",
    "turquoise": "64, 224, 208",
    "violet": "238, 130, 238",
    "wheat": "245, 222, 179",
    "white": "255, 255, 255",
    "whitesmoke": "245, 245, 245",
    "yellow": "255, 255, 0",
    "yellowgreen": "154, 205, 50",
    "rebeccapurple": "102, 51, 153"
}

hex_name = {name_hex[k]: k for k in name_hex}

rgb_name = {name_rgb[k]: k for k in name_rgb}


def name_to_hex(name_str: Optional[str]) -> Optional[str]:
    if not name_str:
        return None
    name_str = name_str.lower().strip()
    return name_hex.get(name_str, None)


def name_to_rgb(name_str: Optional[str]) -> Optional[str]:
    if not name_str:
        return None
    name_str = name_str.lower().strip()
    if name_str in name_rgb:
        return f"rgb({name_rgb[name_str]})"
    return None


def name_to_rgba(name_str: Optional[str]) -> Optional[str]:
    if not name_str:
        return None
    name_str = name_str.lower().strip()
    if name_str == "transparent":
        return "rgba(0, 0, 0, 0)"
    if name_str in name_rgb:
        return f"rgba({name_rgb[name_str]}, 1)"
    return None


def hex_to_name(hex_str: Optional[str]) -> Optional[str]:
    if not hex_str:
        return None
    hex_str = hex_str.lower().strip()
    return hex_name.get(hex_str, None)


def rgb_to_name(rgb_str: Optional[str]) -> Optional[str]:
    if not rgb_str:
        return None
    rgb_str = ", ".join(rgb_str.lower().replace(" ", "").removeprefix("rgb(").removesuffix(")").split(","))
    return rgb_name.get(rgb_str, None)


def rgba_to_name(rgba_str: Optional[str]) -> Optional[str]:
    if not rgba_str:
        return None
    rgba = rgba_str.replace(" ", "").split(",")
    rgba[-1] = str(float(rgba[-1]))
    if ", ".join(rgba) == "0, 0, 0, 0.0":
        return "transparent"

    # Cut off transparency
    return rgb_name.get(", ".join(rgba[:-1]), None)


class Color:
    as_name: Optional[str]
    as_hex: Optional[str]
    as_rgb: Optional[str]
    as_rgba: Optional[str]

    def __init__(self, value_str):
        if value_str.startswith("#"):
            self._from_hex(value_str)
        elif value_str.startswith("rgba("):
            self._from_rgba(value_str)
        elif value_str.startswith("rgb("):
            self._from_rgb(value_str)
        else:
            self._from_name(value_str)

        # Remove spaces in rgb & rgba
        if self.as_rgb is not None:
            self.as_rgb = self.as_rgb.replace(" ", "")

        if self.as_rgba is not None:
            self.as_rgba = self.as_rgba.replace(" ", "")

            # Make alpha a float
            parts = self.as_rgba.removesuffix(")").split(",")
            parts[-1] = str(float(parts[-1]))
            self.as_rgba = (",".join(parts)) + ")"

    def __repr__(self):
        return f"<Color: {self.as_name}>"

    def __eq__(self, other):
        if not isinstance(other, Color):
            return False
        return self.values() == other.values()

    def values(self) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        return self.as_name, self.as_hex, self.as_rgb, self.as_rgba

    def _from_name(self, name: str):
        self.as_name = name
        self.as_hex = name_to_hex(name)
        self.as_rgb = name_to_rgb(name)
        self.as_rgba = name_to_rgba(name)

    def _from_hex(self, hex_str: str):
        self.as_name = hex_to_name(hex_str)
        self.as_hex = hex_str
        self.as_rgb = rgb_to_name(self.as_name)
        self.as_rgba = name_to_rgba(self.as_name)

    def _from_rgb(self, rgb_str: str):
        self.as_name = rgb_to_name(rgb_str)
        self.as_hex = name_to_hex(self.as_name)
        self.as_rgb = rgb_str
        self.as_rgba = name_to_rgba(self.as_name)

    def _from_rgba(self, rgba_str: str):
        # Split string into r, g, b, and a
        rgba_parts = rgba_str.lower().replace(" ", "").removeprefix("rgba(").removesuffix(")").split(",")

        # Cut off trailing 0's
        rgba_parts[-1] = str(float(rgba_parts[-1]))

        rgba_str = ", ".join(rgba_parts)

        self.as_name = rgba_to_name(rgba_str)
        self.as_hex = name_to_hex(self.as_name)
        self.as_rgb = name_to_rgb(self.as_name)
        self.as_rgba = rgba_str
