# from pyquery import PyQuery as pq
import chevron

def generate(element_html, data):
    pass

def prepare(element_html, data):
    pass

def parse(element_html, data):
    # doc = pq(element_html)
    # inputs = doc(".pl-html-input")
    # for input in inputs:
    #     key = input.attr('pl-html-key')
    #     value = input.val()
    #     data["submitted_answers"][key] = value
    pass

def render(element_html, data):
    with open("editor.mustache", "r") as f:
        return chevron.render(f, {}).strip()

class Frame():
    is_global = False

    def __init__(self, bindings=None, parent=None):
        self.parent = parent
        if bindings is None:
            self.bindings = {}
        self.name = None

    def bind(self, name, value):
        self.bindings[name] = value # Note: this will allow for duplicate entries. need to figure out a better way to do this. 
    
    def set_name(self, name):
        self.name = name

class Environment():
    def __init__(self, *frames):
        self.frames = frames
        self.global_frame = frames[0]

    def add_frame(self, bindings=None, parent=None):
        frame = Frame(bindings, parent)
        self.frames.append(frame)
        return frame

correct_env = Environment([Frame({'x': 5})])
def grade(element_html, data):
    parsed_response = {}
    for key, value in data['submitted_answers'].items():
        key_components = key.split("-")
        vanguard = parsed_response
        for component in key_components[:-1]:
            if component in vanguard:
                vanguard = vanguard[component]
            else: 
                vanguard[component] = {} # created unnecessary dicts at end
                vanguard = vanguard[component]
        vanguard[key_components[-1]] = value
    
    total_correct = int('var0' in parsed_response['f0'] and parsed_response['f0']['var0'] == {'name': 'x', 'val': '5'}) \
        + int('var1' in parsed_response['f0'] and parsed_response['f0']['var1'] == {'name': 'y', 'val': '17'})
    data['partial_scores']['f0'] = {'score':max(min(total_correct, 2), 0)/2,
                                    'feedback':'',
                                    'weight':1}
    
    return data