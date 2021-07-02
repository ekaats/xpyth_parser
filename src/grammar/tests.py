from pyparsing import (
    Optional,
    Word,
    Keyword, Literal,
)

from .literals import l_par_l, l_par_r, t_NCName, t_StringLiteral
from .qualified_names import t_TypeName, t_ElementName, t_AttributeName, t_QName, t_Wildcard
from ..conversion.tests import elementTest, schemaElementTest, documentTest, schemaAttributeTest, commentTest, textTest, \
    anyKindTest, processingInstructionTest

"""
TESTS
https://www.w3.org/TR/xpath20/#prod-xpath-KindTest
"""

t_ElementNameOrWildcard = t_ElementName | Literal("*")
t_ElementNameOrWildcard.setName("ElementNameOrWildcard")

t_ElementTest = (
    Keyword("element")
    + l_par_l
    + Optional(t_ElementNameOrWildcard + Optional("," + t_TypeName + Optional("?")))
    + l_par_r
)
t_ElementTest.setName("ElementTest")
t_ElementTest.setParseAction(elementTest)

t_ElementDeclaration = t_ElementName
t_ElementDeclaration.setName("ElementDeclaration")

t_SchemaElementTest = Word("schema-element") + l_par_l + t_ElementDeclaration + l_par_r
t_SchemaElementTest.setParseAction(schemaElementTest)
t_SchemaElementTest.setName("schema-element")

t_DocumentTest = (
    Word("document-node")
    + l_par_l
    + Optional(t_ElementTest | t_SchemaElementTest)
    + l_par_r
)
t_DocumentTest.setName("DocumentTest")
t_DocumentTest.setParseAction(documentTest)

t_AttribNameOrWildcard = t_AttributeName | "*"
t_AttribNameOrWildcard.setName("AttribNameOrWildcard")

t_AttributeTest = (
    Word("attribute")
    + l_par_l
    + Optional(t_AttribNameOrWildcard + Optional("," + t_TypeName))
    + l_par_r
)
t_AttributeTest.setName("AttributeTest")

t_AttributeDeclaration = t_AttributeName
t_AttributeDeclaration.setName("AttributeDeclaration")

t_SchemaAttributeTest = Word("schema-attribute") + l_par_l + t_AttributeDeclaration + l_par_r
t_SchemaAttributeTest.setParseAction(schemaAttributeTest)
t_SchemaAttributeTest.setName("SchemaAttributeTest")

t_CommentTest = Word("comment") + l_par_l + l_par_r
t_CommentTest.setParseAction(commentTest)
t_CommentTest.setName("comment")

t_TextTest = Word("text") + l_par_l + l_par_r
t_TextTest.setParseAction(textTest)
t_TextTest.setName("TextTest")

t_AnyKindTest = Word("node") + l_par_l + l_par_r
t_AnyKindTest.setParseAction(anyKindTest)
t_AnyKindTest.setName("AnyKindTest")

t_PITest = (
    Word("processing-instruction") + l_par_l + Optional(t_NCName | t_StringLiteral) + l_par_r
)
t_PITest.setParseAction(processingInstructionTest)
t_PITest.setName("Processing-InstructionTest")

t_KindTest = (
    t_ElementTest
    | t_AttributeTest
    | t_SchemaElementTest
    | t_SchemaAttributeTest
    | t_PITest
    | t_CommentTest
    | t_TextTest
    | t_AnyKindTest
    | t_DocumentTest
)
t_KindTest.setName("KindTest")

t_NameTest = t_QName | t_Wildcard
t_NameTest.setName("NameTest")

t_NodeTest = t_KindTest | t_NameTest
t_NodeTest.setName("NodeTest")

