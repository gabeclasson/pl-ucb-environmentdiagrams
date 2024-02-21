import prairielearn as pl

class Frame():
    is_global = False

    def __init__(self, parent=None, bindings=None):
        if parent is None:
            self.is_global = True
        self.parent = parent
        if bindings is None:
            self.bindings = {}
            
def generate(data):
    data["params"]["code"] = "x = 3"
    data["correct_answers"] = pl.to_json({"frame": "Global", "variables": {"x": 3}})
