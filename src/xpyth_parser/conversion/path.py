class Axis:
    def __init__(self, axis, step):

        self.axis = axis
        self.step = step

    def __repr__(self):
        return f"axis: {self.axis}, step:{self.step}"


def get_single_path_expr(v):

    if len(v) == 2:
        return Axis(axis=v[0], step=v[1])
    else:
        return v


class PathExpression:
    def __init__(self, steps):

        if isinstance(steps, list):
            self.steps = steps
        else:
            self.steps = [steps]

    def to_str(self):
        return_string = ""
        for step in self.steps:
            return_string += step.axis
            return_string += str(step.step)

        return return_string

    def resolve_path(self, lxml_etree):
        """
        Attempt to resolve path queries

        :param lxml_etree: LXML etree which the query is run against
        :return:
        """

        found_values = []
        if lxml_etree is not None:
            results = lxml_etree.xpath(self.to_str(), namespaces=lxml_etree.nsmap)
            for result in results:
                # Try to cast the value to int if applicable.
                try:
                    found_values.append(int(result.text))
                except:
                    found_values.append(result.text)
        else:
            return None

        return found_values


def get_path_expr(v):
    """

    :param v:
    :return:
    """
    steps = []
    if v[0] == "/" and len(v) == 1:
        # https://www.w3.org/TR/xpath-3/#parse-note-leading-lone-slash
        return "/"

    elif v[0] in ["/", "//"]:
        first_step = Axis(axis=v[0], step=v[1])
        if len(v) > 1:
            # todo EK: We probably only want predicates here?
            steps = list(v[2:])
        else:
            steps = []

        steps.insert(0, first_step)

        """
        Dealing with abbreviated steps
        https://www.w3.org/TR/xpath-3/#abbrev
        """
    elif v[0] == "@":
        # attribute::
        steps.append(Axis(axis="attribute::", step=v[1]))
    elif v[0] == "..":
        # parent::node()
        steps.append(Axis(axis="parent::node()", step=v[1]))

    else:
        # Can just be a RelativePathExpr, which can itself be a postfix expr
        # steps.append(v[0])

        # If we didn't find anything axis-like, we probably need to return all toks
        return v

    return PathExpression(steps=steps)
