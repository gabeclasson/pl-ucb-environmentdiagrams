import pickle
import inspect
import heapq
import frame
# i refer to this as "framenode" in some places. this is to avoid ambiguity. we will discuss changing the name.
Frame = frame.Frame

class Binding():
    def __init__(self, value):
        self.value = value
        self.referencees = set()
    
    def set_binding(self, framenode, bindingname):
        """ adds the binding to our list of references. Then assign ourself to the binding. """
        # not sure bindingname is necessary but better safe than sorry, and I can see some weird bugs happening if we leave it out. 
        self.referencees.add((framenode, bindingname))
        framenode.binding = self

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
        self.framename_dict = {}
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
            if name in self.framename_dict:
                self.framename_dict[name] = self.framename_dict[name] + 1
                name = name + str(self.framename_dict[name])
            else:
                self.framename_dict[name] = 0
            
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

        #code_list.insert(0, "envframes_dict = {'global':{}}")
        #code_list.insert(1, "fobj_framenode_dict = {}")
        #code_list.insert(2, "fobj_name_dict = {}")
        #code_list.insert(def_line + 1, ' '*whitespace + "print(fobj_framenode_dict)")
        #code_list.insert(0, "print('test glob', self.fobj_framenode_dict)")
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
                #code_list.insert(def_line + 1, ' '*whitespace + "print('test', self.fobj_framenode_dict)")
                #code_list.insert(def_line + 1, ' '*whitespace + "print('test', self.lastcreatedframe.parent)")
                code_list.insert(def_line + 1, ' '*whitespace + "self.add_newframe()") 
            i = i + 1
        #code_list.insert(i, "print('len in exec():',len(self.fobj_framenode_dict))")
        #code_list.insert(i, "print('end in exec():', self.fobj_framenode_dict)")
        self.codestring = str.join("\n", code_list)
        #print(self.codestring)
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
        #code_list.insert(exitline + 2, trk_var_names[2] + '=' "{var:(type(" + "globvar[var]), " + "globvar[var]) for var in " + "globvar" + "}")
        #code_list.insert(exitline + 1, trk_var_names[2] + '=' "{var:(type(" + "var" + "), " + "var" + ") for var in " + "globvar.values()" + "}")   
        #code_list.insert(exitline + 1, trk_var_names[2] + '=' "{var:(" + "var" + ") for var in " + "globvar" + "}")    
        #code_list.insert(exitline + 1, trk_var_names[2] + '=' "globvar")        
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
            #code_list.insert(i + 1, ' '*whitespace + "print('locals'," + trk_var_names[1] + ")")
            # store bindings at this point
            # TODO: 'var' might also be an issue here..
            
            #code_list.insert(i + 1, ' '*whitespace + trk_var_names[2] + '=' "{var:(type(" + trk_var_names[1] + "[var]), " + trk_var_names[1] + "[var]) for var in " + trk_var_names[1] + "}")
            code_list.insert(i + 2, ' '*whitespace + trk_var_names[2] + '=' + trk_var_names[1])
            code_list.insert(i + 3, ' '*whitespace + "frame" + '=' "self.fobj_framenode_dict[inspect.currentframe()]")
            # TODO: var names
            code_list.insert(i + 4, ' '*whitespace + "frame.bind(" + trk_var_names[2] + ")")

        #code_list.insert(len(code_list), "print('bindings', ft.lastcreatedframe.bindings)")

        # get modified code with Frame initialization
        newcode = str.join("\n", code_list)
        print(newcode)
        # THEN RUN EXEC(newcode), 
        exec(newcode, d, {})
        del self.root.bindings["globvar"]

    def get_simpletree(self):
        self.bindings_set = set()
        bindings_dict = self.simplify_node(self.root, {})
        self.bindings_set.update(bindings_dict.values())
        return self.root

    def simplify_node(self, framenode, bindings_dict):
        framenode.fobj = None
        framenode.name = None
        #new_bindings = {}
        #for bindingname in framenode.bindings:
            #b = framenode.bindings[bindingname]
            #if not id(b) in bindings_dict:
                #bindings_dict[id(b)] = Binding(b)
            #new_bindings[bindingname] = bindings_dict[id(b)]
            #new_bindings[bindingname].set_binding(framenode, bindingname)
        #framenode.bindings = new_bindings
        # TODO: make sure this tree recrusion is valid?
        for child in framenode.children:
            bindings_dict = self.simplify_node(child, bindings_dict)

        return bindings_dict
    
    # RIGHT NOW ONLY WORKS WITH INTEGER
    def makejson(self):
        # keeps track of how many of the same frame name exist
        frames_dict = {}
        # MOVE TO FRAMETREE DEF
        objname_dict = {"int":0, "func":0}
        heap_dict = {}
        mem_to_loc_dict = {}
        def addtojson(frame): # frames_dict, heap_dict, objname_dict
            newframe = {}
            frames_dict[frame.json_name] = newframe
            for varname in frame.bindings:
                if id(frame.bindings[varname]) in mem_to_loc_dict:
                    newframe[varname] = mem_to_loc_dict[id(frame.bindings[varname])]
                else:
                    # MOVE TO FRAMETREE DEF
                    match frame.bindings[varname]:
                        case int():
                            mem_to_loc_dict[id(frame.bindings[varname])] = "int-" + str(objname_dict["int"])
                            objname_dict["int"] = objname_dict["int"] + 1
                            heap_dict[mem_to_loc_dict[id(frame.bindings[varname])]] = frame.bindings[varname]
                        # NOT WORKING FOR FUNC CASE?
                        case _:
                            mem_to_loc_dict[id(frame.bindings[varname])] = "func-" + str(objname_dict["func"])
                            objname_dict["func"] = objname_dict["func"] + 1
                            # change so its more than just name, also parent frame
                            heap_dict[mem_to_loc_dict[id(frame.bindings[varname])]] = "function <" + str(frame.bindings[varname].__name__ + ">")
                        #case function():
                            # change to include function name: f_code.co_name
                        #    mem_to_loc_dict[id(frame.bindings[varname])] = "func-" + str(objname_dict["func"])
                        #    objname_dict["func"] = objname_dict["func"] + 1
                    newframe[varname] = mem_to_loc_dict[id(frame.bindings[varname])]
            for child in frame.children:
                addtojson(child)
        addtojson(self.root)
        return frames_dict, heap_dict
        

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

ft = FrameTree(example_intsonly)
#print("root:", ft.root)
ft.get_simpletree()
print(ft.root.bindings)
ft2 = FrameTree(example_meow)
ft2.get_simpletree()
#print(ft2.root.bindings)
#ftfr = ft.root.freeze()
#ftfr2 = ft2.root.freeze()
#print(ftfr.__hash__())
#print(ftfr2.__hash__())
#print(ft.root.freeze() == ft2.root.freeze())
json = ft.makejson()
print(json)
