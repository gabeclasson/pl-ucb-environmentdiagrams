# TODO: move question_gen.py to elements/pl-env-diagram and figure out how to import it from there
try:
    import grading.question_gen as question_gen
except:
    import question_gen

######################################################################
######################### CUSTOM FUNCTIONS ###########################
######################################################################

# Here you can write your own functions for name/value/line generation. You cannot provide functions that take in a variable.

import random
listComprehensionSimple = lambda : random.choice(['lst.extend([' + str(random.randint(1, 10)) + '])', 'lst.append(' + str(random.randint(1, 10)) + ')', 'lst += [' + str(random.randint(1, 10)) + ']'])

######################################################################
###################### REPLACEMENT OPTIONS ###########################
######################################################################

# Below there are options for replacement of various parts of your default code. 
# Please note that replacement occurs in the following order:
# 1. Value replacements
# 2. Special replacements
# 3. Namespace replacements (replace the names of variables/functions)

# WARNING: it is possible to choose options that do not work and will not compile. 
# Please test any given problem a few times (not just generating the problem, but 
# also completing it) before releasing it to students.

######################################################################
################## OPTIONS FOR NAMESPACE REPLACEMENT #################
######################################################################

# Provide possible options to rename variables and functions with. You should provide all function/variable names here, even if you would like to leave them unchanged. The code will not necessarily err if you neglect to do this, but in some cases or on some seeds it might. This is because the question generation stage cannot detect all of the variables in the codestring unless you provide them, so it won't know if there are overlapping names.
# WARNING: If you do not provide enough options such that each variable can get a unique name, the question generator will time out. 
# WARNING 2: If you provide options for some variables but not for others, and it is possible for other variables to be given the same name as the unchanged variable(s),
# the code may err or you may just be testing students on a different kind of environment diagram in some cases. If you would like to leave a variable unchanged, just 
# provide the variable name and only itself as an option in the list, and it should go before randomizable variable names. For example, if you wanted to leave "f" unchanged, provide "f":["f"], and it should go first.

allowed_names = {
    # below are our variable names
    "a": [question_gen.lowercase_letters, ["priscilla", "munchkin"]], 
    "b": [question_gen.lowercase_letters, ["precious", "munchkin"]],
    "z": [question_gen.common_variable_names, "oreo"],
    "lst": ["my_list", "lst", "LIST", "list__"],
    # below are our function names
    "meow_mix": [question_gen.common_function_names, ["meow_munch"]], 
    "cat": [question_gen.lowercase_letters, ["feline", "kitty"]],}

######################################################################
############# OPTIONS FOR VALUE ASSIGNMENT REPLACEMENT ###############
######################################################################

# On lines where a variable assignment happens, you can provide different options for the value
# assigned. Indicate the line number, and the value options. Line numbers that correspond to 
# no variable assignment will be ignored. Variable assignments with no line number given will be
# left alone. 

# NOTE: question_gen.py counts the first line that isn't just whitespace as line 0. Comments count. Keep this in mind when indexing lines.

# NOTE: You must provide either functions that can be evaluated to create a value that is a string, a list of strings, or a string containing the value you want.
    # For example, if you wanted the value on line 3 to be the integer 5000, you would have to provide that as '5000'. See line 3 below. 
    # If you wanted the value on line 1 to be "Cats say meow", you would have to provide that as '"Cats say meow"' with additional outside quotations. See line 1 below.
    # If you want the new value to include the name of a variable, use the name in the default code. See the example in line 3 below. 

allowed_assignment_values = {
    1:[ '"I love cats"', '"Cats are cool"'],
    3:[question_gen.small_int, 'len(a)'],
    6:[question_gen.small_int],
    7:[question_gen.digit_str, question_gen.letter_str,], # this line will be ignored since line 8 is a return statement.
    }

######################################################################
##################### SPECIAL REPLACEMENT OPTIONS ####################
######################################################################

# If you would instead like to replace particular tags in your code with a set of options, you can use this dictionary. 
    # Tags should not appear in any way outside of the intended tags as these will use simple pythonic string substitution. We recommend naming your tags
    # with a sequence of characters that are unlikely to appear in normal code, like $5$.
    # This might be useful for segments of the code that you may want to replace that are not covered by variable name substitution or value assignment changes. 
    # For example, you could make it so that some randomized code includes a .extend statement while other includes a .append statement. 
    # Rules for formatting everything as strings applies. Read the comments on the above dictionary for explanation. 
# WARNING: If you use this feature, please try a few randomizations on your own to make sure it looks and grades how you expect it to. Small mistakes can cause the problem to not work as expected.

special_replacements = {
    '$1$': [listComprehensionSimple],
    '$2$': ['a'],
}

######################################################################
########################## INPUT BASE CODE ###########################
######################################################################

# You can choose to input the problem's base code as a string,

code_string = """ 
def meow_mix():
    a = "I love 'cats'"
    # cats are my favorite :3
    b = 6
    def cat(a):
        # I love cats
        z = 5
        return z + a
    lst = [cat(b)]
    $1$          
    lst.append($2$)
    return lst
meow_mix()""" 

# Or as a filepath (from question_gen.py). If you do both, the generator will prioritize the string. 

code_filepath = None #"meow.py"

######################################################################
############################ GENERATION ##############################
######################################################################

# DO NOT MODIFY THE BELOW LINE

generateQ = lambda seed : question_gen.generate_question(allowed_names, allowed_assignment_values, special_replacements, code_string, code_filepath, seed)

######################################################################
############################ TESTING #################################
######################################################################

# These lines show you a potential result of your problem. We recommend running this file a few times to see if it works how you expect before testing it on Prarielearn.  

if __name__ == "__main__":
    import random
    result_code_string = generateQ(seed = random.randint(0, 50))
    print(result_code_string)