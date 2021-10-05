from dodona.translator import Translator
from lxml.html import fromstring, HtmlElement, HtmlComment

from validators.css_validator import CssValidator
from utils.html_navigation import compare_content


class NotTheSame(Exception):
    def __init__(self, msg: str, line: int, trans: Translator):
        self.msg = msg
        self.line = line - 1  # 1 based to 0 based
        self.trans = trans

    def __repr__(self):
        return f"{self.msg} {self.trans.translate(Translator.Text.AT_LINE)} {self.line + 1}"

    def __str__(self):
        return self.__repr__()

    def message_str(self):
        # Line number < 0 means no line number should be shown (eg. empty submission)
        # (#137)
        if self.line < 0:
            return self.msg

        return f"{self.msg} {self.trans.translate(Translator.Text.AT_LINE)} {self.line + 1}"

    def annotation_str(self):
        # Don't show line number in annotations (#137)
        return self.msg


def compare(solution: str, submission: str, trans: Translator, **kwargs):
    """compare submission structure to the solution structure (html)
    possible kwargs:
    * attributes: (default: False) check whether attributes are exactly the same in solution and submission
    * minimal_attributes: (default: False) check whether at least the attributes in solution are supplied in the submission
    * contents: (default: False) check whether the contents of each tag in the solution are exactly the same as in the submission
    * css: (default: True) if there are css rules defined in the solution, check if the submission can match these rules.
            We don't compare the css rules itself, but rather whether every element in the submission has at least the css-rules defined in the solution.
    Raises a NotTheSame exception if the solution and the submission are not alike

    the submission html should be valid html
    """
    if not submission.strip():
        raise NotTheSame(trans.translate(Translator.Text.EMPTY_SUBMISSION), 0, trans)

    # structure is always checked
    check_attributes = kwargs.get("attributes", False)
    check_minimal_attributes = kwargs.get("minimal_attributes", False)
    check_contents = kwargs.get("contents", False)
    check_css = kwargs.get("css", True)
    check_comments = kwargs.get("comments", False)

    sol_css = None
    sub_css = None
    if check_css:
        try:
            sol_css = CssValidator(solution)
            sub_css = CssValidator(submission)
            if not sol_css.rules:  # no rules in solution file
                check_css = False
        except Exception:
            check_css = False

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
        if check_comments and isinstance(node_sol, HtmlComment):
            if not isinstance(node_sub, HtmlComment):
                raise NotTheSame(trans.translate(Translator.Text.EXPECTED_COMMENT), node_sub.sourceline, trans)
            node_sol.text = node_sol.text.strip().lower() if node_sol.text is not None else ''
            node_sub.text = node_sub.text.strip().lower() if node_sub.text is not None else ''
            if node_sol.text != "dummy" and not compare_content(node_sol.text, node_sub.text):
                raise NotTheSame(trans.translate(Translator.Text.COMMENT_CORRECT_TEXT), node_sub.sourceline, trans)
            continue
        node_sol.tag = node_sol.tag.lower()
        node_sub.tag = node_sub.tag.lower()
        node_sol.text = node_sol.text.strip() if node_sol.text is not None else ''
        node_sub.text = node_sub.text.strip() if node_sub.text is not None else ''
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
            if node_sol.text != "DUMMY" and not compare_content(node_sol.text, node_sub.text):
                raise NotTheSame(trans.translate(Translator.Text.CONTENTS_DIFFER), node_sub.sourceline, trans)
        # check css
        if check_css:
            rs_sol = sol_css.rules.find_all(solution, node_sol)
            rs_sub = sub_css.rules.find_all(submission, node_sub)
            if rs_sol:
                for r_key in rs_sol:
                    if r_key not in rs_sub:
                        raise NotTheSame(trans.translate(Translator.Text.STYLES_DIFFER, tag=node_sub.tag), node_sub.sourceline, trans)
                    if rs_sol[r_key].value_str != rs_sub[r_key].value_str:
                        if not (rs_sol[r_key].is_color() and rs_sol[r_key].has_color(rs_sub[r_key].value_str)):
                            raise NotTheSame(trans.translate(Translator.Text.STYLES_DIFFER, tag=node_sub.tag), node_sub.sourceline, trans)
        # check whether the children of the nodes have the same amount of children
        node_sol_children = node_sol.getchildren()
        node_sub_children = node_sub.getchildren()
        if not check_comments:
            node_sol_children = [x for x in node_sol_children if isinstance(x, HtmlElement)]
            node_sub_children = [x for x in node_sub_children if isinstance(x, HtmlElement)]
        if len(node_sol_children) != len(node_sub_children):
            raise NotTheSame(trans.translate(Translator.Text.AMOUNT_CHILDREN_DIFFER), node_sub.sourceline, trans)
        # reverse children bc for some reason they are in bottom up order (and we want to review top down)
        queue += zip(reversed(node_sol_children), reversed(node_sub_children))

