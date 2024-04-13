try:
    import autoeval
except:
    import grading.autoeval as autoeval
import hashlib
import copy

# function that will make a hash out of a frame dictionary. Assumes input is a simplified frame dictionary
def hash_frame(frame):
    hashSum = 0
    for key in frame:
        if key == "var":
            variable_dictList = frame["var"] + [frame["return"]] if ("return" in frame and frame["return"]) else frame["var"]
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
        for badKey in ["nameWidth", "valWidth", "funcIndex", "listIndex", "tupleIndex", "varIndex", "isLastElement"]:
            if badKey in iterable:
                del iterable[badKey]
        if "val" in iterable:
            if iterable["val"] in pointerlocs:
                iterable["val"] = pointerlocs[iterable["val"]]
            # reformats strings so they all have the same enclosing marks
            if len(iterable["val"]) > 0 and iterable["val"][0] == '"' and iterable["val"][-1] == '"':
                iterable["val"] = "'" + iterable["val"][1:-1] + "'"
        if "frameIndex" in iterable:
            if "var" not in iterable:
                iterable["var"] = []
            if iterable["frameIndex"] in parentNames:
                iterable["frameIndex"] = parentNames[iterable["frameIndex"]]
        if "parent" in iterable and iterable["parent"] and iterable["parent"][1:] in parentNames:
            iterable["parent"] = parentNames[iterable["parent"]] #####
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
    frame_list[0]["name"] = "Global"
    parentpq = [("Global", 0)]
    # insert depth into each frame. additionally create a "depths_list" which at each index i has all of the frames at depth i.
    depth_lists = [[frame_list[0]]]
    while len(parentpq) > 0:
        currParent = parentpq[0][0]
        currDepth = parentpq[0][1] + 1
        for frame in frame_list:
            if type(frame["frameIndex"]) != str:
                frame["frameIndex"] = str(frame["frameIndex"])
            if "parent" in frame and (frame["parent"] == currParent) or (frame["parent"] == "f" + currParent):
                frame["depth"] = str(currDepth)
                parentpq.append(("f" + str(frame["frameIndex"]), currDepth))
                if len(depth_lists) <= currDepth:
                    depth_lists.append([frame])
                else:
                    depth_lists[currDepth].append(frame)
        parentpq = parentpq[1:]
    # clear frame_list, and create new one in order of depth, which are then sorted deterministically by the frame hash.
    # additionally modifies frameIndex and parent on all frames (except Global) to correspond with the ordering.
    modified_indices = {"Global":"Global"}
    frame_list = []
    for depth_frames in depth_lists:
        depth_frames = sorted(depth_frames, key = hash_frame)
        for i in range(len(depth_frames)):
            # sort variables in list in order of hash (NOTE: this might make the diagram non-sensical, but this is just for grading so this should be fine)
            depth_frames[i]["var"] = sorted(depth_frames[i]["var"], key = lambda x: int(hashlib.sha256((x["name"] + x["val"]).encode('utf-8')).hexdigest(), 16))
            if depth_frames[i]["frameIndex"] == "0":
                continue
           ### parent = modified_indices[depth_frames[i]["parent"]]
            depth_frames[i]["parent"] = modified_indices[depth_frames[i]["parent"]] ###"Global" if parent == "Global" else "f" + parent
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
    newHeap_dict = {"func":[], "list":[], "tuple": []}
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
    for sequence_type_name in ("list", "tuple"):
        if sequence_type_name in html_json["heap"]:
            for sequence in html_json["heap"][sequence_type_name]:
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

def grading(generated_json, student_json, partial_credit = "by_frame"):
    """ returns score and feedback (if applicable) for the student.
    
    options for partial_credit include:
    "none" --> no partial credit
    "by_frame" --> gets credit per correct frame, and lose points for extra frames. if heap is not identical, loses 1/3 credit."""
    score, feedback = check_validity(student_json)
    if feedback:
        return score, feedback
    student_json = copy.deepcopy(student_json)
    orig = generated_json
    generated_json = copy.deepcopy(generated_json)
    try:
        if student_json["frame"][0]["parent"] is None:
            del student_json["frame"][0]["parent"]
            del student_json["frame"][0]["name"]
    except:
        pass
    if "heap" not in generated_json:
        generated_json["heap"] = {}
    if "heap" not in student_json:
        student_json["heap"] = {}
    generated_json = simplify_html_json(generated_json)
    generated_json = sort_frame_json(generated_json)
    generated_json = sort_heap_json(generated_json)
    try:
        student_json = simplify_html_json(student_json)
        student_json = sort_frame_json(student_json)
        student_json = sort_heap_json(student_json)
    except Exception as e:
        return None, ""

    if partial_credit == "by_frame":
        feedback = []
        if generated_json["heap"] == student_json["heap"] and generated_json["frame"] == student_json["frame"]:
            return 1, ""
        # if not perfect, continue to partial credit. 
        score = 0
        framesListG = [hash_frame(frame) for frame in generated_json["frame"]]
        framesListS = [hash_frame(frame) for frame in student_json["frame"]]
        student_frame_count = len(framesListS)
        # if student provided less frames than exist, remove the amount of extras divided by their total framecount from the score.
        score -= max(0, len(framesListG) - len(framesListS))/len(framesListG)
        for frame in framesListG:
            # TEMPORARY SOLUTION
            findex = framesListG.index(frame)
            if frame in framesListS:
                score += 1/student_frame_count
                framesListS.remove(frame)
            elif findex < student_frame_count:
                feedback.append(("Global" if findex == 0 else "f" + str(findex)) + " is incorrect.\n")
        # for frame in generated_json["frame"]:
            #if hash_frame(frame) in framesListS:
            #    score += 1/len(student_json["frame"])
            #    framesListS.remove(frame)
            #else:
            #    feedback.append("Frame "+ frame["name"])
        # return the score with an upper bound of 1 and a lower bound of 0 (just to avoid rounding issues).
        return max(0, min(1, score)), "\n".join(feedback) #+ "\n student" + student_json["frame"].__repr__() + " \n gen" + generated_json["frame"].__repr__() + "\n orig" + orig["frame"].__repr__()

    elif partial_credit == "none":
        return generated_json["heap"] == student_json["heap"] and generated_json["frame"] == student_json["frame"], ""
    
    raise Exception("valid partial credit setting not provided")

def check_validity(student_input):
    return 1, None

def get_correctAnswerJSON(codestring):
    return autoeval.FrameTree(codestring).generate_html_json()

