
file_path = 'elements/pl-env-diagram/example_meow.py'

lowercase_letters = "qwertyuiopasdfghjklzxcvbnm".split()

allowed_variable_names = {"z":["x", "y", "z", "a", "b", "kitty", "feline", "fluffy"]}
allowed_variable_values = {}
 
with open(file_path, 'r') as file:
    file_content = file.read()
 
a = file_content
#print(a)
x="5"
print(x.__repr__())
print("'7'"=='"7"')
#f = sorted([{5:5}, {6:6}]) == sorted([{6:6}, {5:5}])
print([4,3,1,2,4,8][:-1])