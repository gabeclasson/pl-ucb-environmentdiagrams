import inspect
import heapq
try:
    import autoeval_frame as frame
except:
    import grading.autoeval_frame as frame
import os, contextlib
import re

# i refer to this as "framenode" in some places. this is to avoid ambiguity. we can discuss changing the name.
Frame = frame.Frame

class FrameTree():

    def __init__(self, codestring):
        # The "root" (aka Global) frame of the tree. Points to a Frame object.
        self.root = None
        # The amount of frames in our tree thusfar.
        self.framecounter = 0
        # Associates a frame object to a frame node (or in the case of global, at least for the time being, "global" to a frame node.) This is used to identify the parent frame of the frame being added.
        self.fobj_framenode_dict = {}
        # Associates id(function.__code__) to a parent frame. This is used so that we can identify the parent of each function for grading.
        self.codestrID_parent_dict = {}
        # Make sure the inputted code actually runs before generating the FrameTree
        try:
            exec(codestring, {}, {})
        except:
            raise Exception("Inputted codestring errs.")
        # Generate the FrameTree! 
        codestring = self.initialize_Frames(codestring)
        self.get_exitlines(codestring)
    
    def add_newFrame(self): 
        """ Adds a new Frame to the FrameTree. 
        """
        # Get the frame object of the frame being added. The current frame we are in is add_newFrame. We want the frame that called it.
        fobj = inspect.currentframe().f_back
        # If no Frames have been initialized yet, set the frame as the global frame and the root
        if self.framecounter == 0:
            name = "global"
            frame = Frame(name = name, fobj = fobj, index="Global")
            self.fobj_framenode_dict[fobj] = frame
            self.root = frame
        # If this frame is not the global frame, initialize as normal.
        else: 
            # Get the frame object of the parent frame. 
            parent_fobj = fobj.f_back
            # Get the Frame of the new Frame's parent. Sometimes Frames whose parent is global were called from some other Frame, so if we can't find their caller Frame we just say that their parent is global.
            parent = self.fobj_framenode_dict[parent_fobj] if parent_fobj in self.fobj_framenode_dict else self.root
            # The name of the Frame is the name of the function that it is calling. 
            name = fobj.f_code.co_name
            # Create the Frame with all of this information. Name it "f" + however many frames there are. 
            frame = Frame(name = name, parent = parent, fobj=fobj, index="f" + str(self.framecounter))
            # Add the new Frame to the frame object <--> Frame dict so children of this Frame are able to find it. 
            self.fobj_framenode_dict[fobj] = frame
            # Modify parent Frame to include the new Frame as a child
            parent.add_child(self.fobj_framenode_dict[fobj])
        # Increment the amount of Frames. 
        self.framecounter += 1
        return frame
    

    def get_environmentDiagram(self, codestring):
        """ Generates the 
        """
    def initialize_Frames(self, codestring):
        """This function adds a new line of code initializing the FrameNode in each function definition. 
        It then runs the modified code. We can later use all of the created FrameNodes to identify where to put
        listeners that will give us more information.
        
        I accomplish this by locating 'def' statements in the code and then initializing a new Frame in the line after.
        Then the code gets run in exec."""

        # Create a list of lines of code.
        code_list = codestring.split("\n")

        # Insert the line that will create the global Frame.
        code_list.insert(0, "self.add_newFrame()")
        # Insert lines that will create all non-global Frames by identifying ####
        i = 3 # TODO: modify to consider initalized vars // I am no longer sure what this means
        # Keep track of how much the current line has been shifted by (for example, if I am on what was line 2 but I added 3 lines before it, the shift is 3)
        shift = 0
        while i < len(code_list):
            # If the line contains a lambda, rewrite it as a def statement on the previous line so we can do frame tracking. 
            # THIS CURRENTLY DOES NOT WORK. REGEX IS DIFFICULT. 
            if False and re.search("lambda.*:", code_list[i]):
                def_line = i
                # Get size of whitespace before the line of code
                whitespace = len(code_list[i]) - len(code_list[i].lstrip(' '))
                # Split the line into parts that are not lambda statements and parts that are. 
                # More comprehensive search that includes = with lambda arguments: ((?![^\w\d_])lambda(\s*(((\s+(_?\w)+(\w*\d*_*)*(\s*=\s*(([^:,\n()\[\]{}\"'])*(\[.*\])*\9*(\{.*\})*\9*(\(.*\))*\9*(\".*\")*\9*('.*')*\7*)*)?\s*),\s*))*((_?\w)+(\w*\d*_*)*(\s*=\s*(([^:,\n()\[\]{}\"'])*(\[.*\])*\9*(\{.*\})*\9*(\(.*\))*\9*(\".*\")*\9*('.*')*\9*)*)?\s*)?)(:)(([^:,\n()\[\]{}\"'])*(\[.*\])*\28*(\{.*\})*\28*(\(.*\))*\28*(\".*\")*\28*('.*')*\28*)*)
                split_line = re.split("((?![^\w\d_])lambda(\s*(((\s+(_?\w)+(\w*\d*_*)*\s*),\s*)*(\s+(_?\w)+(\w*\d*_*)*\s*)\s+)?(:)(([^:,\n()\[\]{}\"'])*(\[.*\])*\13*(\{.*\})*\13*(\(.*\))*\13*(\".*\")*\13*('.*')*\13*)*))", code_list[i])
                # Technically its possible that there are multiple lambda statements on one line, so we have to loop through. 
                for k in range(len(split_line)):
                    if re.search("((?![^\w\d_])lambda(\s*(((\s+(_?\w)+(\w*\d*_*)*\s*),\s*)*(\s+(_?\w)+(\w*\d*_*)*\s*)\s+)?(:)))", split_line[k]):
                        # Split it to get the left side (lambda (args):) and the right side.
                        split_line[k] = re.split("((?![^\w\d_])lambda(\s*(((\s+(_?\w)+(\w*\d*_*)*\s*),\s*)*(\s+(_?\w)+(\w*\d*_*)*\s*)\s+)?(:)))", split_line[k])
                        print("test", split_line[k], re.split("(lambda)", split_line[k][0]))
                        arguments = re.split("(lambda)", split_line[k][0])[1][:-1]
                        code = split_line[k][1]
                        code_list.insert(i, ' '*whitespace + "def ghjk__lambda__line_" + str(i - shift) + "(" + arguments + "):") 
                        code_list.insert(i + 1, ' '*whitespace + '  ' + "return " + code)
                        i += 2
                        shift += 2
                        # Redefine this part of the line to be the name of the function lambda has been replaced with.
                        split_line[k] = "ghjk__lambda__line_" + str(i - shift)
                code_list[i] = "".join(split_line)   
                # set i back to def_line so it can get modified in the next if statement. 
                i = def_line

            if code_list[i].lstrip(' ')[:4] == "def ":
                def_line = i
                # find the indent size after the def
                whitespace = 0
                # The amount of whitespace indented after a def statement must be greater than 0, so we can continue while the whitespace is 0.
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
                code_list.insert(def_line + 1, ' '*whitespace + "self.add_newFrame()") 
                shift += 1

            i = i + 1
        codestring = str.join("\n", code_list)
        d =  {"self":self, "inspect":inspect}
        try:
            # These two 'with' statements silence the execution so no print statements are printed, which can bug out prarielearn. 
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stdout(devnull):
                    exec(codestring, d, {})
        except:
            raise Exception("Error evaluating the autogenerated code. Please contact an administrator.")    
        return codestring
    
    def get_exitlines(self, codestring):
        ### EXIT LINE TRACING ###
        # TODO: might get rid of: edits all FrameNodes to include a reference to which line it ends on (in the modified code)
        """edits all FrameNodes to include a reference to which line it ends on in .exitline. 
        Additionally returns a max heap of exit lines, and a dictionary mapping exit lines to Frame objects."""

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

        ### BINDING TRACKING ###

        # clear the dictionaries and frame counter
        self.fobj_framenode_dict = {}
        self.framecounter = 0
        self.root = None

        # keeps track of how many lines have been inserted above the 
        # if code is given as a string
        # TODO: REMOVE BELOW LINE(S) WHEN ALL CODE IS WORKING
        exitlines_pq = exitlines_pq.copy()
        code_list = codestring.split("\n")

        # TODO: fix to include correct variable names
        # set variable names for things we are using to store tracking info. (TODO: CHNAGE NAME GLOBVAR)
        trk_var_names = ["returnval", "locs", "bindings", "fobj_framenode_dict", "frame_name_dict"]
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
        code_list.insert(exitline + 3, "frame.bind(" + "globvar" + "," + "exclude =  ['frame']" + "," + "codestrID_parent_dict =  self.codestrID_parent_dict" + ")") # + "," + " frame"
        

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
        d =  {"self":self, "inspect":inspect}
        # then execute the code
        try:
            # These two 'with' statements silence the execution so no print statements are printed, which can bug out prarielearn. 
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stdout(devnull):
                    exec(newcode, d, {})
        except:
            raise Exception("Error evaluating the autogenerated code. Please contact an administrator.")    
        # TODO: Needed?
        del self.root.bindings["globvar"]
    
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
                        # Parent of the function is found by indexing the __code__ attribute into this dictionary
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

        def addFrameToJson(frame):
            newframe = {}
            newframe["var"] = []
            if frame.__name__ != "global":
                newframe["name"] = frame.__name__
                newframe["parent"] = str(frame.parent.index)
                # keep this line?
                newframe["return"] = None
                # may cause formatting issues, check this
                newframe["nameWidth"] = 2
            newframe["frameIndex"] = str(len(self.frames_list))
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
                addFrameToJson(child)
        addFrameToJson(self.root)
        return {"heap": self.heap_dict, "frame":self.frames_list}

testlambdacode = """
x = 5
f = lambda a: a + 5
f(7)
"""

ft = FrameTree(testlambdacode)