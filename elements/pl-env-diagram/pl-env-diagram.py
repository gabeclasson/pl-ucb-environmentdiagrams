import chevron
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
        structured_data = Frame.unflatten_raw_data(data["submitted_answers"])
        return chevron.render(f.read(), structured_data)

correct_env = Frame({'x': '5', 'y': '17'})
def grade(element_html, data):
    frame = Frame.from_raw_data(data['submitted_answers']).freeze()
    correct_env.freeze()
    score = int(internal_representations['f0'] == correct_env)
    data['partial_scores']['problem'] = {'score':score,
                                    'feedback':'',
                                    'weight':1}