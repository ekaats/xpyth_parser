import ast

from .conversion.functions.generic import Function
from .conversion.qname import Parameter
from .grammar.expressions import t_XPath

class ResolveQnames(ast.NodeTransformer):

    def visit_QName(self, node):
        print("")



class XPath:

    def __init__(self, xpath_expr, parseAll=True, variable_map=None):
        self.XPath = t_XPath.parseString(xpath_expr, parseAll=parseAll)

        self.variable_map = variable_map if variable_map else []

        # If variable map is given, automatically resolve QNames
        if variable_map:
            self.resolve_qnames()

    def get_expression(self, expr_nr=0):
        """
        Returns XPath expression wrapped into an ast.Expression.
        An XPath expression should resolve into one part,
        but sometimes this is not the case. expr_nr be used to select a different part of the expression.

        :arg: expr_nr: int
        :return: ast.Expression
        """
        return ast.Expression(self.XPath[expr_nr])

    def resolve_qnames(self):
        """
        Loops though parsed results and resolves qnames using the variable_map

        :return:
        """
        # TODO: Pickle grammar for reuse with different sets of variables
        def resolve_fn(fn):
            fn.cast_parameters(paramlist=self.variable_map)

            # Then get the value by running the function
            value = fn.run()

            # Put the output value of the function into the AST as a number
            return ast.Num(value)

        for parsed_expr in self.XPath:

            for node in ast.walk(parsed_expr):
                if hasattr(node, "comparators"):

                    '''Go through comparators and replace these with AST nodes based on the variable map'''
                    for i, comparator in enumerate(node.comparators):
                        if isinstance(comparator, Parameter):
                            # Recast the parameter based on information from the variable_map
                            comparator = comparator.get_ast_node(self.variable_map)
                            node.comparators[i] = comparator


                if hasattr(node, "operand"):

                    # First cast parameters based on variable map
                    if isinstance(node.operand, Function):
                        # Run the function and add the outcome as a value to the operand
                        node.operand = resolve_fn(node.operand)


                if hasattr(node, "left"):
                    if isinstance(node.left, Function):
                        node.left = resolve_fn(node.left)


                if hasattr(node, "right"):
                    if isinstance(node.right, Function):
                        node.right = resolve_fn(node.right)


    def eval_expression(self):
        """
        :return: Result of XPath expression
        """
        fixed = ast.fix_missing_locations(self.get_expression())
        compiled_expr = compile(fixed, "", "eval")
        evaluated_expr = eval(compiled_expr)
        return evaluated_expr
