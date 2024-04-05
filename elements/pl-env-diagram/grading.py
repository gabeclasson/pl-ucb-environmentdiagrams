import autoeval
import hashlib

# function that will make a hash out of a frame dictionary. Assumes input is a simplified frame dictionary
def hash_frame(frame):
    hashSum = 0
    for key in frame:
        if key == "var":
            variable_dictList = frame["var"] + [frame["return"]] if "return" in frame else frame["var"]
            for variable_dict in variable_dictList:
                # by summing all of the elements of the variable list, it makes it such that order doesn't matter.
                for key2 in variable_dict:
                    # we need to hash differently if the value is a pointer, since things can be arbitrarily ordered in the heap.
                    if type(variable_dict[key2]) == str and len(variable_dict[key2]) > 0 and variable_dict[key2][0] == "#":
                        modified_str = "".join(variable_dict[key2].split('-')[:-1])
                        hashSum += int(hashlib.sha256((key2 + modified_str).encode('utf-8')).hexdigest(), 16)
                    else:
                        hashSum += int(hashlib.sha256((key2 + str(variable_dict[key2])).encode('utf-8')).hexdigest(), 16)
        # we can skip "return" since we already handled it in the above part
        elif key == "return":
            continue
        # since parent names might be different accross student v. machine frame_lists, we ignore this entry.
        elif key == "parent" or key == "frameIndex":
            continue
        else:
            hashSum += int(hashlib.sha256((key + str(frame[key])).encode('utf-8')).hexdigest(), 16)
    return hashSum % 1073741824 

# recursive function that removes unnecessary variables for comparison.
# it can optionally replace a dictionary of pointer locations and parent names with other names
def simplify_html_json(iterable, pointerlocs = {}, parentNames = {}):
    if type(iterable) is list:
        for i in range(len(iterable)):
            # TODO: remove this from FrameTree?
            iterable[i] = simplify_html_json(iterable[i])
    elif type(iterable) is dict:
        for badKey in ["nameWidth", "valWidth", "funcIndex", "sequenceIndex", "varIndex"]:
            if badKey in iterable:
                del iterable[badKey]
        if "val" in iterable and iterable["val"] in pointerlocs:
            iterable["val"] = pointerlocs[iterable["val"]]
        if "frameIndex" in iterable and iterable["frameIndex"] in parentNames:
            iterable["frameIndex"] = parentNames[iterable["frameIndex"]]
        if "parent" in iterable and iterable["parent"][1:] in parentNames:
            iterable["parent"] = "f" + parentNames[iterable["parent"]]
        for key in iterable:
            iterable[key] = simplify_html_json(iterable[key])
    return iterable

def sort_frame_json(html_json): 
    """
    outputs the new html_json
    - expects an input of a simplified frame_list. Also replaces frameIndex with a hash.
    - modifies heap_dict by replacing frame names with the new frame names created via the sorting.
    """
    frame_list = html_json["frame"]
    frame_list[0]["depth"] = 0
    frame_list[0]["parent"] = ""
    frame_list[0]["name"] = ""
    parentpq = [("Global", 0)]
    # insert depth into each frame. additionally create a "depths_list" which at each index i has all of the frames at depth i.
    depth_lists = [[frame_list[0]]]
    while len(parentpq) > 0:
        currParent = parentpq[0][0]
        currDepth = parentpq[0][1] + 1
        for frame in frame_list:
            if "parent" in frame and frame["parent"] == currParent:
                frame["depth"] = str(currDepth)
                parentpq.append(("f" + str(frame["frameIndex"]), currDepth))
                if len(depth_lists) <= currDepth:
                    depth_lists.append([frame])
                else:
                    depth_lists[currDepth].append(frame)
        parentpq = parentpq[1:]
    # clear frame_list, and create new one in order of depth, which are then sorted deterministically by the frame hash.
    # additionally modifies frameIndex and parent on all frames (except global) to correspond with the ordering.
    modified_indices = {"Global":"Global"}
    frame_list = []
    for depth_frames in depth_lists:
        depth_frames = sorted(depth_frames, key = hash_frame)
        for i in range(len(depth_frames)):
            # sort variables in list in order of hash (NOTE: this might make the diagram non-sensical, but this is just for grading so this should be fine)
            depth_frames[i]["var"] = sorted(depth_frames[i]["var"], key = lambda x: int(hashlib.sha256((x["name"] + x["val"]).encode('utf-8')).hexdigest(), 16))
            if depth_frames[i]["frameIndex"] == "0":
                continue
            depth_frames[i]["parent"] = modified_indices[depth_frames[i]["parent"]]
            oldIndex = depth_frames[i]["frameIndex"]
            depth_frames[i]["frameIndex"] = depth_frames[i]["depth"] + ":" + str(i)
            modified_indices["f" + oldIndex] = depth_frames[i]["frameIndex"]
        frame_list += depth_frames
    html_json["frame"] = frame_list
    # modifies functions in the heap in correspondence to the new frame names
    heap_dict = html_json["heap"]
    if "func" in heap_dict:
        for i in range(len(heap_dict["func"])):
            heap_dict["func"][i]["parent"] = modified_indices[heap_dict["func"][i]["parent"]]
        html_json["heap"] = heap_dict
    return html_json

def sort_heap_json(html_json):
    """assumes input is a simplified html_json, and that the frames are sorted."""
    heap_dict = html_json["heap"]
    modified_indices = {}
    newHeap_dict = {"func":[], "sequence":[]}
    # TODO: since contents of loops in this one and the next are identical, consider moving to func.
    for frame in html_json["frame"]:
        variable_list = frame["var"] + [frame["return"]] if "return" in frame else frame["var"]
        for variable in variable_list:
            if type(variable["val"]) == str and len(variable["val"]) > 0 and variable["val"][0] == "#":
                if variable["val"] in modified_indices:
                    variable["val"] = modified_indices[variable["val"]]
                    continue
                val = variable["val"].split("-")
                varType = val[1]
                oldVarIndex = int(val[2])
                if varType not in newHeap_dict:
                    newHeap_dict[varType] = []
                modified_indices[variable["val"]] = "-".join(val[:2] + [str(len(newHeap_dict[varType]))])
                variable["val"] = modified_indices[variable["val"]]
                newHeap_dict[varType].append(html_json["heap"][varType][oldVarIndex])
    if "sequence" in html_json["heap"]:
        for sequence in html_json["heap"]["sequence"]:
            for variable in sequence["item"]:
                if type(variable["val"]) == str and len(variable["val"]) > 0 and variable["val"][0] == "#":
                    if variable["val"] in modified_indices:
                        variable["val"] = modified_indices[variable["val"]]
                        continue
                    val = variable["val"].split("-")
                    varType = val[1]
                    oldVarIndex = int(val[2])
                    if varType not in newHeap_dict:
                        newHeap_dict[varType] = []
                    modified_indices[variable["val"]] = "-".join(val[:2] + [str(len(newHeap_dict[varType]))])
                    variable["val"] = modified_indices[variable["val"]]
                    newHeap_dict[varType].append(html_json["heap"][varType][oldVarIndex])
    html_json["heap"] = newHeap_dict
    return html_json

def grading(generated_json, student_json, partial_credit = "none"):
    """ returns score and feedback (if applicable) for the student.
    
    options for partial_credit include:
    "none" --> no partial credit
    "by_frame" --> gets credit per correct frame, and lose points for extra frames. if heap is not identical, loses 1/3 credit."""
    if "heap" not in generated_json:
        generated_json["heap"] = {}
    if "heap" not in student_json:
        student_json["heap"] = {}
    generated_json = simplify_html_json(generated_json)
    generated_json = sort_frame_json(generated_json)
    generated_json = sort_heap_json(generated_json)
    student_json = simplify_html_json(student_json)
    student_json = sort_frame_json(student_json)
    student_json = sort_heap_json(student_json)

    if partial_credit == "by_frame":
        if generated_json["heap"] == student_json["heap"] and generated_json["frame"] == student_json["frame"]:
            return 1, ""
        # if not perfect, continue to partial credit. 
        score = 0
        framesListG = [hash_frame(frame) for frame in generated_json["frame"]]
        framesListS = [hash_frame(frame) for frame in student_json["frame"]]
        # if student provided more frames than exist, remove the amount of extras divided by their total framecount from the score.
        score -= max(0, len(framesListS) - len(framesListG))/len(framesListS)
        for frame in framesListG:
            if frame in framesListS:
                score += 1/len(framesListG)
                framesListS.remove(frame)
        #print(max(0, min(1, score)), generated_json["frame"].__repr__() + " \n" + student_json["frame"].__repr__() )
        # return the score with an upper bound of 1 and a lower bound of 0 (just to avoid rounding issues).
        return max(0, min(1, score)), generated_json["frame"].__repr__() + " \n" + student_json["frame"].__repr__()

    elif partial_credit == "none":
        return generated_json["heap"] == student_json["heap"] and generated_json["frame"] == student_json["frame"], ""
    
    raise Exception("valid partial credit setting not provided")

def check_validity(student_input):
    pass

def get_correctAnswerJSON(codestring):
    return autoeval.FrameTree(codestring).generate_html_json()


student_input = {
    "heap": {
        "func": [
            {"name": "f", "parent": "f1", "funcIndex": "0", "nameWidth": 2},
            {"name": "g", "parent": "Global", "funcIndex": "1", "nameWidth": 2},
        ],
        "sequence": [
            {
                "item": [
                    {"val": "#heap-sequence-1", "itemIndex": "0"},
                    {"val": "2", "valWidth": 2, "itemIndex": "1"},
                    {"val": '"goo"', "valWidth": 6, "itemIndex": "2"},
                    {"val": "4.56", "valWidth": 5, "itemIndex": "3"},
                    {"val": "2.0", "valWidth": 4, "itemIndex": "4"},
                    {"val": "True", "valWidth": 5, "itemIndex": "5"},
                    {"val": "False", "valWidth": 6, "itemIndex": "6"},
                ],
                "type": "list",
                "sequenceIndex": "0",
            },
            {
                "item": [
                    {"val": "3", "valWidth": 2, "itemIndex": "0"},
                    {"val": "2", "valWidth": 2, "itemIndex": "1"},
                    {"val": "#heap-func-1", "itemIndex": "2"},
                ],
                "type": "tuple",
                "sequenceIndex": "1",
            },
        ],
    },
    "frame": [
        {
            "var": [
                {"val": "#heap-func-0", "name": "x", "varIndex": "0", "nameWidth": 2},
                {
                    "val": "7",
                    "name": "y",
                    "valWidth": 2,
                    "varIndex": "1",
                    "nameWidth": 2,
                },
            ],
            "frameIndex": "0",
        },
        {
            "var": [
                {
                    "val": "#heap-sequence-0",
                    "name": "g",
                    "varIndex": "0",
                    "nameWidth": 2,
                }
            ],
            "name": "f",
            "parent": "Global",
            "return": {"val": "#heap-func-1"},
            "nameWidth": 2,
            "frameIndex": "1",
        },
        {
            "var": [
                {
                    "val": "5",
                    "name": "f",
                    "valWidth": 2,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {
                    "val": "",
                    "name": "lst",
                    "valWidth": 1,
                    "varIndex": "1",
                    "nameWidth": 4,
                },
            ],
            "name": "g",
            "parent": "Global",
            "return": {"val": "#heap-sequence-1"},
            "nameWidth": 2,
            "frameIndex": "3",
        },
        {
            "var": [
                {
                    "val": "False",
                    "name": "y",
                    "valWidth": 6,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {
                    "val": "5",
                    "name": "p",
                    "valWidth": 2,
                    "varIndex": "1",
                    "nameWidth": 2,
                },
            ],
            "name": "f",
            "parent": "f3",
            "return": {"val": "True", "valWidth": 5},
            "nameWidth": 2,
            "frameIndex": "4",
        },
    ],
    "pointer": [
        {
            "d": "M 0, 15.593754768371582 L 125.94375610351562 0",
            "raw": '{"d":"M 0, 15.593754768371582 L 125.94375610351562 0","width":"125.94375610351562","height":"15.593754768371582","top":"72.5938px","left":"171.994px"}',
            "top": "72.5938px",
            "left": "171.994px",
            "width": "125.94375610351562",
            "height": "15.593754768371582",
            "origin": "frame-0-var-0-val",
            "destination": "heap-func-0",
        },
        {
            "d": "M 0, 65.59376239776611 L 121.60000610351562 0",
            "raw": '{"d":"M 0, 65.59376239776611 L 121.60000610351562 0","width":"121.60000610351562","height":"65.59376239776611","top":"264.356px","left":"176.338px"}',
            "top": "264.356px",
            "left": "176.338px",
            "width": "121.60000610351562",
            "height": "65.59376239776611",
            "origin": "frame-1-return-val",
            "destination": "heap-func-1",
        },
        {
            "d": "M 0, 126.67501926422119 L 121.60000610351562 0",
            "raw": '{"d":"M 0, 126.67501926422119 L 121.60000610351562 0","width":"121.60000610351562","height":"126.67501926422119","top":"168.475px","left":"176.338px"}',
            "top": "168.475px",
            "left": "176.338px",
            "width": "121.60000610351562",
            "height": "126.67501926422119",
            "origin": "frame-1-var-0-val",
            "destination": "heap-sequence-0",
        },
        {
            "d": "M 0, 208.6749963760376 L 121.60000610351562 0",
            "raw": '{"d":"M 0, 208.6749963760376 L 121.60000610351562 0","width":"121.60000610351562","height":"208.6749963760376","top":"360.238px","left":"176.338px"}',
            "top": "360.238px",
            "left": "176.338px",
            "width": "121.60000610351562",
            "height": "208.6749963760376",
            "origin": "frame-3-return-val",
            "destination": "heap-sequence-1",
        },
        {
            "d": "M 29.79998779296875, 0 L 0 179.07499599456787",
            "raw": '{"d":"M 29.79998779296875, 0 L 0 179.07499599456787","width":"29.79998779296875","height":"179.07499599456787","top":"181.162px","left":"297.938px"}',
            "top": "181.162px",
            "left": "297.938px",
            "width": "29.79998779296875",
            "height": "179.07499599456787",
            "origin": "heap-sequence-0-item-0-val",
            "destination": "heap-sequence-1",
        },
        {
            "d": "M 133.39996337890625, 108.56876850128174 L 0 0",
            "raw": '{"d":"M 133.39996337890625, 108.56876850128174 L 0 0","width":"133.39996337890625","height":"108.56876850128174","top":"264.356px","left":"297.938px"}',
            "top": "264.356px",
            "left": "297.938px",
            "width": "133.39996337890625",
            "height": "108.56876850128174",
            "origin": "heap-sequence-1-item-2-val",
            "destination": "heap-func-1",
        },
    ],
}


student_input_modified = {
    "heap": {
        "func": [
            {"name": "g", "parent": "Global", "funcIndex": "0", "nameWidth": 2},
            {"name": "f", "parent": "f1", "funcIndex": "1", "nameWidth": 2},
        ],
        "sequence": [
            {
                "item": [
                    {"val": "#heap-sequence-1", "itemIndex": "0"},
                    {"val": "2", "valWidth": 2, "itemIndex": "1"},
                    {"val": '"goo"', "valWidth": 6, "itemIndex": "2"},
                    {"val": "4.56", "valWidth": 5, "itemIndex": "3"},
                    {"val": "2.0", "valWidth": 4, "itemIndex": "4"},
                    {"val": "True", "valWidth": 5, "itemIndex": "5"},
                    {"val": "False", "valWidth": 6, "itemIndex": "6"},
                ],
                "type": "list",
                "sequenceIndex": "0",
            },
            {
                "item": [
                    {"val": "3", "valWidth": 2, "itemIndex": "0"},
                    {"val": "2", "valWidth": 2, "itemIndex": "1"},
                    {"val": "#heap-func-0", "itemIndex": "2"},
                ],
                "type": "tuple",
                "sequenceIndex": "1",
            },
        ],
    },
    "frame": [
        {
            "var": [
                {"val": "#heap-func-1", "name": "x", "varIndex": "0", "nameWidth": 2},
                {
                    "val": "7",
                    "name": "y",
                    "valWidth": 2,
                    "varIndex": "1",
                    "nameWidth": 2,
                },
            ],
            "frameIndex": "0",
        },
        {
            "var": [
                {
                    "val": "#heap-sequence-0",
                    "name": "g",
                    "varIndex": "0",
                    "nameWidth": 2,
                }
            ],
            "name": "f",
            "parent": "Global",
            "return": {"val": "#heap-func-0"},
            "nameWidth": 2,
            "frameIndex": "1",
        },
        {
            "var": [
                {
                    "val": "5",
                    "name": "f",
                    "valWidth": 2,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {
                    "val": "",
                    "name": "lst",
                    "valWidth": 1,
                    "varIndex": "1",
                    "nameWidth": 4,
                },
            ],
            "name": "g",
            "parent": "Global",
            "return": {"val": "#heap-sequence-1"},
            "nameWidth": 2,
            "frameIndex": "3",
        },
        {
            "var": [
                {
                    "val": "False",
                    "name": "y",
                    "valWidth": 6,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {
                    "val": "5",
                    "name": "p",
                    "valWidth": 2,
                    "varIndex": "1",
                    "nameWidth": 2,
                },
            ],
            "name": "f",
            "parent": "f3",
            "return": {"val": "True", "valWidth": 5},
            "nameWidth": 2,
            "frameIndex": "4",
        },
    ],
}


student_input_correct_intsonly = {
    "heap": {
        "func": [
            {"name": "f", "parent": "Global", "funcIndex": "0", "nameWidth": 2},
        ],
    },
    "frame": [
        {
            "var": [
                {
                    "val": "5",
                    "name": "x",
                    "valWidth": 2,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {
                    "val": "6",
                    "name": "y",
                    "valWidth": 2,
                    "varIndex": "1",
                    "nameWidth": 2,
                },
                {
                    "val": "'7'",
                    "name": "d",
                    "valWidth": 2,
                    "varIndex": "2",
                    "nameWidth": 2,
                },
                {"val": "#heap-func-0", "name": "f", "varIndex": "3", "nameWidth": 2},
            ],
            "frameIndex": "0",
        },
        {
            "var": [
                {
                    "val": "10",
                    "name": "x",
                    "valWidth": 2,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {
                    "val": "20",
                    "name": "z",
                    "valWidth": 2,
                    "varIndex": "1",
                    "nameWidth": 2,
                },
            ],
            "name": "f",
            "parent": "Global",
            "return": {"val": "5"},
            "nameWidth": 2,
            "frameIndex": "1",
        },
    ],
}



#intsonly_ft = autoeval.FrameTree(autoeval.example_intsonly)
#intsonly_json = intsonly_ft.generate_html_json()
#print(grading(intsonly_json, student_input_correct_intsonly, partial_credit="by_frame"))


