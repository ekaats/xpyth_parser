import operator

from src.xpyth_parser.conversion.functions.generic import Function
from src.xpyth_parser.conversion.qname import Parameter


arth_ops = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "div": operator.truediv,
    "mod": operator.mod,
}

class SyntaxTreeNodeMixin(object):

    @property
    def _children(self) -> list:
        """
        Returns list with child nodes.

        """
        raise NotImplementedError

    def process_children(self):
        raise NotImplementedError

class Operator:
    pass

    @property
    def operator(self):
        # self.op does not show up in debugger. This is a workaround to see which operator is present.
        return str(self.op)

    def answer(self):
        raise NotImplementedError

    def resolve(self, variable_map, lxml_etree):

        raise NotImplementedError


class UnaryOperator(SyntaxTreeNodeMixin, Operator):
    def __init__(self, operand, operator):
        self.operand = operand
        self.op = operator

    def resolve(self, variable_map, lxml_etree):
        """
        Resolve parameter, path expression and context item of children

        :param variable_map:
        :param lxml_etree:
        :return:
        """

        if isinstance(self.operand, Function):
            self.operand.resolve_paths(lxml_etree=lxml_etree)
            self.operand.cast_parameters(paramlist=variable_map)
        else:
            print("Operand of unary operator type not known")

    def answer(self):

        if isinstance(self.operand, int):
            # If the value is an int, we can just use this value
            operand = self.operand

        elif isinstance(self.operand, Operator):
            # If the value is an Operator, we need to get to calculate its value first
            operand = self.operand.answer()

        elif isinstance(self.operand, Function):
            # Get the value from the function
            operand = self.operand.run()

        else:

            # Is an XPath expression that needs to be resolved.
            operand = self.operand.resolve_expression()

        if self.op == "+":
            return +operand
        elif self.op == "-":
            return -operand
        else:
            raise ("Unknown unary operator")

    @property
    def _children(self):
        return [self.operand]

    def process_children(self):
        new_operand = yield self.operand
        if new_operand is not None:
            self.operand = new_operand




class BinaryOperator(SyntaxTreeNodeMixin, Operator):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    @property
    def _children(self) -> list:
        return [self.left, self.right]

    def process_children(self):
        new_left = yield self.left
        if new_left is not None:
            self.left = new_left

        new_right = yield self.right
        if new_right is not None:
            self.right = new_right


    def resolve(self, variable_map, lxml_etree):
        """
        Resolve parameter, path expression and context item of children

        :param variable_map:
        :param lxml_etree:
        :return:
        """
        if isinstance(self.left, Function):
            self.left.resolve_paths(lxml_etree=lxml_etree)
            self.left.cast_parameters(paramlist=variable_map)
        elif isinstance(self.left, int):
            pass
        else:
            print("Operand of unary operator type not known")

        if isinstance(self.right, Function):
            self.right.resolve_paths(lxml_etree=lxml_etree)
            self.right.cast_parameters(paramlist=variable_map)
        elif isinstance(self.right, int):
            pass
        else:
            print("right Operand of binary operator type not known")

    def answer(self):

        if isinstance(self.left, int) or isinstance(self.left, float):
            # If the value is an int, we can just use this value
            left = self.left

        elif isinstance(self.left, Operator):
            # If the value is an Operator, we need to get to calculate its value first
            left = self.left.answer()

        elif isinstance(self.left, Function):
            # Get the value from the function
            left = self.left.run()

        else:

            # Is an XPath expression that needs to be resolved.
            left = self.left.resolve_child()

        if isinstance(self.right, int)  or isinstance(self.right, float):
            right = self.right

        elif isinstance(self.right, Operator):
            # If the value is an Operator, we need to get to calculate its value first
            right = self.right.answer()

        elif isinstance(self.right, Function):
            # Get the value from the function
            right = self.right.run()

        else:
            # Is an XPath expression that needs to be resolved.
            right = self.right.resolve_child()

        return self.op(left, right)


def add_node(i, l_values):

    # Take operator and expressions out of the list

    expr_right = l_values.pop(i + 1)

    op = l_values.pop(i)
    op = arth_ops[op]

    expr_left = l_values.pop(i - 1)

    # get the node
    node = BinaryOperator(expr_left, op, expr_right)

    l_values.insert(i - 1, node)

    return l_values


def get_nodes(l_values):
    # First loop though the whole equation and look for multiplication/dividing/modulo operators

    for i, val in enumerate(l_values):
        if val in ["*", "div", "mod"]:
            # if  val in [operator.mul, operator.truediv]:
            newlist = add_node(i=i, l_values=l_values)
            return get_nodes(newlist)

    # If mul/div operators have been handled, continue on with adding and subtracting
    for i, val in enumerate(l_values):
        # go though list of values, try to find operators in order of precedence.
        if val in ["+", "-"]:
            # if  val in [operator.add, operator.sub]:
            # Create a node for these
            newlist = add_node(i=i, l_values=l_values)
            return get_nodes(newlist)


def get_unary_expr(v):

    if len(v) > 1 and v[0] in ["+", "-"]:

        unary_op = UnaryOperator(operator=v[0], operand=v[1])
        return unary_op

    else:
        return v


comp_expr = {
    "=": operator.is_,  # General comparison
    "eq": operator.eq,  # value comparison
    "!=": operator.is_not,
    "ne": operator.ne,
    "<": "<",
    "lt": operator.lt,
    "<=": "<=",
    "le": operator.le,
    ">": ">",
    "gt": operator.gt,
    ">=": ">=",
    "ge": operator.ge,
}


def resolve_comparator_loop(expr, variable_map, lxml_etree):
    if isinstance(expr, int):
        return expr
    elif isinstance(expr, float):
        return expr

    elif isinstance(expr, Function):
        # Run the function and add the outcome as a value to the operand
        # if variable_map is not None:
        # Cast parameters if variable map has been provided and is not None
        expr.cast_parameters(paramlist=variable_map)

        # if lxml_etree is not None:
        # Resolve paths if etree is given and is not None
        expr.resolve_paths(lxml_etree=lxml_etree)

    elif isinstance(expr, Operator):
        # Need to get the value of the operator
        expr.resolve(variable_map, lxml_etree)

    elif isinstance(expr, Parameter):
        # Parameters need to be writen back
        return expr.resolve_parameter(paramlist=variable_map)

    else:
        # Probably an XPath
        resolve_comparator_loop(
            expr=expr.expr,
            variable_map=variable_map,
            lxml_etree=lxml_etree,
        )

        # Return the expression so we do not have to deal with the XPath wrapper anymore
        return expr.expr


class Compare(SyntaxTreeNodeMixin):
    def __init__(self, left, ops, comparators):
        self.left = left

        if len(ops) != len(comparators):
            raise ValueError(
                f"Got {len(ops)} operators and {len(comparators)} comparators to compare"
            )
        self.ops = ops
        self.comparators = comparators

    @property
    def _children(self) -> list:
        return [self.left] + self.comparators

    def process_children(self):
        new_left = yield self.left
        if new_left is not None:
            self.left = new_left

        for i, comparator in enumerate(self.comparators):
            new_comparator = yield comparator
            if new_comparator is not None:
                self.comparators[i] = new_comparator

    def resolve(self, variable_map, lxml_etree):

        for i, child in enumerate(self.comparators):
            ans = resolve_comparator_loop(
                child,
                variable_map=variable_map,
                lxml_etree=lxml_etree,
            )
            if ans is not None:
                self.comparators[i] = ans

        # Do the same with the left operand
        ans_left = resolve_comparator_loop(
            self.left,
            variable_map=variable_map,
            lxml_etree=lxml_etree,
        )
        if ans_left is not None:
            self.left = ans_left

    def answer(self):
        """
        Gives the answer of the Operator. If the operator contains any nested functions,
        they will be resolved automatically.

        so if isinstance(self.left, Function), this child will first be ran.

        :return: Answer of operator
        """
        if isinstance(self.left, Function):
            left = self.left.run()

        elif isinstance(self.left, Operator):
            # Need to get the value of the operator
            left = self.left.answer()

        else:
            left = self.left

        for i, op in enumerate(self.ops):

            # Resolve function or operator if this is a nested function
            if isinstance(self.comparators[i], Function):
                self.comparators[i] = self.comparators[i].run()

            elif isinstance(self.comparators[i], Operator):
                self.comparators[i] = self.comparators[i].answer()

            if op(left, self.comparators[i]) is False:
                return False

        return True


def get_comparitive_expr(v):
    val_list = list(v)

    # Put all operators in one list
    py_ops = []
    for val in val_list:
        if val in comp_expr.keys():

            py_ops.append(comp_expr[val])

    # # Only add a comparative expression if a comparator symbol has been found
    if len(py_ops) > 0:

        py_left = val_list[0]
        # Everything that isn't the first item or an op is considered a comperator
        comps = [v for v in val_list[1:] if v not in comp_expr.keys()]
        py_comps = []
        for comp in comps:

            py_comps.append(comp)

        py_compare_expr = Compare(left=py_left, ops=py_ops, comparators=py_comps)

        return py_compare_expr
    else:
        return v


def get_additive_expr(v):

    l_values = list(v)

    # Loop though the equation and create a nested tree of BinOp objects
    get_nodes(l_values)

    # If the final list only has one value, return that value instead of a list.

    if len(l_values) == 1:

        # We expect there to be only one value, which should be a BinOp.
        l_values = l_values[0]
        return l_values

    elif isinstance(l_values[0], BinaryOperator):
        # If the function gets called recursively, it could happen we already created the full expression.
        # In that case, just send it though.
        return l_values[0]

    else:
        # Is not a comparative expression
        return v
