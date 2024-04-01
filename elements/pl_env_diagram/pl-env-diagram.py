import chevron
import re
import lxml.html
from frame import *
import prairielearn as pl
import json
import grading.autoeval as autoeval

def generate(element_html, data):
    pass

env_diagram_text_pattern = re.compile(r"""
	(?P<index>[Gg](?:lobal)?|[Ff]\d+)[\t\f ]*(?::[\t\f ]]*
	                    (?P<name>\w+)[\t\f ]*
	                    \[[\t\f ]*[Pp](?:arent)?[\t\f ]*=[\t\f ]*(?P<parent>[Gg](?:lobal)?|f\d+)[\t\f ]*\])?[\t\f ]*
	                        (?P<variables>(?:$\n[\t\f ]*(?:\w+)[\t\f ]+.*\S+.*$)*
	                        (?:$\n[\t\f ]*\#[Rr](?:eturn)?[\t\f ]+(?:.*)$)?)
	""", re.VERBOSE | re.MULTILINE)

def parse_env_diagram_from_text(text):
    m = env_diagram_text_pattern.findall(text)
    if not m:
        print("Error in instructor-provided correct environment diagram.")
    frame_lst = []
    for index, name, parent, vars in m:
        frame = {}
        index = index.strip()
        if index[0].lower() == "g" or index == "f0":
            frame['frameIndex'] = str(0)
        else: 
            frame['frameIndex'] = index[1:]
        frame['name'] = name
        frame['parent'] = parent
        lines = vars.split("\n")
        frame['var'] = bindings = []
        for j, line in enumerate(lines):
            line = line.strip()
            try: 
                index = line.index(" ")
            except:
                continue
            var = line[:index].strip()
            val = line[index:].strip()
            if var[0] == '#':
                frame['return'] = {'val': val}
            else: 
                bindings.append({
                    'varIndex': j,
                    'name': var,
                    'val': val
                })
        frame_lst.append(frame)
    return {'frame': frame_lst}

def prepare(element_html, data):
    element = lxml.html.fragment_fromstring(element_html)
    for sub_element in element.iter():
        if sub_element.tag == "correct-env-diagram":
            env_diagram_text = sub_element.text
            correct_answers = parse_env_diagram_from_text(env_diagram_text)
            data['correct_answers'] = correct_answers
    return data

def parse(element_html, data):
    if not data["submitted_answers"]:
        data['submitted_answers'] = default_submission
    structured_answers = Frame.unflatten_raw_data(data["submitted_answers"], ('pointer',))
    pointer_list = []
    def investigate(key, obj, history, parent):
        if type(obj) == list:
            for item in obj:
                investigate(item[key + "Index"], item, history + [item[key + "Index"]], obj)
        elif type(obj) == dict:
            for child_key, child in dict(obj).items():
                investigate(child_key, child, history + [child_key], obj)
        else: 
            if (key == 'val' or key == 'name') and type(obj) == str: # Injecting lengths and pointer information
                if key == 'val' and obj and obj[0] == '#':
                    origin = "-".join(history)
                    raw_pointer_data = structured_answers['pointer'][origin+"-input"]
                    pointer_data = json.loads(raw_pointer_data)
                    pointer_data.update({'origin': origin, 'destination': obj[1:], 'raw': raw_pointer_data})
                    pointer_list.append(pointer_data)
                else: 
                    parent[key + 'Width'] = len(obj) + 1
    investigate(None, structured_answers, [], None)
    structured_answers['pointer'] = pointer_list
    data['submitted_answers'] = structured_answers
    return data

default_submission = {'frame': [{'name': None, 'frameIndex': 0, 'var': [], 'parent': None}]}
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
            rendering_data = default_submission
        rendering_data.update({'show_controls': show_controls})
        return chevron.render(template, rendering_data)

def grade(element_html, data):
    frame = Frame.from_raw_data(data['submitted_answers'])
    correct_frame = Frame.from_raw_data(data['correct_answers'])
    A_frames, A_heap = autoeval.convert_studentinput_to_json(frame)
    B_frames, B_heap = autoeval.convert_studentinput_to_json(correct_frame)
    #score = int(frame.freeze() == correct_frame.freeze())
    score = autoeval.grade_allornothing(A_json_frames= A_frames, A_json_heap=A_heap, B_json_frames= B_frames, B_json_heap=B_heap)
    data['partial_scores']['problem'] = {'score':score,
                                    'feedback':'',
                                    'weight':1}