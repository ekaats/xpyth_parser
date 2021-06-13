# Parse XPATH 2.0 and 3.1 using Pyparsing
XPath (XML Path Language) is a query language for selecting nodes from an XML document.
In addition, XPath may be used to compute values (e.g., strings, numbers, or Boolean values) from the content of an XML document.
XPath was defined by the World Wide Web Consortium (W3C).

[Pyparsing](https://github.com/pyparsing/pyparsing) is a parsing module used to construct grammar in Python.
XPyth uses Pyparsing to parse XPath strings, and offers an additional abstraction layer.

## Status
This library is an attempt to create a parser which can be used both to query XML documents,
as well as calculation tasks.
The original plan was to support both options. However, XPath 2.0 and 3.1 is not widely used, so use cases are sparse.
Parsing XPath 3.1 on a grammar level should still be supported, but not all information may be available when using
the abstraction layer. Most importantly, there will be [XPath functions](https://www.w3.org/2005/xpath-functions/) missing.

### Alternatives
For most use cases, there will be (better) alternatives to this project. [LXML](https://lxml.de/) is Pythonic binding
for the C libraries libxml2 and libxslt. If only XPath 1.0 is needed, LXML will be a better solution.


## Goals
This project started out with a specific goal:
to parse [XBRL formula](https://specifications.xbrl.org/work-product-index-formula-formula-1.0.html) tests.
These tests are heavily reliant on [XBRL specific XPath 2.0 functions](https://specifications.xbrl.org/work-product-index-registries-functions-registry-1.0.html).
Because of this, the author of this library is focussing on correctly interpreting these functions.

# Examples

Parse a string using Pyparsing

    count = t_XPath.parseString("count(1,2,3)", parseAll=True)[0]

This returns a Python function which can be used elsewhere
The function contains the QName which identifies the function, as well as the arguments

   count -> Count(qname=QName(localname="count"), arguments=(1,2,3))

Functions can have a run() function which returns a value as described in the Xpath functions document.

    count.run() -> 3
