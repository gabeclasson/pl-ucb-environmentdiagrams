import Qgen_simple
import os
import contextlib
def generate(data):
    with open(os.devnull, 'w') as devnull:
        with contextlib.redirect_stdout(devnull):
            data["params"]["codestring"] = Qgen_simple.generateQ(data['variant_seed'])
    return data
