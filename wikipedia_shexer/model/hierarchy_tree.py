
class HNode(object):

    def __init__(self, label):
        self._label = label

    def __str__(self):
        return self._label

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self == other


class HClass(HNode):

    def __init__(self, label, superclass=None):
        super().__init__(label)
        self._superclass = superclass

    def set_superclass(self, superclass):
        self._superclass = superclass

    def add_child(self, subclass):
        subclass.set_superclass(self)

    @property
    def superclass(self):
        return self._superclass


class HInstance(HNode):

    def __init__(self, label, types=None):
        super().__init__(label)
        self._types = set() if types is None else types

    def add_type(self, a_class):
        self._types.add(a_class)

    @property
    def types(self):
        # This should return a copy, but life is not a safe place
        return self._types


OWL_THING = HClass("http://www.w3.org/2002/07/owl#Thing")


class HTree(object):

    def __init__(self):
        self._root = OWL_THING  # HNode
        self._node_index = {}

    def add_class_relation(self, parent, child):
        h_parent = self._get_class_from_index(class_label=parent)
        h_child = self._get_class_from_index(class_label=child)

        h_parent.add_child(h_child)


    def is_node_available(self, node):
        return node in self._node_index

    def is_class_descendent(self, superclass, subclass):
        tmp_super = subclass.superclass
        while tmp_super is not None:
            if tmp_super == superclass:
                return True
            tmp_super = tmp_super.superclass
        return False

    def is_instance_descendent(self, superclass, instance):
        for a_type in instance.types:
            if self.is_class_descendent(superclass=superclass,
                                        subclass=a_type):
                return True
        return False

    def add_type(self, instance, a_class):
        h_type = self._get_class_from_index(class_label=a_class)
        h_instance = self._get_instance_from_index(instance_label=instance)

        instance.add_type(a_class)

    def _get_class_from_index(self, class_label):
        if class_label not in self._node_index:
            self._node_index[class_label] = HTree._create_class(class_label)
        return self._node_index[class_label]

    def _get_instance_from_index(self, instance_label):
        if instance_label not in self._node_index:
            self._node_index[instance_label] = HTree._create_instance(instance_label)
        return self._node_index[instance_label]

    @staticmethod
    def _create_class(class_label):
        return HClass(label=class_label, superclass=OWL_THING)

    @staticmethod
    def _create_instance(instance_label):
        return HInstance(label=instance_label)

