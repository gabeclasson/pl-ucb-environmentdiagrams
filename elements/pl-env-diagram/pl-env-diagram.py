import chevron, re
import lxml.html
from frame import *
import prairielearn as pl

def generate(element_html, data):
    pass

env_diagram_text_pattern = re.compile(r"""[Ff]rame[\t\f\cK ]+(?:
                    (?P<index_1>[Gg](?:lobal)?)|(?:(?P<index_2>[Ff]\d+)[\t\f\cK ]*
                    (?P<name>\w+)[\t\f\cK ]*
                    \[[\t\f\cK ]*[Pp](?:arent)?[\t\f\cK ]*=[\t\f\cK ]*(?P<parent>[Gg](?:lobal)?|f\d+)[\t\f\cK ]*\]))[\t\f\cK ]*:
                        (?P<variables>(?:$\n[\t\f\cK ]*(?:\w+)[\t\f\cK ]+.*\S+.*$)*
                        (?:$\n[\t\f\cK ]*\#[Rr](?:eturn)?[\t\f\cK ]+(?:.*)$)?)""", re.X | re.M)

def parse_env_diagram_from_text(text):
    print(text)
    m = env_diagram_text_pattern.findall(text)
    if not m:
        print("Issue with formatting in correct environment diagram: " + text)
    frame_lst = []
    for index1, index2, name, parent, vars in m:
        frame = {}
        index = (index1 + index2).strip()
        if index[0].lower() == "g" or index == "f0":
            frame['index'] = str(0)
        else: 
            frame['index'] = index[1:]
        frame['name'] = name
        frame['parent'] = parent
        lines = vars.split("\n")
        frame['var'] = bindings = []
        for j, line in enumerate(lines):
            line = line.strip()
            try: 
                index = line.index(" ")
            except:
                return
            var = line[:index].strip()
            val = line[index].strip()
            if var[0] == '#':
                frame['return'] = {'val': val}
            else: 
                bindings.append({
                    'index': j,
                    'var': var,
                    'val': val
                })
        frame_lst.append(frame)
    return {'frame': frame_lst}

def prepare(element_html, data):
    element = lxml.html.fragment_fromstring(element_html)
    for sub_element in element.iter():
        if sub_element.tag == "correct-env-diagram":
            env_diagram_text = sub_element.text
            print(env_diagram_text)
            correct_answers = parse_env_diagram_from_text(env_diagram_text)
            data['correct_answers'] = correct_answers
    return data

def parse(element_html, data):
    # doc = pq(element_html)
    # inputs = doc(".pl-html-input")
    # for input in inputs:
    #     key = input.attr('pl-html-key')
    #     value = input.val()
    #     data["submitted_answers"][key] = value
    data['submitted_answers'] = Frame.unflatten_raw_data(data["submitted_answers"])
    return data

default_rendering_data = {'frame': [{'name': None, 'index': 0, 'var': [], 'parent': None}], 'show_controls': True}
def render(element_html, data):
    with open("editor.mustache", "r") as f:
        template = f.read()
        if data['panel'] == 'answer':
            rendering_data = data['correct_answers']
            show_controls = False
        elif data['panel'] == 'question': 
            rendering_data = data['submitted_answers']
            show_controls = True
        else: # Submission
            rendering_data = data['submitted_answers']
            show_controls = False
        if not rendering_data:
            rendering_data = default_rendering_data
        rendering_data.update({'show_controls': show_controls})
        return chevron.render(template, rendering_data)  
            
def grade(element_html, data):
    frame = Frame.from_raw_data(data['submitted_answers'])
    correct_frame = Frame.from_raw_data(data['correct_answers'])
    score = int(frame.freeze() == correct_frame.freeze())
    data['partial_scores']['problem'] = {'score':score,
                                    'feedback':'',
                                    'weight':1}