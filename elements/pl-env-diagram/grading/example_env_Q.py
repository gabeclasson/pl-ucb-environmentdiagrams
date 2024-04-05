import question_gen
import random

# Here you can write your own functions for name/value/line generation.

listComprehensionSimple = lambda : random.choice('lst.extend([' + str(random.choice(10)) + '])', 'lst.append(' + str(random.choice(10)) + ')', 'lst + [' + str(random.choice(10)) + ']')

# Provide possible options to rename variables and functions with.

allowed_names = {
    # below are our variable names
    "a":question_gen.lowercase_letters + ["priscilla", "munchkin"], 
    "b":question_gen.lowercase_letters + ["precious", "munchkin"],
    "z":question_gen.common_variable_names + ["priscilla", "oreo"],
    # below are our function names
    "meow_mix":question_gen.common_function_names + ["meow_munch"], 
    "cat":question_gen.lowercase_letters + ["feline", "kitty"],}

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
    3:[question_gen.small_int, 'len(a)', '5000'],
    6:[question_gen.small_int],
    7:[question_gen.digit_str, question_gen.letter_str,], # this line will be ignored since line 7 is a return statement.
    }

# If you would instead like to replace particular tags in a code_string with a set of options, you can use this dictionary. 
# Tags should not appear in any way outside of the intended tags as these will use simple regex substitution. We recommend naming your tags
# with a sequence of characters that are unlikely to appear in normal code, like $5$.
# This might be useful for segments of the code that you may want to replace that are not covered by variable name substitution or value assignment changes. 
# For example, you could make it so that some randomized code includes a .extend statement while other includes a .append statement. 
# WARNING: If you use this feature, please try a few randomizations on your own to make sure it looks and grades how you expect it to. Small mistakes can cause the problem to not work as expected.
special_replacements = {
    '$1$': [listComprehensionSimple],
    '$2$': ['"Please be careful using this. READ THE COMMENTS ABOVE!"'],
}

# You can choose to input the problem's base code as a string,

code_string = """
def meow_mix():
    a = "I love 'cats'"
    print(a + "!!!!")
    b = 6
    def cat(a):
        # I love cats
        z = 5
        return z + a
    cat(b)

meow_mix()""" # if you don't want to use this option, replace it with None.

# Or as a filepath. If you do both, the generator will prioritize the string. 

code_filepath = None #"example_meow.py" # if you don't want to use this option, replace it with None.

# DO NOT MODIFY THE BELOW LINE

result_code_string = question_gen.generate_question(allowed_names, allowed_assignment_values, code_string, code_filepath)
print(result_code_string)