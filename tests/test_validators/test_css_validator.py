import unittest
from bs4 import BeautifulSoup

from validators.css_validator import CssValidator

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

<div class="test_element_with_attribute_contains_substring_value" test_element_with_attribute_contains_substring_value="aavalueaa"></div>

<div class="test_most_precise"></div>

<div class="test_order"></div>

<div class="test_important"></div>

</body>
</html>
"""


class TestHtmlValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bs: BeautifulSoup = BeautifulSoup(html, "html.parser")
        self.validator = CssValidator(html)

    def test_green_tests(self):
        test_classes = [
            "test_classname",
            "test_multiple_classname test_multiple_classname2",
            "test_class_descendant",
            "test_id",
            "test_select_all1", "test_select_all2", "test_select_all3",
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
            "test_important"
        ]

        # Change amount of times this is run to benchmark
        # the speed of the css parsing (timing below uses 125)
        num_tests = 1

        for _ in range(num_tests):
            for green_class in test_classes:
                sol_el = self.bs.find("div", attrs={"class": green_class})
                self.assertEqual("green", self.validator.find(sol_el, "color"), green_class)
        for _ in range(num_tests):
            for green_class in test_classes:
                sol_el = self.bs.find("div", attrs={"class": green_class})
                self.assertEqual("2px", self.validator.find(sol_el, "margin"), green_class)
