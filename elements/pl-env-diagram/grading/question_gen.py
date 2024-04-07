import random
import re
import signal
import json

# built-in options for generating variable and function names
lowercase_letters = lambda : random.choice(list("qwertyuiopasdfghjklzxcvbnm"))
uppercase_letters = lambda : random.choice(list("qwertyuiopasdfghjklzxcvbnm".upper()))
common_variable_names = lambda : random.choice(list("abxyz"))
common_function_names = lambda : random.choice(list("fgh"))

# built-in options for generating variable values
small_int = lambda : str(random.randint(-15,99))
letter_str = lambda : random.choice([lowercase_letters, uppercase_letters])().__repr__()
digit_str = lambda : str(random.randint(0,9)).__repr__()

def generate_question(allowed_names, allowed_assignment_values, special_replacements, code_string, code_filepath, seed):
    """ generates an environment diagram question using input from a setup file. """
    # Makes the generation time out if it takes too long.
    #if timeout:
    #    def timeout_handler(signum, frame):
    #        raise Exception("Question Generator took longer than ", timeout, " seconds to run. The most likely cause of this error is not enough options for variable names, or just very bad luck.")
    #    signal.signal(signal.SIGALRM, timeout_handler)
    #    signal.alarm(timeout)
    # Sets the random seed
    random.seed(seed)
    if code_string and code_filepath:
        print("""WARNING: User has provided both a code_string and a code_filepath. The code_string will be used. 
        If this is undesired, please replace the code_string variable with None.""")
    elif code_filepath:
        with open(code_filepath,"r") as file:
            code_string = file.read()
    line_list = code_string.split("\n")
    # Removes all whitespace at beginning of code and the end of the code
    while re.fullmatch("\s*", line_list[0]):
        del line_list[0]
    while re.fullmatch("\s*", line_list[-1]):
        del line_list[-1]
    # Do special replacements 
    line_list = replace_special(special_replacements, "\n".join(line_list)).split("\n")
    # Do value replacements
    line_list = replace_values(allowed_assignment_values, line_list)
    # Do namespace replacements
    line_list = replace_names(allowed_names, line_list)
    print(line_list)
    return "\n".join(line_list)

def replace_special(special_replacements, code_string):
    for key in special_replacements:
        special = random.choice(special_replacements[key])
        if callable(special):
            special = special()
        elif type(special) is list:
            special = random.choice(special)
        # Check that special is now a string. If not, throw an error.
        if type(special) != str:
            raise Exception("Expected special replacement in ", key, " to be string. Instead, it is ", type(special))
        code_string = code_string.replace(key, special)
    return code_string

def replace_values(allowed_assignment_values, line_list):
    for i in range(len(line_list)): 
        if "=" in line_list[i] and i in allowed_assignment_values:
            # Split the line at "=" signs.
            line = line_list[i].split('=')
            new_val =  random.choice(allowed_assignment_values[i])
            if callable(new_val):
                new_val = new_val()
            elif type(new_val) is list:
                new_val = random.choice(new_val)
            # Check that new_val is now a string. If not, throw an error.
            if type(new_val) != str:
                raise Exception("Expected new value on line ", str(i), " to be string. Instead, it is ", str(type(new_val)), ".\n This may have occured because you provided an option for a non-string to be chosen for this value. You still need to write all options as strings for them to be correctly processed. This includes adding other quotations outside of strings. Please see the comments on OPTIONS FOR VALUE ASSIGNMENT.")
            line_list[i] = line[0] + "= " + new_val
    return line_list
         
def replace_names(allowed_names, line_list):
    # generate all the replacement names
    newNames_dict = {}
    for key in allowed_names:
        new_name = None
        while new_name is None:
            new_name =  random.choice(allowed_names[key])
            if callable(new_name):
                new_name = new_name()
            elif type(new_name) is list:
                new_name = random.choice(new_name)
            # Check that new_name is now a string. If not, throw an error.
            if type(new_name) != str:
                raise Exception("Expected new name for variable or function ", key, " to be string. Instead, it is ", type(new_name))
            # if the new name has already been given to a different variable, we need a different value. 
            if new_name in newNames_dict.values():
                new_name = None
            else:
                newNames_dict[key] = new_name
    # modify all variable names in correspondence with what we've generated
    for i in range(len(line_list)):
        # This separates the line into non-string and string parts, so > a = b + "hello 'world' " + '' would become ['a = b + ', '"hello \'world\' " + '\'\''].
        line = line_list[i].split('(\"[^\"]*\"|\'[^\']*\')')
        # Now further split the line by splitting the line when any character occurs that could not appear in a variable name (not a letter, number, or underscore)
        split_line = []
        for part in line:
            split_line.extend(re.split('([^\w\d_]+)', part))
        for k in range(len(split_line)):
            # If this part of the line cannot be a variable/function name, skip it without modifying it. 
            if re.search('[^\w\d_]+', split_line[k]) is not None:
                continue
            if split_line[k] in newNames_dict:
                split_line[k] = newNames_dict[split_line[k]]
        line_list[i] = "".join(split_line)
    return line_list