import emmet
from validators.checks import TestSuite, Element, all_of, EmptyElement


def emmet_to_check(emmet_str: str, suite: TestSuite):
    parsed = emmet.parse_markup_abbreviation(emmet_str)

    def make_params(node):
        out = {}
        if node.attributes:
            out.update({attribute.name: " ".join(attribute.value) for attribute in node.attributes})
        if node.value:
            out.update({"text": " ".join(node.value)})
        return out

    def match_one(ls: [], node):
        if len(ls) == 1:
            return ls[0], node
        elif node.repeat:
            if node.repeat.value < len(ls):
                return ls[node.repeat.value], node
            else:
                return EmptyElement(), node
        elif ls:
            return ls[0], node
        else:
            return EmptyElement(), node

    def to_checks(ls: []):
        el: Element
        length = len(ls)
        while length > 0:
            if ls[0][1].children:
                el, abr = ls.pop(0)
                for node in abr.children:
                    kwargs = make_params(node)
                    ls.append(match_one(el.get_children(node.name, direct=True, **kwargs), node))
                    length += 1
            length -= 1
        return all_of(*[x[0].exists() for x in ls])

    roots = []
    for root_child in parsed.children:
        params = make_params(root_child)
        roots.append(match_one(suite.all_elements(root_child.name, **params), root_child))

    checks = to_checks(roots)
    return checks
