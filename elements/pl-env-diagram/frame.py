class Frame():
    is_global = False

    def __init__(self, parent=None, bindings=None):
        if parent is None:
            self.is_global = True
        self.parent = parent
        if bindings is None:
            self.bindings = {}