import sys
# caution: path[0] is reserved for script path (or '' in REPL)
#sys.path.insert(1, '/path/to/application/app/folder')

sys.path.append('../../')

import elements.pl_env_diagram.grading.autoeval as autoeval
import random

questionbank = ["""x = 5
y = 3 * x + 2"""]

answer = """
Global
    x 5
    y 17"""

def generate(data):
    ed = random.choice(questionbank)
    #g.undirect_matrix()
    #mat = g.matrix
    data["code"] = ed
    #data["params"]["matrix"] = pl.to_json(mat)
    data["correct_answers"] = answer