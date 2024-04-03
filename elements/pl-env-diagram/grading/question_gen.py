import random
import re

# built-in options for variable and function names
lowercase_letters = list("qwertyuiopasdfghjklzxcvbnm")
uppercase_letters = list("qwertyuiopasdfghjklzxcvbnm".upper())
common_variable_names = list("abxyz")
common_function_names = list("fgh")

# built-in options for generating variable values
small_int = lambda : random.randint(-15,99)
letter_str = lambda : random.choice(lowercase_letters + uppercase_letters)
digit_str = lambda : str(random.randint(0,9))

def generate_question(allowed_variable_names, allowed_function_names, allowed_assignment_values, code_string, code_filepath):
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
    for line in line_list:
        #print(line)
        split_line = line.split()
        print(split_line)
        if len(split_line) > 1 and split_line[1] == "=":
            print("in here")
            # TODO: make sure this is comprehensive 
            split_var = split_line[0].split([".", "(", "["])
            if split_var[0] in allowed_variable_names:
                new_variable_name = random.choice(allowed_variable_names[split_var[0]])
                line = re.sub(r'^\s+'+split_var[0], new_variable_name, line)
        elif len(split_line) > 0 and split_line[0] == "def":
            pass
    return "\n".join(line_list)
            

