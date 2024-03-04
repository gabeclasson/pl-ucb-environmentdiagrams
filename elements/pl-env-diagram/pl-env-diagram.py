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
    print(data['submitted_answers'])
    data['submitted_answers'] = Frame.unflatten_raw_data(data["submitted_answers"])
    return data

def render(element_html, data):
    with open("editor.mustache", "r") as f:
        if data['panel'] == 'submission':
            return chevron.render(f.read(), data['submitted_answers'] + {'show_controls': False})
        elif data['panel'] == 'answer':
            return chevron.render(f.read(), data['correct_answers'] + {'show_controls': False})
        else: 
            return chevron.render(f.read(), {'frame': [{'name': None, 'index': 0, 'var': [], 'parent': None}], 'show_controls': True})

correct_env = Frame(bindings={'x': '5', 'y': '17'})
def grade(element_html, data):
    frame = Frame.from_raw_data(data['submitted_answers'])
    score = int(frame.freeze() == correct_env.freeze())
    data['partial_scores']['problem'] = {'score':score,
                                    'feedback':'',
                                    'weight':1}