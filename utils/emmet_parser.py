import emmet
from bs4 import BeautifulSoup

from validators.checks import TestSuite, Element, all_of, fail, EmptyElement


def emmet_to_check(emmet_str: str, suite: TestSuite):
    parsed: emmet.Abbreviation = emmet.parse_markup_abbreviation(emmet_str)
    start: emmet.AbbreviationNode

    def make_params(node: emmet.AbbreviationNode):
        out = {}
        if node.attributes:
            out.update({attribute.name: " ".join(attribute.value) for attribute in node.attributes})
        if node.value:
            out.update({"text": " ".join(node.value)})
        return out

    def match_one(ls: [], node: emmet.AbbreviationNode):
        if len(ls) == 1:
            return ls[0], node
        elif node.repeat and node.repeat.value < len(ls):
            return ls[node.repeat.value], node
        else:
            return EmptyElement(), node

    def to_checks(ls: [emmet.AbbreviationNode]):
        el: Element
        abr: emmet.AbbreviationNode
        length = len(ls)
        while length > 0:
            if ls[0][1].children:
                el, abr = ls.pop(0)
                for node in abr.children:
                    node: emmet.AbbreviationNode
                    kwargs = make_params(node)
                    ls.append(match_one(el.get_children(node.name, direct=True, **kwargs), node))
                    length += 1
            length -= 1
        return all_of(*[x[0].exists() for x in ls])

    roots = []
    for root_child in parsed.children:
        root_child: emmet.AbbreviationNode
        params = make_params(root_child)
        roots.append(match_one(suite.all_elements(root_child.name, **params), root_child))

    checks = to_checks(roots)
    return checks


document = """
    <li class="item1"></li>
    <li class="item2"></li>
    <li class="item3"></li>
    <li class="item4"></li>
    <li class="item5"></li>
"""
suite = TestSuite("My test suite", document)
c = emmet_to_check("""li*5""", suite)
print("Running check... " + str(bool(c.callback(BeautifulSoup(document, "html.parser")))))
