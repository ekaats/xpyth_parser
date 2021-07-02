class Parenthesized_Expression():

    def __init__(self, expr):
        self.expr = expr



def parenthesized_expression(expr):
    # print()
    # return Parenthesized_Expression(expr=v)
    expr_list = list(expr)
    return_value = tuple(expr)
    return (return_value)