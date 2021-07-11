import ast

def qname_from_parse_results(a, string):
    """
    Return a Qname object

    :param a:
    :param string:
    :return:
    """
    if len(string) > 1:
        return QName(prefix=string[0], localname=string[1])
    else:
        return QName(localname=string[0])

def get_variable(v):
    if len(v) > 1:
        return Parameter(qname=v[0], type_declaration=v[1])
    else:
        return Parameter(qname=v[0])



class QName:

    def __init__(self, localname, prefix=None):
        self.localname = localname
        self.prefix = prefix

    def __repr__(self):
        if self.prefix:
            return f"{self.prefix}:{self.localname}"
        return self.localname

    def __eq__(self, other):
        if not isinstance(other, QName):
            return NotImplemented
        return self.localname == other.localname and self.prefix == other.prefix

    def __hash__(self):
        return hash(self.__repr__())

class Parameter:

    def __init__(self, qname, type_declaration=None):
        self.qname = qname
        self.type_declaration = type_declaration

    def get_ast_node(self, paramlist):

        value = paramlist[self.qname.__str__()]
        if isinstance(value, int):
            return ast.Num(value)
        elif isinstance(value, list):
            val_list = [ast.Num(v) for v in value]
            return ast.List(val_list)
        else:
            print("Variable map object type not understood")

    def resolve_parameter(self, paramlist):
        return paramlist[self.qname.__str__()]

    def __repr__(self):
        return self.qname.localname

    def __eq__(self, other):
        if not isinstance(other, Parameter):
            return NotImplemented
        return self.qname == other.qname

    def __hash__(self):
        return hash(self.__repr__())