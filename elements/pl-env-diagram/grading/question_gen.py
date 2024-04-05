import random
import re

# built-in options for generating variable and function names
lowercase_letters = lambda : random.choice(list("qwertyuiopasdfghjklzxcvbnm"))
uppercase_letters = lambda : random.choice(list("qwertyuiopasdfghjklzxcvbnm".upper()))
common_variable_names = lambda : random.choice(list("abxyz"))
common_function_names = lambda : random.choice(list("fgh"))

# built-in options for generating variable values
small_int = lambda : random.randint(-15,99)
letter_str = lambda : random.choice(lowercase_letters + uppercase_letters)
digit_str = lambda : str(random.randint(0,9))

def generate_question(allowed_names, allowed_assignment_values, special_replacements, code_string, code_filepath):
    """ generates an environment diagram question using input from a setup file. """
    if code_string and code_filepath:
        raise Warning("""User has provided both a code_string and a code_filepath. The code_string will be used. 
        If this is undesired, please replace the code_string variable with None.""")
    elif code_filepath:
        with open(code_filepath,"r") as file:
            code_string = file.read()
    line_list = code_string.split("\n")
    # remove all whitespace at beginning of code
    while line_list[0] == "":
        del line_list[0]
    line_list = replace_names(allowed_names, line_list)
    return "\n".join(line_list)

def replace_special(special_replacements, line_list):
    pass

def replace_values(allowed_assignment_values, line_list):
    pass
         
def replace_names(allowed_names, line_list):
    # generate all the replacement names
    newNames_dict = {}
    for key in allowed_names:
        new_name =  random.choice(allowed_names[key])
        if callable(new_name):
            new_name = new_name()
        elif type(new_name) is list:
            new_name = random.choice(new_name)
        # Check that new_name is now a string. If not, throw an error.
        if type(new_name) != str:
            raise Exception("Expected new name for variable or function ", key, " to be string. Instead, it is ", type(new_name))
        newNames_dict[key] = new_name
    # modify all variable names in correspondence with what we've generated
    for i in range(len(line_list)):
        print("-------")
        # This separates the line into non-string and string parts, so > a = b + "hello 'world' " + '' would become ['a = b + ', '"hello \'world\' " + '\'\''].
        line = line_list[i].split('(\"[^\"]*\"|\'[^\']*\')')
        print(line)
        # Now further split the line by splitting the line when any character occurs that could not appear in a variable name (not a letter, number, or underscore)
        split_line = []
        for part in line:
            split_line.extend(re.split('([^\w\d_]+)', part))
        print(split_line)
        for k in range(len(split_line)):
            # If this part of the line cannot be a variable/function name, skip it without modifying it. 
            if re.search('[^\w\d_]+', split_line[k]) is not None:
                continue
            print(split_line[k])
            if split_line[k] in newNames_dict:
                split_line[k] = newNames_dict[split_line[k]]
        line_list[i] = "".join(split_line)
    return line_list
