import pickle
import inspect
import heapq
import frame
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
            #print("test2: ", name, parent.name)
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

    def get_simpletree(self):
        self.bindings_set = set()
        bindings_dict = self.simplify_node(self.root, {})
        self.bindings_set.update(bindings_dict.values())
        return self.root
    
    # RIGHT NOW ONLY WORKS WITH INTEGER + FUNC
    def get_json(self):
        # keeps track of how many of the same frame name exist
        frames_dict = {}
        # TODO: MOVE TO FRAMETREE DEF
        objname_dict = {"int":0, "func":0}
        heap_dict = {}
        mem_to_loc_dict = {}
        def addtojson(frame): # frames_dict, heap_dict, objname_dict
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
                            mem_to_loc_dict[id(frame.bindings[varname])] = "int-" + str(objname_dict["int"])
                            objname_dict["int"] = objname_dict["int"] + 1
                            heap_dict[mem_to_loc_dict[id(frame.bindings[varname])]] = frame.bindings[varname]
                        # TODO: NOT WORKING FOR FUNC CASE?
                        case _:
                            mem_to_loc_dict[id(frame.bindings[varname])] = "func-" + str(objname_dict["func"])
                            objname_dict["func"] = objname_dict["func"] + 1
                            # change so its more than just name, also parent frame?
                            heap_dict[mem_to_loc_dict[id(frame.bindings[varname])]] = "function <" + str(frame.bindings[varname].__name__ + ">")
                    newframe[varname] = mem_to_loc_dict[id(frame.bindings[varname])]
            for child in frame.children:
                addtojson(child)
        addtojson(self.root)
        return frames_dict, heap_dict

    def equaljson(self, other = None, otherjson_frames = None, otherjson_heap = None, partial = None):
        sumgrade = 0
        extraframes = 0 
        total = 0
        if not other is None:
            otherjson_frames, otherjson_heap = other.get_json()
        myjson_frames, myjson_heap = self.get_json()
        self_other_pointer_dict = {}
        if myjson_frames.keys() != otherjson_frames.keys():
            if partial is None:
                return 0
        if myjson_heap.keys() != otherjson_heap.keys():
            if partial is None:
                return 0
        # get common frames between both groups
        # TODO: frame name is not really a concern - can be different between things?
        framekeys = set(myjson_frames).intersection(set(otherjson_frames))
        for frame in framekeys:
            if len(myjson_frames[frame]) != len(otherjson_frames[frame]):
                if partial is None:
                    print("amount of sub-frames not equal in ", frame)
                    return 0
            # sets the indices of all frames in the other json to be yet to be checked
            framestomatch = [True]*len(otherjson_frames[frame])
            for i in range(len(myjson_frames[frame])):
                found_match = False
                total += 1
                for j in range(len(otherjson_frames[frame])):
                    if not framestomatch[j]:
                        continue
                    is_match = True
                    # checks through each variable in the frame
                    variablekeys = set(myjson_frames[frame][i]).intersection(set(otherjson_frames[frame][j]))
                    for varname in variablekeys:
                        # if we have the pointer from the variable name already recorded, check to make sure the value in the pointer dict
                        # matches what we expect
                        if myjson_frames[frame][i][varname] in self_other_pointer_dict:
                            if otherjson_frames[frame][j][varname] != self_other_pointer_dict[myjson_frames[frame][i][varname]]:
                                print("not a match, variable pointers are mismatched")
                                is_match = False
                                break
                        else:
                            # set pointer matching
                            self_other_pointer_dict[myjson_frames[frame][i][varname]] = otherjson_frames[frame][j][varname]
                        if myjson_heap[myjson_frames[frame][i][varname]] != otherjson_heap[otherjson_frames[frame][j][varname]]:
                            print("not a match, variable values are not matched")
                            is_match = False
                            break 
                    if is_match:
                        found_match = True
                        framestomatch[j] = False
                        if partial == "byframe":
                            # adds grade by one frame
                            sumgrade += 1
                        break
                if not found_match:
                    if partial is None:
                        print("match not found for frame: ", frame)
                        return 0
            if partial == "byframe":
                # punishes student for extra frames
                sumgrade = sumgrade - sum(framestomatch)/len(framestomatch)
        if partial is None:
            return 1
        return sumgrade/total - max(len(otherjson_frames) - len(myjson_frames), 0)/len(otherjson_frames)
        

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

ft2 = FrameTree(example_simple)
#print("root:", ft.root)
ft = FrameTree(example_intsonly2)
#print(ft2.root.bindings)
#ftfr = ft.root.freeze()
#ftfr2 = ft2.root.freeze()
#print(ftfr.__hash__())
#print(ftfr2.__hash__())
#print(ft.root.freeze() == ft2.root.freeze())
json = ft.get_json()
print(json)
# not working with reverse currently
print(ft.equaljson(ft2, partial = "byframe"))