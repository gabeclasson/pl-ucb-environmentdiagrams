
import inspect
import heapq # only used for second step of code modification with bindings tracking and in exitlines func

class Frame():
    # I, Noemi, will refer to this as a FrameNode for the time being to remove ambiguity with FrameObjects for the time being. 
    is_global = False
    exitline = None

    def __init__(self, name = None, bindings=None, parent=None, fobj=None):
        self.parent = parent
        self.children = set()
        if bindings is None:
            self.bindings = {}
        self.name = name
        # self's frame object
        self.fobj = fobj

    def bind(self, name, value):
        self.bindings[name] = value # Note: this will allow for duplicate entries. need to figure out a better way to do this. 
    
    def bind(self, name_value_dict):
        self.bindings = name_value_dict # Note: this will allow for duplicate entries. need to figure out a better way to do this. 
    
    def set_name(self, name):
        self.name = name
    
    def add_child(self, child):
        self.children.add(child)
    
    def set_exitline(self, exitline):
        self.exitline = exitline
    
    def __str__(self, level=0):
        ret = "\t"*level+repr(self.name)+"\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret

    def __repr__(self):
        return '<frame node representation>'


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

    def __init__(self, codestring):
        self.originalcodestring = codestring
        self.codestring = codestring
        # a dictionary containing frames with associated variables in the form of a tuple: (type, name, mem loc, value)
        self.envframes_dict = {}
        self.fobj_name_dict = {}
        # associates a frame object to a frame node (or in the case of global, at least for the time being, "global" to a frame node.)
        self.fobj_framenode_dict = {}
        self.env_mutables = {}
        self.insertFrameTracking()
    
    def add_new_frame(self, name = None): # func should always refer to the caller
        fobj = inspect.currentframe().f_back
        # if no frame nodes have been initialized, set the frame as the global frame and the root
        if len(self.fobj_framenode_dict.keys()) == 0:
            name = "global"
            frame = Frame(name = name, fobj = fobj)
            self.fobj_framenode_dict[fobj] = frame
            self.fobj_name_dict[fobj] = name
            self.root = frame
            # OLD
            self.envframes_dict[name] = {"name": None, "parent": None, "parent_fobj": None, "curr_fobj": fobj}

        else: 
            name = fobj.f_code.co_name
            f_name = "f" + name #temp TODO: add number
            parent_frame = fobj.f_back
            parent = self.fobj_framenode_dict[parent_frame] if parent_frame in self.fobj_framenode_dict else self.root
            
            # OLD: dictionary rep of frame associations. Use for debugging only. 
            self.envframes_dict[f_name] = {"name": name, "parent": parent, "parent_fobj": parent_frame, "curr_fobj": fobj}
            # init FrameNode
            frame = Frame(name = name, parent = parent, fobj=fobj)
            # add self to the pairing dict
            self.fobj_framenode_dict[fobj] = frame
            # modify parent to include self as a child
            parent.add_child(self.fobj_framenode_dict[fobj])
            # OLD: dictionary rep between fobj and frame
            self.fobj_name_dict[fobj] = name
            #print("test2: ", name, parent.name)
        self.lastcreatedframe = frame
    
    # TODO: do this for lambda as well
    def insertFrameTracking(self):
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
        code_list.insert(0, "self.add_new_frame()")
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
                code_list.insert(def_line + 1, ' '*whitespace + "self.add_new_frame()") 
            i = i + 1
        #code_list.insert(i, "print('len in exec():',len(self.fobj_framenode_dict))")
        #code_list.insert(i, "print('end in exec():', self.fobj_framenode_dict)")
        self.codestring = str.join("\n", code_list)
        #print(self.codestring)
        d =  {"self":self}#{"add_new_frame":self.add_new_frame, "self":self}
        exec(self.codestring, d, {})

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

ft = FrameTree(example_meow)
print("root:", ft.root)