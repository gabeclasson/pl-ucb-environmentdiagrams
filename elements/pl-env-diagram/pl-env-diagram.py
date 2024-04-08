import chevron
import re
import lxml.html
from frame import *
import prairielearn as pl
import json
import grading.grading as grading

# maybe issue is in info.json? check documentation

def generate(element_html, data):
    # These two 'with' statements silence the execution so no print statements are printed, which can bug out prarielearn. 
    # with open(os.devnull, 'w') as devnull:
    #     with contextlib.redirect_stdout(devnull):
    #         codestring = Qgen.generateQ(data["variant_seed"])
    # data["params"] = {"codestring":codestring, "codelength":len(codestring.split('\n')) - 1}
    # data["correct_answers"] = grading.get_correctAnswerJSON(codestring)
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

# NOT STARTED
def parse_text_from_env_diagram(json):
    if not json:
        print("Error in instructor-provided correct environment diagram.")
    frame_text_lst = []
    for frame in json["frame"]:

        return
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
    #print(data["params"]["codestring"])
    generate(element_html, data)
    element = lxml.html.fragment_fromstring(element_html)
    for sub_element in element.iter():
        if sub_element.tag == "base-code":
            base_code = sub_element.text
            data["correct_answers"] = grading.get_correctAnswerJSON(base_code)
            #correct_answers = parse_env_diagram_from_text(env_diagram_text)
            #data['correct_answers'] = correct_answers
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
                    print(structured_answers)
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

default_submission = {'frame': [{'name': None, 'frameIndex': 0, 'var': [], 'parent': None}], 'heap': {}}
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
    score, feedback = grading.grading(data['correct_answers'], data['submitted_answers'], partial_credit="by_frame")
    data['partial_scores']['problem'] = {'score': score,
                                    'feedback': feedback,
                                    'weight':1}
