
def from_parse_results(a, string):
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