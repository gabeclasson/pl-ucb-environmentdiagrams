class Frame: 
    def __init__(self, name : str =None, bindings:dict=None, parent =None, children : iter = None):
        self.parent = parent
        self.name = name
        if children is None:
            self.children = []
        else: 
            self.children = []
        if bindings is None:
            self.bindings = {}
        else:
            self.bindings = bindings
        self.name = None

    def bind(self, name, val):
        self.bindings[name] = val; # Note that this does not check for duplicate bindings


def traverse(obj):
    objects = [obj]
    seen_ids = set([obj.id])

    def safe_add(x):
        if x.id in seen_ids:
            return
        if type(x) in (bool, str, int, float, type(None)):
            return
        objects.append(x)
        seen_ids.add(x.id)

    for y in objects:
        if type(y) == list or type(y) == tuple:
            for sub_obj in y:
                safe_add(sub_obj)
        elif type(y) == dict:
            for sub_obj in y.keys():
                safe_add(sub_obj)
            for sub_obj in y.values():
                safe_add(sub_obj)
        elif type(y) == Frame:
            for sub_obj in y.bindings.values():
                safe_add(sub_obj)

    
    helper(obj)
    return objects

def score(correct, test):
    """Returns correct_components, total_components"""
    correct, total = 0
    if type(correct) == list or type(correct) == tuple: 
        list_total = len(correct) + 1
        list_correct = 0
        if type(correct) == type(test):
            list_correct += 1
        for list in 
        for elem in 