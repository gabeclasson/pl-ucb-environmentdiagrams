class Frame():
    # I, Noemi, will refer to this as a FrameNode for the time being to remove ambiguity with FrameObjects for the time being. 
    is_global = False

    def __init__(self, name = None, bindings=None, parent=None, fobj=None):
        self.parent = parent
        self.children = set()
        if bindings is None:
            self.bindings = {}
        self.name = name
        # self's frame object
        self.fobj = fobj

    def bind(self, name, value):
        self.bindings[name] = value # Note: this will allow for duplicate entries. need to figure out a better way to do this. 
    
    def bind(self, name_value_dict):
        self.bindings = name_value_dict # Note: this will allow for duplicate entries. need to figure out a better way to do this. 
    
    def set_name(self, name):
        self.name = name
    
    def add_child(self, child):
        self.children.add(child)
    
    def __str__(self, level=0):
        ret = "\t"*level+repr(self.name)+"\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret

    def __repr__(self):
        return '<frame node representation>'