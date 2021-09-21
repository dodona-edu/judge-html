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
    # structure is always checked
    check_attributes = kwargs.get("attributes", False)
    check_minimal_attributes = kwargs.get("minimal_attributes", False)
    check_contents = kwargs.get("contents", False)
    html_validator = HtmlValidator(trans)
    html_validator.validate_content(submission)

    solution: HtmlElement = fromstring(solution)
    submission: HtmlElement = fromstring(submission)
    # start checking structure

    queue = ([(solution, submission)])
    while queue:
        node_sol, node_sub = queue.pop()
        # check name of the node
        if node_sol.tag != node_sub.tag:
            raise NotTheSame(trans.translate(Translator.Text.TAGS_DIFFER), node_sub.sourceline, trans)
        # check attributes if wanted
        if check_attributes:
            if node_sol.attrib != node_sub.attrib:
                raise NotTheSame(trans.translate(Translator.Text.ATTRIBUTES_DIFFER), node_sub.sourceline, trans)
        if check_minimal_attributes:
            if not set(node_sol.attrib).issubset(set(node_sub.attrib)):
                raise NotTheSame(trans.translate(Translator.Text.NOT_ALL_ATTRIBUTES_PRESENT), node_sub.sourceline, trans)
        # check content if wanted
        if check_contents:
            if node_sol.text != node_sub.text:
                raise NotTheSame(trans.translate(Translator.Text.CONTENTS_DIFFER), node_sub.sourceline, trans)
        # check children of the node
        if len(node_sol.getchildren()) != len(node_sub.getchildren()):
            raise NotTheSame(trans.translate(Translator.Text.AMOUNT_CHILDREN_DIFFER), node_sub.sourceline, trans)
        node_sol_children = node_sol.getchildren()
        node_sub_children = node_sub.getchildren()
        for i in range(len(node_sol.getchildren())):
            queue.append((node_sol_children[i], node_sub_children[i]))
