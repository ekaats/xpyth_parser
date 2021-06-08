

class Test:

    def __init__(self, test_type, test=None):

        self.test_type = test_type

        if test:
            self.test = test
        else:
            # No subtests
            self.test = None

    def __repr__(self):
        return f"{self.test_type} test"

    def __eq__(self, other):
        if not isinstance(other, Test):
            return NotImplemented
        return self.test_type == other.test_type and self.test == other.test


def documentTest(v):
    """
    Document tests can have an optional element or schema element test

    :param v:
    :return:
    """
    if len(v) > 1:
        # (Sub) test element has already been parsed py Pyparsing
        subtest = v[1]

    else:
        # No arguments given
        subtest = None

    return Test(test_type="document-node", test=subtest)

def elementTest(v):
    """
    An ElementTest is used to match an element node by its name and/or type annotation.
    https://www.w3.org/TR/xpath-31/#id-element-test

    (
        ElementNameOrWildcard
            ("," TypeName "?"? )?
     )?

    :param v:
    :return:
    """
    if len(v) > 1:
        test = v[1]
    else:
        test = None

    return Test(test_type="element", test=test)

def attributeTest(v):
    pass

def schemaElementTest(v):
    """
    schema element must have an Element declaration
    https://www.w3.org/TR/xpath-31/#prod-xpath31-SchemaElementTest

    :param v:
    :return:
    """

    test = v[1]

    return Test(test_type="schema-element", test=test)

def schemaAttributeTest(v):
    """
    https://www.w3.org/TR/xpath-31/#id-schema-attribute-test
    :param v:
    :return:
    """
    test = v[1]

    return Test(test_type="schema-attribute", test=test)

def processingInstructionTest(v):
    """
    Processing Instruction can have an NCName or StringLiteral as test

    :param v:
    :return:
    """
    if len(v) > 1:
        test = v[1]
    else:
        test = None

    return Test(test_type="processing-instruction", test=test)

def commentTest(v):
    return Test(test_type="comment")

def textTest(v):
    return Test(test_type="text")

def anyKindTest(v):
    return Test(test_type="node")