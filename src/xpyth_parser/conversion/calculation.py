import ast
import operator


def add_node(i, l_values):

    # Take operator and expressions out of the list
    expr_right = l_values.pop(i + 1)
    op = l_values.pop(1)
    expr_left = l_values.pop(i - 1)

    # get the node
    node = ast.BinOp(expr_left, op, expr_right)

    # Add node to list/tree
    l_values.insert(i - 1, node)

    return l_values


def get_nodes(l_values):

    # First loop though the whole equation and look for add/sub operators
    for i, val in enumerate(l_values):
        # go though list of values, try to find operators in order of precedence.

        if  val in [operator.add, operator.sub]:
            # Create a node for these
            newlist = add_node(i=1, l_values=l_values)
            return get_nodes(newlist)

    # If add/sub operators have been handled, continue on with multiplication and dividing
    for i, val in enumerate(l_values):
        if  val in [operator.mul, operator.truediv]:
            newlist = add_node(i=1, l_values=l_values)
            return get_nodes(newlist)


def get_ast(v):
    l_values = list(v)

    # Loop though the equation and create a nested tree of BinOp objects
    get_nodes(l_values)

    # If the final list only has one value, return that value instead of a list.
    if len(l_values) == 1:
        l_values = l_values[0]

    return l_values
