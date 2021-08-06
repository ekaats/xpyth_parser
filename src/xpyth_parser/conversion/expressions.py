
class IfExpression:

    def __init__(self, test_expr, then_expr, else_expr):

        self.test_expr = test_expr
        self.then_expr = then_expr
        self.else_expr = else_expr

    def resolve_expression(self):

        pass

def get_if_expression(v):

    parsed_expr = IfExpression(test_expr=v[0], then_expr=v[1], else_expr=v[2])
    return parsed_expr
