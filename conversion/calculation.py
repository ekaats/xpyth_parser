



class Calculation:

    def __init__(self, operator, value_1, value_2):
        self.operator = operator
        self.value_1 = value_1
        self.value_2 = value_2


    def __repr__(self):
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



def get_comparison_operator(value):
    value_1 = value[0]
    operator = value[1]
    value_2 = value[2]

    return Calculation(operator=operator, value_1=value_1, value_2=value_2)