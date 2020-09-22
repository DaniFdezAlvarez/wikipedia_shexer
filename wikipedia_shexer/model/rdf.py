BNODE_ELEM_TYPE = "BNode"
IRI_ELEM_TYPE = "IRI"
DOT_ELEM_TYPE = "."
LITERAL_ELEM_TYPE = "LITERAL"


class Literal(object):

    def __init__(self, content, elem_type):
        self._content = content
        self._elem_type = elem_type

    def __str__(self):
        return self._content

    @property
    def elem_type(self):
        return self._elem_type


class Iri(object):

    def __init__(self, content):
        self._content = content

    def __str__(self):
        return self._content

    @property
    def elem_type(self):
        return IRI_ELEM_TYPE

    @property
    def iri(self):
        return self._content

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)


class Property(object):

    def __init__(self, content):
        self._content = content

    def __str__(self):
        return self._content

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def iri(self):
        return self._content


class BNode(object):

    def __init__(self, identifier):
        self._identifier = identifier

    def __str__(self):
        return self._identifier

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return str(self) == str(other)

    @property
    def elem_type(self):
        return BNODE_ELEM_TYPE
