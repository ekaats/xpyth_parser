# # todo: temporary flag for
# direct_parse = True


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
        print("")
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


def get_path_expr(v):
    if v[0] == "/" and len(v) == 1:
        # https://www.w3.org/TR/xpath-3/#parse-note-leading-lone-slash
        return "/"
    elif v[0] in ["/", "//"]:
        first_step = Axis(axis=v[0], step=v[1])
        if len(v) > 1:

            steps = list(v[2:])
        else:
            steps = []
        steps.insert(0, first_step)

        return PathExpression(steps=steps)
    else:

        return v
