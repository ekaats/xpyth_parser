class Calculation:

    def __init__(self, operator, value_1, value_2):
        self.operator = operator

        self.value_1 = value_1
        self.value_2 = value_2


    def __str__(self):
        return f"Calc op='{self.operator}' v1='{self.value_1}' v2='{self.value_2}'"

    def __eq__(self, other):
        if not isinstance(other, Calculation):
            return NotImplemented
        return self.operator == other.operator and self.value_1 == other.value_1 and self.value_2 == other.value_2

    def ans(self):

        if self.operator == "+":
            return self.value_1 + self.value_2
        elif self.operator == "-":
            return self.value_1 - self.value_2
        elif self.operator == "/":
            return self.value_1 / self.value_2
        elif self.operator == "*":
            return self.value_1 * self.value_2



def get_comparison_operator(v):


    l_values = list(v)

    value_1 = v[0]
    operator = v[1]
    value_2 = v[2]

    return Calculation(operator=operator, value_1=value_1, value_2=value_2)
    # return (v)

# def get_arth(value):
#     p_opListOrParser = [
#
#     ]
#     parser = BaseArithmeticParser()
#     arth_expr = parser.parse(value)
#     arth_eval = parser.evaluate(value)
#
#     # arth_expr = p_ParseOrExpr.parseString(value)
#     # for i, elem in enumerate(arth_expr):
#     #     print(f"{i}: {elem}")
#     return arth_expr
#
#

# get_arth("(1 * 2 - (3 + 5)) * 2")