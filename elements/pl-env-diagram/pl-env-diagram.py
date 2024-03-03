from frame import *

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
        return f.read()

correct_env = Frame({'x': '5', 'y': '17'})
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

    internal_representations = {}
    for key in parsed_response:
        if key[0] == "f" and key[1] in '1234567890':
            internal_representations[key] = Frame()
    
    for key in parsed_response:
        if key[0] == "f" and key[1] in '1234567890':
            frame_data = parsed_response[key]
            frame = internal_representations[key]
            for val_key in frame_data:
                if val_key == "return":
                    frame.bind("#return", frame_data[val_key])
                elif val_key == "parent": 
                    frame.parent = internal_representations[frame_data[val_key]]
                    frame.parent.children.append(frame)
                elif val_key[:3] == "var": 
                    frame.bind(frame_data[val_key]['name'], frame_data[val_key]['val'])
    internal_representations['f0'].freeze()
    correct_env.freeze()
    score = int(internal_representations['f0'] == correct_env)
    data['partial_scores']['problem'] = {'score':score,
                                    'feedback':'',
                                    'weight':1}