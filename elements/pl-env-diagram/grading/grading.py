import autoeval
import copy
import hashlib

# TODO: keep in autoeval or move here?
def generate_html_json(self):
        # stores values of objects.
        self.heap_dict = {"func":[], "sequence":[]}
        # keeps track of how many of the same frame name exist
        self.frames_list = []
        # maps id() of objects to their index in heapdict. 
        mem_to_index_dict = {}
        def handle_variable(raw_variable, name = None, listIndex = None, varIndex = None):
            # TODO: i dont know whether its better to have these as separate lines for readibility, or in just one line
                variable = {
                    "val": None,
                    "name": name, # none if list element
                    "valWidth": None, # no valWidth if object 
                    "varIndex": varIndex, # none if list element
                    "nameWidth": len(name) + 1 if name is not None else None, # none if list element
                }
                # TODO: i dont know whether its better to have the primitives as separate lines for readibility, or in just one line
                if type(raw_variable).__name__ == "str":
                    variable["val"] = raw_variable.__repr__()
                    variable["valWidth"] = len(variable["val"]) + 1
                elif type(raw_variable).__name__ == "int":
                    variable["val"] = raw_variable.__repr__()
                    variable["valWidth"] = len(variable["val"]) + 1
                elif type(raw_variable).__name__ == "float":
                    variable["val"] = raw_variable.__repr__()
                    variable["valWidth"] = len(variable["val"]) + 1
                elif type(raw_variable).__name__ == "boolean":
                    variable["val"] = raw_variable.__repr__()
                    variable["valWidth"] = len(variable["val"]) + 1
                elif type(raw_variable).__name__ == "function":
                    if id(raw_variable) in mem_to_index_dict:
                        func_index = mem_to_index_dict[id(raw_variable)]  
                        variable["val"] = "#heap-func-" + str(func_index)  
                    else:
                        variable["val"] = "#heap-func-" + str(len(self.heap_dict["func"]))
                        parent = self.codestrID_parent_dict[id(raw_variable.__code__)]
                        mem_to_index_dict[id(raw_variable)] = len(self.heap_dict["func"])
                        self.heap_dict["func"].append({"name":raw_variable.__name__, 
                                                    "parent":parent, 
                                                    "funcIndex":len(self.heap_dict["func"]), 
                                                    "nameWidth":len(raw_variable.__name__) + 1})
                    del variable["valWidth"]

                elif type(raw_variable).__name__ == "list" or type(raw_variable).__name__ == "tuple":
                    if id(raw_variable) in mem_to_index_dict:
                        seq_index = mem_to_index_dict[id(raw_variable)]  
                        variable["val"] = "#heap-sequence-" + str(seq_index)  
                    else:
                        variable["val"] = "#heap-sequence-" + str(len(self.heap_dict["sequence"]))
                        seq = {"item":[], "type":type(raw_variable).__name__, "sequenceIndex":len(self.heap_dict["sequence"])}
                        mem_to_index_dict[id(raw_variable)] = len(self.heap_dict["sequence"])
                        for i in range(len(raw_variable)):
                            seq["item"].append(handle_variable(raw_variable[i], listIndex=i))
                        self.heap_dict["sequence"].append(seq)
                    del variable["valWidth"]

                if listIndex is not None:
                    variable["listIndex"] = listIndex
                    del variable["name"]
                    del variable["varIndex"]
                    del variable["nameWidth"]

                return variable

        def addtojson(frame):
            newframe = {}
            # in the end, the values will be converted to a list. It is initially a dictionary just for ease of variable location
            newframe["var"] = []
            if frame.__name__ != "global":
                newframe["name"] = frame.__name__
                newframe["parent"] = frame.parent.index
                # keep this line?
                newframe["return"] = None
                # may cause formatting issues, check this
                newframe["nameWidth"] = 2
            newframe["frameIndex"] = len(self.frames_list)
            self.frames_list.append(newframe)

            i = 0
            for varname in frame.bindings:
                if varname == "returnval":
                    variable = handle_variable(frame.bindings[varname], name = varname, varIndex=i)
                    newframe["return"] = {"val":variable["val"]}
                    break
                # TODO: MOVE TO FRAMETREE DEF
                newframe["var"].append(handle_variable(frame.bindings[varname], name = varname, varIndex=i))
                i = i + 1
            for child in frame.children:
                addtojson(child)
        addtojson(self.root)
        return {"heap": self.heap_dict, "frame":self.frames_list}

def convert_studentinput_to_json(student_input):
    frames_dict = {}
    heap_dict = {}
    reverse_heap = {}
    varcount = 0
    for frame in student_input["frame"]:
        currframe = {}
        if frame["frameIndex"] == "0":
            name = "global"
            # modifies student input
            frame["pname"] = "global"
        else:
            name = frame["name"]
            parent_index = 0 if frame["parent"] == "Global" else int(frame["parent"][1:])
            name = name + "#" + student_input["frame"][parent_index]["pname"]
            frame["pname"] = name
        if name not in frames_dict:
            frames_dict[name] = []
        for var in frame["var"]:
            value = var["val"]
            if value in reverse_heap:
                currframe[var["name"]] = reverse_heap[value]
            else:
                currframe[var["name"]] = varcount
                heap_dict[varcount] = value
                reverse_heap[value] = varcount
                varcount += 1
        if "return" in frame:
            value = frame["return"]["val"]
            if value in reverse_heap:
                currframe["returnval"] = reverse_heap[value]
            else:
                currframe["returnval"] = varcount
                heap_dict[varcount] = value
                reverse_heap[value] = varcount
                varcount += 1
        frames_dict[name].append(currframe)
                
        
    return frames_dict, heap_dict

# function that will make a hash out of a frame dictionary. Assumes input is a simplified frame dictionary
def hash_frame(frame):
    hashSum = 0
    for key in frame:
        if key == "var":
            # TODO: might cause bugs with return not being counted if "var" doesn't exist in empty frames.
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


# NOTE: DEPRECATED
# re-orders pointer variables and frames in order by serialization of crucial components to make comparison easier.
def reorder_html_json(json):
    json = FrameTree.simplify_html_json(json)
    json = copy.deepcopy(json)
    # get the global frame in the 0th position
    finalFrameList = [json["frame"][0]]
    # remove the global frame from the json since we don't need it anymore. 
    del json["frame"][0]
    # frame reordering dict that maps the old index to the new index
    frameReorder = {"Global":"Global"}
    parentpq = ["Global"]
    while len(parentpq) > 0:
        currParent = parentpq[0]
        currFrameList = []
        for frame in json["frame"]:
            if frame["parent"] == currParent:
                currFrameList.append(frame)
        copyCurrFrameList = copy.deepcopy(currFrameList)
        previousCurrListOrdering = []
        for frame in currFrameList:
            json["frame"].remove(frame)
            previousCurrListOrdering.append(int(currFrameList["frameIndex"]))
            del currFrameList["frameIndex"]
            del copyCurrFrameList["frameIndex"]
        
        
        parentpq = parentpq[1:]
    pass

def grading(generated_json, student_json, partial_credit = "none"):
    """ options for partial_credit include:
    "none" --> no partial credit
    "by_frame" --> gets credit per correct frame, and lose points for extra frames. if heap is not identical, loses 1/3 credit."""
    generated_json = simplify_html_json(generated_json)
    generated_json = sort_frame_json(generated_json)
    generated_json = sort_heap_json(generated_json)
    student_json = simplify_html_json(student_json)
    student_json = sort_frame_json(student_json)
    student_json = sort_heap_json(student_json)

    if partial_credit == "by_frame":
        if generated_json["heap"] == student_json["heap"] and generated_json["frame"] == student_json["frame"]:
            return 1
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
        # return the score with an upper bound of 1 and a lower bound of 0 (just to avoid rounding issues).
        return max(0, min(1, score))

    elif partial_credit == "none":
        return generated_json["heap"] == student_json["heap"] and generated_json["frame"] == student_json["frame"]
    
    raise Exception("valid partial credit setting not provided")

def grade_allornothing1(self, other):
        self_heap_dict = FrameTree.simplify_html_json(self.heap_dict)
        self_frames_list = FrameTree.simplify_html_json(self.frames_list)
        other_heap_dict = FrameTree.simplify_html_json(other["heap"])
        other_frames_list = FrameTree.simplify_html_json(other["frame"])

        # set up dictionaries that will assign names of matching frames and matching object pointers across self and other.
        selfToOther_frames = {"Global":"Global"}
        selfToOther_objects = {}

        # function that will check variable equality for us, even if the order is different or pointer locations differ
        # it will not detect if the objects it associates happen to be different. at the end we will check for heap equality given the found associations.
        # O(n^2) time
        def equal_ignore_order(a, b):
            """ Use only when elements are neither hashable nor sortable! """
            unmatched = list(b)
            for elementA in a:
                foundMatch = False
                for elementB in unmatched:
                    if elementA["name"] == elementB["name"]: 
                        # this line only looks at objects with pointers. the first character can only be "#" for objects, since "#" is a comment character which we manually place to denote an object.
                        if elementA["val"][:1] == "#":
                            # then, we have to check that the two are the same kind of object. 
                            if not elementA["val"].split("-")[:-1] ==  elementB["val"].split("-")[:-1]:
                                break
                            # now check to see if there is already an association between the object in elementA and elementB, and if there is make sure it is matching.
                            elif elementA["val"] in selfToOther_objects:
                                if selfToOther_objects[elementA["val"]] == elementB["val"]:
                                    foundMatch = True
                                # if there is an entry but it doesn't match, we haven't found matching variables
                                break
                            else:
                                selfToOther_objects[elementA["val"]] = elementB["val"]
                                foundMatch = True
                        # if the two elements are NOT objects and they values stored are equal, they are equivalent.
                        elif elementA == elementB:
                            foundMatch = True
                            break

                if foundMatch:
                    unmatched.remove(elementB)  
                else:
                    return False

            return not unmatched

        # check that the global frames are equivalent
        # TODO: will not work if objects have differening indices
        if not equal_ignore_order(self_frames_list[0]["var"], other_frames_list[0]["var"]):
            print("Failed attempt - global frames are not equivalent")
            print(self_frames_list[0])
            print(other_frames_list[0])
            return 0
        
        # now find all of the matching frames for the rest of the function
        unmatchedSelf = list(self_frames_list[1:])
        unmatchedOther = list(other_frames_list[1:])
        # priority queue that tells us whose children to visit next. 
        parentpq = ["global"]
        while len(parentpq) > 0:
            currparent = parentpq[0]
            matched_frames = []
            for self_frame in unmatchedSelf:
                if self_frame["parent"] != currparent:
                    continue
                foundMatch = False
                for other_frame in unmatchedOther:
                    if self_frame["name"] != other_frame["name"]:
                        break
                    elif "parent" in self_frame["parent"] and selfToOther_frames[self_frame["parent"]] != other_frame["parent"]:
                        break
                if foundMatch:
                        selfToOther_frames["f" + self_frame["frameIndex"]] = "f" + other_frame["frameIndex"]
                        parentpq.append("f" + self_frame["frameIndex"])
                        matched_frames.append(self_frame)
                        unmatchedOther.remove(other_frame)  
                else:
                    return 0
            for self_frame in matched_frames:
                unmatchedSelf.remove(self_frame)
            parentpq = parentpq[1:]
        
        # check in the heap to make sure all matched pointer objects are really the same (from what we can tell)


        # at the end we check to make sure that when we modify everything so that the frame and pointer value locations are equivalent, we get them to be completely equal.

        # if the end check does not pass, we can attempt every possible mapping between frame indices and pointers to see if one configuration works. this is slow, but makes it unlikely that a student is mistakenly marked wrong.
        return 1

def grade_allornothing(A_json_frames = None, A_json_heap = None, B_json_frames = None, B_json_heap = None):
    """
    grades all or nothing
    """

    print("Aframes", A_json_frames)
    print("Bframes", B_json_frames)
    # check that the same framekeys exist in both A and B
    if A_json_frames.keys() != B_json_frames.keys():
        print("keys in A and B not matching.")
        return 0
    # Associates the pointer in A to the pointer in B.
    A_to_B_pointer_dict = {}
    # sets the indices of all frames in the other json to be yet to be checked
    for framekey in A_json_frames:
        framestomatch = [True]*len(B_json_frames[framekey])
        # get each frame with the same framename in A and find a match in B
        for a in range(len(A_json_frames[framekey])):
            has_match = False
            # get each frame with the same framename in B
            for b in range(len(B_json_frames[framekey])):
                # if b has already found a match in A_json_frames, do not attempt to match it. 
                if not framestomatch[b]:
                    continue
                # we assume that j is a match for i until proven otherwise
                is_match = True
                # gets all the variable keys that occur in A
                a_variablekeys = A_json_frames[framekey][a].keys()
                # first checks that we have matching keys between a and b
                if B_json_frames[framekey][b].keys() != a_variablekeys:
                    #print("not a match, mismatching variables")
                    is_match = False
                    continue
                # checks through each variable in the frame
                for a_varname in a_variablekeys:
                    # checks to make sure the variable exists in B
                    if not a_varname in B_json_frames[framekey][a]:
                        #print("not a match, other does not have variable ", a_varname)
                        is_match = False
                        break
                    # if we have the pointer from the variable name already recorded, check to make sure the value in the pointer dict
                    # matches what we expect
                    elif A_json_frames[framekey][a][a_varname] in A_to_B_pointer_dict:
                        if B_json_frames[framekey][b][a_varname] != A_to_B_pointer_dict[A_json_frames[framekey][a][a_varname]]:
                            #print("not a match, variable pointers are mismatched")
                            is_match = False
                            break
                    else:
                        # check that the values stored in each variable are the same
                        if A_json_heap[A_json_frames[framekey][a][a_varname]] != B_json_heap[B_json_frames[framekey][b][a_varname]]:
                            #print("not a match, variable values are not matched")
                            is_match = False
                            break
                        # if they are the same, we can keep track of the equivalence in pointers for future comparisons.
                        A_to_B_pointer_dict[A_json_frames[framekey][a][a_varname]] = B_json_frames[framekey][b][a_varname]
                # if everything in b matches everything in a, we have found the matching frames.
                if is_match:    
                    # to prevent "b" from being matched to future frames in "A"
                    framestomatch[b] = False
                    has_match = True
                    break
            # if frame A doesn't have a matching frame, leave
            if not has_match:
                print("unable to find matching frame in B for A for frame", framekey)
                return 0
        # if there are leftover frames in B, return 0
        if sum(framestomatch) > 0:
            return 0
    return 1

def check_validity(student_input):
    pass


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



intsonly_ft = autoeval.FrameTree(autoeval.example_intsonly)
intsonly_json = intsonly_ft.generate_html_json()
#student_input = simplify_html_json(student_input)
#print(student_input)
#html_json = sort_frame_json(student_input)
#html_json = sort_heap_json(html_json)
#print(html_json)
print(grading(intsonly_json, student_input_correct_intsonly, partial_credit="by_frame"))


