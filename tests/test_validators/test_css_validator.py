import unittest
from typing import TYPE_CHECKING, cast

from bs4 import BeautifulSoup

from utils.color_converter import Color
from validators.css_validator import CssValidator

if TYPE_CHECKING:
    from bs4.element import Tag

html = """<!DOCTYPE html>
<html lang="en">
<head>
    <style>
        .test_important {color:green!important;margin:2px!important;}
.test_important {color:red;margin:3px}
* {color:red;margin:3px}
.test_order {color:red;margin:3px}

 .test_classname,
 .test_multiple_classname.test_multiple_classname2,
 .test_class_descendant2 .test_class_descendant,
  #test_id,
  .test_select_all *,
  .test_element div,
  div.test_element_with_classname,
  .test_element_comma_element,
  .test_element_space_element2 div div,
  .test_element_gt_element_ div>div,
  .test_element_plus_element_ div+div,
  .test_element_tilde_element_ div~div,
  [test_attribute],
  [test_attribute_equals_value=value],
  [test_attribute_contains_value~=value],
  [test_attribute_equals_or_startswith_value_1|=value],
  div[test_element_with_attribute_startswith_value^=value],
  div[test_element_with_attribute_endswith_value$=value],
  div[test_element_with_attribute_contains_substring_value*=value],
  .test_most_precise,
  .test_order
  {color: green;margin:2px;}
  .test_color_1 {color:#008000;margin:2px}

</style>
</head>
<body>

<div class="test_classname"></div>

<div class="test_multiple_classname test_multiple_classname2"></div>

<div class="test_class_descendant2"><div class="test_class_descendant"></div></div>

<div class="test_id" id="test_id"></div>

<div class="test_select_all">
    <div class="test_select_all1"></div>
    <div class="test_select_all2">
        <div class="test_select_all3"></div>
    </div>
</div>

<div class="test_element">
    <div class="test_element_div"></div>
</div>

<div class="test_element_with_classname"></div>

<div class="test_element_comma_element"></div>

<div class="test_element_space_element2">
    <div>
        <div class="test_element_space_element"></div>
    </div>
</div>

<div class="test_element_gt_element_">
    <div>
        <div class="test_element_gt_element"></div>
    </div>
</div>

<div class="test_element_plus_element_">
    <div></div>
    <div class="test_element_plus_element"></div>
</div>

<div class="test_element_tilde_element_">
    <div></div>
    <div class="test_element_tilde_element"></div>
</div>

<div class="test_attribute" test_attribute=""></div>

<div class="test_attribute_equals_value" test_attribute_equals_value="value"></div>

<div class="test_attribute_contains_value" test_attribute_contains_value="a value aa"></div>


<div class="test_attribute_equals_or_startswith_value_1" test_attribute_equals_or_startswith_value_1="value"></div>
<div class="test_attribute_equals_or_startswith_value_2" test_attribute_equals_or_startswith_value_1="value-aa"></div>

<div class="test_element_with_attribute_startswith_value" test_element_with_attribute_startswith_value="valueaa"></div>

<div class="test_element_with_attribute_endswith_value" test_element_with_attribute_endswith_value="aavalue"></div>

<div class="test_element_with_attribute_contains_substring_value"
     test_element_with_attribute_contains_substring_value="aavalueaa"></div>

<div class="test_most_precise"></div>

<div class="test_order"></div>

<div class="test_important"></div>

<div class="test_color_1"></div>

</body>
</html>
"""


class TestCssValidator(unittest.TestCase):
    def test_empty_style_tag(self):
        """An empty <style></style> has no CSS, which is not the same as being unparseable"""
        # style.text is None here, which used to reach Rules() and raise a TypeError that
        # TestSuite.__post_init__ doesn't catch, so the whole judge run fell over
        validator = CssValidator("<html><head><style></style></head><body><p>x</p></body></html>")
        self.assertEqual(validator.rules.rules, [])
        self.assertFalse(validator)

    def test_missing_style_tag(self):
        """A document with no <style> at all behaves the same way"""
        validator = CssValidator("<html><head></head><body><p>x</p></body></html>")
        self.assertEqual(validator.rules.rules, [])
        self.assertFalse(validator)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bs: BeautifulSoup = BeautifulSoup(html, "html.parser")
        self.validator = CssValidator(html)

    def test_selector(self):
        cssval = CssValidator("""<html><head>
        <style>
        #yellow:hover {
            background-color: rgb(255, 210, 0);
        }
        </style>
        </head></html>""")
        r = cssval.rules.rules[0]
        self.assertEqual(cssval.find_by_css_selector("#yellow:hover", "background-color"), r)

    def test_pseudo(self):
        x = """
        <html><head><style>
        div { color:red; }
        div:hover { color:green; }
        </style></head>
        <body>
        <div></div>
        </body></html>
        """
        cssval = CssValidator(x)
        bs: BeautifulSoup = BeautifulSoup(x, "html.parser")
        tag = cast("Tag", bs.find("div"))

        plain = cssval.find(tag, "color")
        hover = cssval.find(tag, "color", "hover")

        assert plain is not None
        assert hover is not None

        self.assertEqual(str(plain.color), "red")
        self.assertEqual(str(hover.color), "green")

    def test_green_tests(self):
        test_classes = [
            "test_classname",
            "test_multiple_classname test_multiple_classname2",
            "test_class_descendant",
            "test_id",
            "test_select_all1",
            "test_select_all2",
            "test_select_all3",
            "test_element_div",
            "test_element_with_classname",
            "test_element_comma_element",  # this is already checked implicitly
            "test_element_space_element",
            "test_element_gt_element",
            "test_element_plus_element",
            "test_element_tilde_element",
            "test_attribute",
            "test_attribute_equals_value",
            "test_attribute_contains_value",
            "test_attribute_equals_or_startswith_value_1",
            "test_attribute_equals_or_startswith_value_2",
            "test_element_with_attribute_startswith_value",
            "test_element_with_attribute_endswith_value",
            "test_element_with_attribute_contains_substring_value",
            "test_most_precise",  # this is already checked implicitly hence everything is color: red
            "test_order",
            "test_important",
            "test_color_1",
        ]

        # Change amount of times this is run to benchmark
        # the speed of the css parsing (timing below uses 125)
        num_tests = 1

        for _ in range(num_tests):
            for green_class in test_classes:
                sol_el = cast("Tag", self.bs.find("div", attrs={"class": green_class}))
                color = self.validator.find(sol_el, "color")

                assert color is not None
                self.assertEqual(Color("green"), color.color, green_class)
        for _ in range(num_tests):
            for green_class in test_classes:
                sol_el = cast("Tag", self.bs.find("div", attrs={"class": green_class}))
                margin = self.validator.find(sol_el, "margin")

                assert margin is not None
                self.assertEqual("2px", margin.value_str, green_class)
