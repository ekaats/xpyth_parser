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

class QName:
    def __init__(self, localname, prefix=None, namespace=None):
        self.localname = localname
        self.prefix = prefix
        self.namespace = namespace

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

    def resolve_parameter(self, paramlist):
        if self.qname.__str__() in paramlist.keys():
            return paramlist[self.qname.__str__()]
        else:
            # Not sure how a parameter that cannot be resolved should be handled.
            # We can return None or raise an error instead.
            return None

    def __repr__(self):
        return self.qname.localname

    def __eq__(self, other):
        if not isinstance(other, Parameter):
            return NotImplemented
        return self.qname == other.qname

    def __hash__(self):
        return hash(self.__repr__())
