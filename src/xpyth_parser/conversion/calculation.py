import ast
import operator

arth_ops = {
    '+' : ast.Add(),
    '-' : ast.Sub(),
    '*' : ast.Mult(),
    'div' : ast.Div(),
    'mod' : ast.Mod(),
}


def add_node(i, l_values):

    # Take operator and expressions out of the list

    expr_right = l_values.pop(i + 1)
    if isinstance(expr_right, int):
        expr_right = ast.Num(expr_right)

    op = l_values.pop(i)
    op = arth_ops[op]

    expr_left = l_values.pop(i - 1)
    if isinstance(expr_left, int):
        expr_left = ast.Num(expr_left)

    # get the node
    node = ast.BinOp(expr_left, op, expr_right)

    # Add node to list/tree
    l_values.insert(i - 1, ast.fix_missing_locations(node))
    # l_values.insert(i - 1, node)

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

# Not | UAdd | USub | Invert
unary_ops = {
        '+': ast.UAdd(),
        '-': ast.USub(),
        }

def get_unary_expr(v):
    """
    Unary Expressions are handled weirdly in the grammar as it can have zero or more operators.
    Right now we only give back a UnaryOp if there is one operator. Otherwise We'll not parse anything
    and let get_ast() handle it though AdditiveExpr.

    :param v:
    :return:
    """
    val_list = list(v)
    if len(val_list) > 1:

        # Only give back a unaryExpr if there is an actual operator being given
        op = unary_ops[val_list[0]]

        val = v[1]
        # val = ast.Num(list(v)[1])
        unary_op = ast.UnaryOp(op, val)
        return unary_op



    else:
        return v

def get_ast(v):
    # TODO: WRAP AST INTO OBJECT WITH FUNCTIONS TO COMPILE, EVAL, RESOLVE VARIABLES AND ADD EXPRESSION()
    l_values = list(v)

    # Loop though the equation and create a nested tree of BinOp objects
    get_nodes(l_values)

    # If the final list only has one value, return that value instead of a list.
    # if len(l_values) == 1 and isinstance(l_values[0], ast.BinOp):
    if len(l_values) == 1:
        # We expect there to be only one value, which should be a BinOp.
        l_values = l_values[0]
        return l_values


    elif isinstance(l_values[0], ast.Expression):
        # If the function gets called recursively, it could happen we already created the full expression.
        # In that case, just send it though.
        return l_values[0]

    else:
        print("Got more values than expected")
