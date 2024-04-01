import pickle
import inspect
import heapq
import frame
import re
# i refer to this as "framenode" in some places. this is to avoid ambiguity. we will discuss changing the name.
Frame = frame.Frame

class FrameTree():
    originalcodestring = None
    codestring = None
    root = None
    # TODO: if i set these to {}, does that make these static?
    envframes_dict = None
    fobj_name_dict = None
    env_mutables = None
    # this is for debugging
    lastcreatedframe = None

    def __init__(self, codestring, debugmessages = False):
        self.originalcodestring = codestring
        self.codestring = codestring
        # a dictionary containing frames with associated variables in the form of a tuple: (type, name, mem loc, value)
        self.envframes_dict = {}
        # associates a frame object to a frame node (or in the case of global, at least for the time being, "global" to a frame node.)
        self.fobj_framenode_dict = {}
        self.env_mutables = {}
        self.debugmessages = debugmessages
        #self.framename_dict = {}
        self.get_evaldiag()
    
    def add_newframe(self, name = None): # func should always refer to the caller
        fobj = inspect.currentframe().f_back
        # if no frame nodes have been initialized, set the frame as the global frame and the root
        if len(self.fobj_framenode_dict.keys()) == 0:
            name = "global"
            frame = Frame(name = name, fobj = fobj)
            self.fobj_framenode_dict[fobj] = frame
            #self.fobj_name_dict[fobj] = name
            self.root = frame
            # OLD
            self.envframes_dict[name] = {"name": None, "parent": None, "parent_fobj": None, "curr_fobj": fobj}

        else: 
            parent_frame = fobj.f_back
            parent = self.fobj_framenode_dict[parent_frame] if parent_frame in self.fobj_framenode_dict else self.root
            name = fobj.f_code.co_name
            #if name in self.framename_dict:
            #    self.framename_dict[name] = self.framename_dict[name] + 1
            #    name = name + str(self.framename_dict[name])
            #else:
            #    self.framename_dict[name] = 0
            
            # OLD: dictionary rep of frame associations. Use for debugging only. 
            self.envframes_dict[name] = {"name": name, "parent": parent, "parent_fobj": parent_frame, "curr_fobj": fobj}
            # init FrameNode
            frame = Frame(name = name, parent = parent, fobj=fobj)
            # add self to the pairing dict
            self.fobj_framenode_dict[fobj] = frame
            # modify parent to include self as a child
            parent.add_child(self.fobj_framenode_dict[fobj])
            # OLD: dictionary rep between fobj and frame
            #self.fobj_name_dict[fobj] = name
            #print("test2: ", name, parent.__name__)
        self.lastcreatedframe = frame
        return frame
    
    def get_evaldiag(self):

        ##### FRAME TRACKING #####

        # TODO: maybe make it so you can input a func directly
        """This function adds a new line of code initializing the FrameNode in each function definition. 
        It then runs the new code made to get exitlines."""
        # does this by finding a 'def' statement, then inserting the init immediately after
        # if code is given as a string
        code_list = self.codestring.split("\n")

        # TODO: add mutables
        # first init all of the vars
        code_list.insert(0, "frame = self.add_newframe()")
        #  loop through all remaining code.
        i = 3 # modify to consider initalized vars
        while i < len(code_list):
            if code_list[i].lstrip(' ')[:4] == "def ":
                def_line = i
                # find the indent size after the def
                whitespace = 0
                while whitespace == 0:
                    i = i + 1
                    # check to make sure it's not just an empty line
                    if len(code_list[i].split()) > 0:
                        # get size of whitespace before code
                        whitespace = len(code_list[i]) - len(code_list[i].lstrip(' '))
                        # set this back to the previous line just in case the first non-empty line is a def statement.
                        i = i - 1
                # insert the code to create the FrameNode
                # TODO: make sure none of the variables are already in scope in the code.
                code_list.insert(def_line + 1, ' '*whitespace + "self.add_newframe()") 
            i = i + 1
        self.codestring = str.join("\n", code_list)
        d =  {"self":self, "inspect":inspect}
        exec(self.codestring, d, {})
        
        ### EXIT LINE TRACING ###
        # TODO: might get rid of: edits all FrameNodes to include a reference to which line it ends on (in the modified code)
        """edits all FrameNodes to include a reference to which line it ends on in .exitline. 
        Additionally returns a max heap of exit lines, and a dictionary mapping exit lines to Frame objects."""
        if self.debugmessages: print("========== RUNNING exit line tracing ==========") # TODO: make self.debugmessages a decorator and apply it to all funcs?

        exitlines_pq = []
        exitlines_fobj_dict = {} # might be able to replace this with an exitlines_pq to var list mapping. if so, change description of this func. 
        for fobj in self.fobj_framenode_dict:
            frame = self.fobj_framenode_dict[fobj]
            if fobj == "global":
                fobj = frame.fobj
            exitline = frame.fobj.f_lineno - 1
            exitlines_pq.append(exitline)
            exitlines_fobj_dict[exitline] = fobj

        # remove duplicate exit lines
        exitlines_pq = list(set(exitlines_pq))
        # heapify the list
        heapq._heapify_max(exitlines_pq)
        if self.debugmessages: print("========== COMPLETED exit line tracing ==========")

        ### BINDING TRACKING ###

        # clear the dictionary
        self.fobj_framenode_dict = {}

        # keeps track of how many lines have been inserted above the 
        # if code is given as a string
        # TODO: REMOVE BELOW LINE(S) WHEN ALL CODE IS WORKING
        exitlines_pq= exitlines_pq.copy()
        code_list = self.codestring.split("\n")

        # TODO: fix to include correct variable names
        # set variable names for things we are using to store tracking info. (TODO: CHNAGE NAME GLOBVAR)
        trk_var_names = ["returnval", "locs", "bindings", "fobj_framenode_dict", "envframes_dict", "frame_name_dict"]
        # if any of the initial variable names are in the local variable scope, we need to change the offending name(s). TODO: check if this is true once impl is done?
        for k in range(len(trk_var_names)):
            while trk_var_names[k] in exitlines_fobj_dict[exitline].f_code.co_varnames:
                trk_var_names[k] = str(hash(trk_var_names[k] + str(exitline)))[:7]

        # handle the global frame
        exitline = heapq._heappop_max(exitlines_pq)
        code_list.insert(exitline + 1, "globvar" + '=' "locals()")
        # TODO: 'var' might also be an issue here..     
        # TODO: var names
        code_list.insert(exitline + 2, "frame" + '=' "self.fobj_framenode_dict[inspect.currentframe()]")
        code_list.insert(exitline + 3, "frame.bind(" + "globvar" + "," + "exclude =  ['frame']" + ")") # + "," + " frame"
        

        #temp (move to main thing?)
        trk_var_names[1] = "locs"


        # get largest exitline
        while len(exitlines_pq) > 0:
            # get the current exitline (also the first line we insert into)!
            exitline = heapq._heappop_max(exitlines_pq)
            i = exitline
            whitespace = len(code_list[i]) - len(code_list[i].lstrip(' '))
            if code_list[i].lstrip(' ')[:7] == "return ":
                returnval = code_list[i].lstrip(' ')[7:]
                # set name for returnval in the code
                # change the return line to return the stored value
                code_list[i] = ' '*whitespace + "return " + trk_var_names[0]
                # insert a line that records the return value
                code_list.insert(i, ' '*whitespace + trk_var_names[0] + '=' + returnval)
            # store local variables at this point
            code_list.insert(i + 1, ' '*whitespace + trk_var_names[1] + '=' "locals()")
            # store bindings at this point
            # TODO: 'var' might also be an issue here..
            code_list.insert(i + 2, ' '*whitespace + trk_var_names[2] + '=' + trk_var_names[1])
            code_list.insert(i + 3, ' '*whitespace + "frame" + '=' "self.fobj_framenode_dict[inspect.currentframe()]")
            # TODO: var names
            code_list.insert(i + 4, ' '*whitespace + "frame.bind(" + trk_var_names[2] + ")")

        # get modified code with Frame initialization
        newcode = str.join("\n", code_list)
        # then execute the code
        exec(newcode, d, {})
        # TODO: Needed?
        del self.root.bindings["globvar"]
    
    def get_simple_json(self):
        sol = []
        def addtojson(frame, sol): 
            sol.append(frame.__name__)
            for varname in frame.bindings:
                match frame.bindings[varname]:
                    case int():
                        repr = frame.bindings[varname]
                    case _:
                        classname = frame.bindings[varname].__class__.__name__
                        #if classname not in objname_dict:
                            #objname_dict[classname] = 0

                        #objname_dict[classname] = objname_dict[classname] + 1
                        if hasattr(frame.bindings[varname], "__name__"):
                            repr = classname + " <" + str(frame.bindings[varname].__name__) + ">"
                        else:
                            repr = classname + " <>"
                sol.append("   " + varname + " " + str(repr))
            for child in frame.children:
                sol = addtojson(child, sol)
        addtojson(self.root, sol)
        print("sol:", sol)
        return "\n".join(sol)




    # RIGHT NOW ONLY WORKS WITH INTEGER + FUNC
    def get_json(self):
        # keeps track of how many of the same frame name exist
        frames_dict = {}
        # TODO: MOVE TO FRAMETREE DEF
        objname_dict = {"int":0, "dict":0, "func":0}
        objcounter = 0
        # stores values of objects.
        heap_dict = {}
        mem_to_loc_dict = {}
        def addtojson(frame, objcounter): # frames_dict, heap_dict, objname_dict
            newframe = {}
            if frame.json_name in frames_dict:
                frames_dict[frame.json_name] = frames_dict[frame.json_name] + [newframe]
            else: 
                frames_dict[frame.json_name] = [newframe]
            for varname in frame.bindings:

                if id(frame.bindings[varname]) in mem_to_loc_dict:
                    newframe[varname] = mem_to_loc_dict[id(frame.bindings[varname])]
                else:
                    # TODO: MOVE TO FRAMETREE DEF
                    match frame.bindings[varname]:
                        case int():
                            mem_to_loc_dict[id(frame.bindings[varname])] = objcounter#"int-" + str(objname_dict["int"])
                            #objname_dict["int"] = objname_dict["int"] + 1
                            heap_dict[mem_to_loc_dict[id(frame.bindings[varname])]] = str(frame.bindings[varname]) #[frame.bindings[varname],0]
                        case _:
                            classname = frame.bindings[varname].__class__.__name__
                            #if classname not in objname_dict:
                            #    objname_dict[classname] = 0
    
                            #objname_dict[classname] = objname_dict[classname] + 1
                            if classname == "function":
                                repr = "#heap-func-" + str(objname_dict["func"])
                                objname_dict["func"] += 1
                            elif hasattr(frame.bindings[varname], "__name__"):
                                repr = classname + " <" + str(frame.bindings[varname].__name__) + ">"
                            else:
                                repr = classname + " <>"
                            mem_to_loc_dict[id(frame.bindings[varname])] = objcounter
                            #heap_dict[mem_to_loc_dict[id(frame.bindings[varname])]] = [repr, list(mem_to_loc_dict.values()).count(repr)]
                            heap_dict[objcounter] = repr
                    newframe[varname] = mem_to_loc_dict[id(frame.bindings[varname])]
                objcounter = objcounter + 1
            for child in frame.children:
                objcounter = addtojson(child, objcounter)
            return objcounter
        addtojson(self.root, 0)
        return frames_dict, heap_dict

    def grade_allornothing(self, other = None, B_json_frames = None, B_json_heap = None):
        """
        grades all or nothing
        """
        if not other is None:
            B_json_frames, B_json_heap = other.get_json()
        A_json_frames, A_json_heap = self.get_json()
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
       
    
    def grade_byframe(self, other = None, B_json_frames = None, B_json_heap = None):
        """
        grades in a way that partial credit is assigned per correct frame
        """
        total_extraframes = 0
        total_framecount = 0
        total_correctframes = 0
        if not other is None:
            B_json_frames, B_json_heap = other.get_json()
        A_json_frames, A_json_heap = self.get_json()
        print("Aframes", A_json_frames)
        print("Bframes", B_json_frames)
        # Associates the pointer in A to the pointer in B.
        A_to_B_pointer_dict = {}
        # sets the indices of all frames in the other json to be yet to be checked
        for framekey in A_json_frames:
            # the amount of matches found for frames matching framekey
            correctframes = 0
            if framekey not in B_json_frames:
                framestomatch = []
            else:
                framestomatch = [True]*len(B_json_frames[framekey])
                # get each frame with the same framename in A and find a match in B
                for a in range(len(A_json_frames[framekey])):
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
                            # adds to the amount of frames the student has gotten correct.
                            correctframes += 1
                            break
                    
            # counts all frames left in B that have not been matched.
            extraframes = max(0, sum(framestomatch) - (len(A_json_frames[framekey]) - correctframes))
            total_extraframes += extraframes
            # adds to the total correct frames
            total_correctframes += correctframes
            # adds to the total count of frames in the correct version
            total_framecount += len(A_json_frames[framekey])

        # counts other frames that occur in B but not in A
        for framekey in list(set(B_json_frames) - set(A_json_frames)):
            total_extraframes += len(B_json_frames[framekey])

        print("total extra", total_extraframes)
        print("total correct", total_correctframes)
        print("total framecount", total_framecount)
        return max(0, total_correctframes/total_framecount - total_extraframes/(total_framecount + total_extraframes))
        
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

example_meow = """
# TEST: meow
def glob_meow():
    print('in global')
    def A_meow():

        # this is a test message
        z = 5
        return z
    A_meow()

glob_meow()"""

example_simple = """
x = 5
def f():
    return 5
y = 6
"""

example_intsonly = """
x = 5
y = 6
def f():
    x = 10
    z = 20
    return 5
f()
"""

example_intsonly2 = """
y = 6
x = 5
def f():
    x = 10
    z = 20
    return 5
f()
"""

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

student_input2 = {
    "heap": {
        "func": [
            {"name": "f", "parent": "Global", "funcIndex": "0", "nameWidth": 2},
            {"name": "g", "parent": "Global", "funcIndex": "1", "nameWidth": 2},
        ],
    },
    "frame": [
        {
            "var": [
                {
                    "val": "5",
                    "name": "x",
                    "valWidth": 2,
                    "varIndex": "1",
                    "nameWidth": 2,
                },
                {
                    "val": "6",
                    "name": "y",
                    "valWidth": 2,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {"val": "#heap-func-0", "name": "f", "varIndex": "2", "nameWidth": 2},
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

#print(convert_studentinput_to_json(student_input2))
intsonly_ft = FrameTree(example_intsonly)

B_frames, B_heap = convert_studentinput_to_json(student_input2)

print("grade all-or-nothing", intsonly_ft.grade_allornothing(B_json_frames= B_frames, B_json_heap=B_heap))

js = intsonly_ft.get_json()
print(js[0])
print(js[1])
