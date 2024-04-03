import question_gen

# Provide possible options to rename variables with.

allowed_variable_names = {
    "a":question_gen.lowercase_letters + ["priscilla", "munchkin"], 
    "b":question_gen.lowercase_letters + ["precious", "munchkin"],
    "z":question_gen.common_variable_names + ["priscilla", "oreo"],}

# Provide possible options to rename functions with.

allowed_function_names = {
    "meow_mix":question_gen.common_function_names + ["meow_munch"], 
    "cat":question_gen.lowercase_letters + ["feline", "kitty"],
    }

# On lines where a variable assignment happens, you can provide different options for the value
# assigned. Indicate the line number, and the value options. Line numbers that correspond to 
# no variable assignment will be ignored. Variable assignments with no line number given will be
# left alone. 

# NOTE: question_gen.py counts the first line that isn't just whitespace as line 0. Comments count. Keep this in mind when indexing lines.

allowed_assignment_values = {
    1:[ "I love cats", "Cats are cool"],
    3:[question_gen.small_int],
    6:[question_gen.small_int],
    7:[question_gen.digit_str, question_gen.letter_str,], # this line will be ignored since line 7 is a return statement.
    }

# You can choose to input the problem's base code as a string,

code_string = """
def meow_mix():
    a = "I love cats"
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

result_code_string = question_gen.generate_question(allowed_variable_names, allowed_function_names, allowed_assignment_values, code_string, code_filepath)
print(result_code_string)