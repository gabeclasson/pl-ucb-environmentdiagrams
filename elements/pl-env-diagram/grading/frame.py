class Frame():
    is_global = False

    def __init__(self, name = None, bindings=None, parent=None, children=None, fobj=None):
        self.parent = parent
        self.children = set()
        if bindings is None:
            self.bindings = {}
        self.name = name
        # self's frame object
        self.fobj = fobj

    def bind(self, name, value):
        self.bindings[name] = value  
    
    def bind(self, name_value_dict):
        self.bindings = name_value_dict 
    
    def set_name(self, name):
        self.name = name
    
    def add_child(self, child):
        self.children.add(child)
    
    def __str__(self, level=0):
        ret = "\t"*level+repr(self.name)+"\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret
    
    def freeze(self):
        return FrozenFrame(bindings = frozenset(item for item in self.bindings.items()), children = frozenset(child.freeze() for child in self.children))

    def __repr__(self):
        return '<frame node representation>'

class FrozenFrame(Frame):

    def __hash__(self) -> int:
        return hash(self.bindings) + hash(self.children)
    
    def __eq__(self, other): 
        if not isinstance(other, Frame):
            # don't attempt to compare against unrelated types
            return False

        return self.__hash__ == other.__hash__