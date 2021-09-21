from dodona.translator import Translator
from validators.html_validator import HtmlValidator
from lxml.html import fromstring, HtmlElement


class NotTheSame(Exception):
    def __init__(self, msg: str, line: int, trans: Translator):
        self.msg = msg
        self.line = line - 1  # 1 based to 0 based
        self.trans = trans

    def __repr__(self):
        return f"{self.msg} {self.trans.translate(Translator.Text.AT_LINE)} {self.line}"

    def __str__(self):
        return self.__repr__()


def compare(solution: str, submission: str, trans: Translator, **kwargs):
    """compare submission structure to the solution structure (html)
    possible kwargs:
    * attributes: (default: False) check whether attributes are exactly the same in solution and submission
    * minimal_attributes: (default: False) check whether at least the attributes in solution are supplied in the submission
    * contents: (default: False) check whether the contents of each tag in the solution are exactly the same as in the submission
    Raises a NotTheSame exception if the solution and the submission are not alike
    """
    # structure is always checked
    check_attributes = kwargs.get("attributes", False)
    check_minimal_attributes = kwargs.get("minimal_attributes", False)
    check_contents = kwargs.get("contents", False)
    html_validator = HtmlValidator(trans)
    html_validator.validate_content(submission)

    solution: HtmlElement = fromstring(solution)
    submission: HtmlElement = fromstring(submission)
    # start checking structure

    def attrs_a_contains_attrs_b(attrs_a, attrs_b, exact_match):
        # split dummy values from attrs_a
        dummies = set()
        exact = {}
        for a in attrs_a:
            if node_sol.attrib.get(a).strip() == "DUMMY":
                dummies.add(a)
            else:
                exact.update({a: node_sol.attrib.get(a).strip()})
        # check if all attrs in a are in b (if exact, all attrs from b must also be in a)
        for b in attrs_b:
            if b in exact and exact[b] == node_sub.attrib[b]:
                exact.pop(b)
            elif b in dummies:
                dummies.remove(b)
            elif exact_match:
                return False
        if dummies or exact:
            return False
        return True

    queue = ([(solution, submission)])
    while queue:
        node_sol, node_sub = queue.pop()
        # check name of the node
        if node_sol.tag != node_sub.tag:
            raise NotTheSame(trans.translate(Translator.Text.TAGS_DIFFER), node_sub.sourceline, trans)
        # check attributes if wanted
        if check_attributes:
            if not attrs_a_contains_attrs_b(node_sol.attrib, node_sub.attrib, True):
                raise NotTheSame(trans.translate(Translator.Text.ATTRIBUTES_DIFFER), node_sub.sourceline, trans)
        if check_minimal_attributes:
            if not attrs_a_contains_attrs_b(node_sol.attrib, node_sub.attrib, False):
                raise NotTheSame(trans.translate(Translator.Text.NOT_ALL_ATTRIBUTES_PRESENT), node_sub.sourceline, trans)
        # check content if wanted
        if check_contents:
            if node_sol.text.strip() != "DUMMY" and node_sol.text.strip() != node_sub.text.strip():
                raise NotTheSame(trans.translate(Translator.Text.CONTENTS_DIFFER), node_sub.sourceline, trans)
        # check children of the node
        if len(node_sol.getchildren()) != len(node_sub.getchildren()):
            raise NotTheSame(trans.translate(Translator.Text.AMOUNT_CHILDREN_DIFFER), node_sub.sourceline, trans)
        node_sol_children = node_sol.getchildren()
        node_sub_children = node_sub.getchildren()
        for i in range(len(node_sol.getchildren())):
            queue.append((node_sol_children[i], node_sub_children[i]))
