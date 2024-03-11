def is_number_str(str):
    for char in str:
        if not('0' <= char <= '9'):
            return False
    return True

def sanitize_frame_index(index):
    if not index:
        return None
    index = index.lower().strip()
    if index[:6] == "frame-":
        index = index[6:]
    if index[:2] == 'f-':
        index = index[2:]
    if index[0] == 'g':
        index = '0'
    return index

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
    def unflatten_raw_data(cls, raw_data, special_keys=()):
        """
        Special keys means you stop processing the tree at that point.
        >>> raw_data = {'frame-0-var-0-name': 'x', 'frame-0-var-0-val': '5', 'frame-0-var-NaN-name': 'y', 'frame-0-var-NaN-val': '17', 'frame-1-name': 'g', 'frame-1-parent': 'Global', 'frame-1-var-0-name': 'z', 'frame-1-var-0-val': '"hi"', 'frame-1-return-val': '3'}
        >>> Frame.unflatten_raw_data(raw_data)
        {'frame': [{'index': '0', 'var': [{'index': '0', 'name': 'x', 'val': '5'}, {'index': '2', 'name': 'y', 'val': '17'}]}, {'index': '1', 'name': 'g', 'parent': 'Global', 'return': {'val': '3'}, 'var': [{'index': '0', 'name': 'z', 'val': '"hi"'}]}]}
        """
        parsed_response = {}
        
        for key, value in sorted(raw_data.items(), key=lambda x: x[0]):
            key_components = key.split("-")
            prev = None
            prev_key = None
            grand_prev_key = None
            vanguard = parsed_response
            for i, component in enumerate(key_components):
                if vanguard is None:
                    if is_number_str(component):
                        vanguard = []
                    else: 
                        vanguard = {}
                    if type(prev) == dict:
                        prev[prev_key] = vanguard
                    elif type(prev) == list:
                        vanguard[grand_prev_key + 'Index'] = prev_key
                        prev.append(vanguard)

                prev = vanguard
                grand_prev_key = prev_key
                prev_key = component
                
                if type(vanguard) == dict and component in vanguard: 
                    vanguard = vanguard[component]
                elif type(vanguard) == list and vanguard and vanguard[-1][grand_prev_key + 'Index'] == component:
                    vanguard = vanguard[-1]
                else: 
                    vanguard = None

                if grand_prev_key in special_keys:
                    break
            
            if type(prev) == dict:
                prev["-".join(key_components[i:])] = value
            elif type(prev) == list:
                prev.append(value)

        return parsed_response

    @classmethod
    def from_raw_data(cls, raw_data):
        if not(raw_data):
            return Frame()
        internal_representations = {frame_data['index']: Frame() for frame_data in raw_data['frame']}
        for frame_data in raw_data["frame"]:
            frame = internal_representations[sanitize_frame_index(frame_data['index'])]
            if 'var' not in frame_data:
                continue
            for var_data in frame_data["var"]:
                frame.bind(var_data['name'], var_data['val'])
            if 'name' in frame_data:
                frame.name = frame_data["name"]
            if 'parent' in frame_data and frame_data['parent']:
                frame.parent = internal_representations[sanitize_frame_index(frame_data['parent'])]
                frame.parent.children.append(frame)
            if 'return' in frame_data:
                frame.return_value = frame_data['return']
        
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
        return hash(self.bindings) + hash(self.children) + hash(self.name)
    
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.name == other.name and self.bindings == other.bindings and self.children == other.children