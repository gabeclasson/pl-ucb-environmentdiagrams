def is_number_str(str):
    for char in str:
        if not('0' <= char <= '9'):
            return False
    return True

class Frame():
    is_global = False

    def __init__(self, bindings=None, name=None, parent=None, children = None, return_value=None):
        self.parent = parent
        self.name = name
        self.return_value = return_value
        if children is None:
            self.children = []
        else: 
            self.children = children
        if bindings is None:
            self.bindings = {}
        else:
            self.bindings = bindings

    @classmethod
    def unflatten_raw_data(cls, raw_data):
        parsed_response = {}
        
        for key, value in sorted(raw_data.items(), key=lambda x: x[0]):
            key_components = key.split("-")
            prev = None
            prev_key = None
            vanguard = parsed_response
            for component in key_components:
                if vanguard is None:
                    if is_number_str(component):
                        vanguard = []
                    else: 
                        vanguard = {}
                    if type(prev) == dict:
                        prev[prev_key] = vanguard
                    elif type(prev) == list:
                        vanguard['index'] = prev_key
                        prev.append(vanguard)
                
                prev = vanguard
                prev_key = component
                
                if type(vanguard) == dict and component in vanguard: 
                    vanguard = vanguard[component]
                elif type(vanguard) == list and vanguard and vanguard[-1]['index'] == component:
                    vanguard = vanguard[-1]
                else: 
                    vanguard = None
            
            if type(prev) == dict:
                prev[prev_key] = value
            elif type(prev) == list:
                prev.append(value)

        return parsed_response

    @classmethod
    def from_raw_data(cls, raw_data):
        internal_representations = {frame_data['index']: Frame() for frame_data in raw_data['frame']}
        for frame_data in raw_data["frame"]:
            frame = internal_representations[frame_data['index']]
            for var_data in frame_data["var"]:
                frame.bind(var_data['name'], var_data['val'])
            frame.name = frame_data["name"]
            if 'parent' in frame_data:
                frame.parent = internal_representations[frame_data['parent']]
                frame.parent.children.append(frame)
            if 'return' in frame_data:
                frame.return_value = frame['return']
        
        return internal_representations['0']

    def bind(self, name, val):
        self.bindings[name] = val; # Note that this does not check for duplicate bindings
    
    def freeze(self):
        return FrozenFrame(bindings = frozenset(item for item in self.bindings.items()), children = frozenset(child.freeze() for child in self.children))

    def __eq__(self, other):
        raise NotImplementedError

    def __repr__(self):
        return f"Frame(bindings={self.bindings}, name={self.name}, children={self.children})"
    
class FrozenFrame(Frame):

    def __hash__(self) -> int:
        return hash(self.bindings) + hash(self.children)
    
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.name == other.name and self.bindings == other.bindings and self.children == other.children