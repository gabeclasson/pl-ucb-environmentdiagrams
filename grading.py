import sys
from collections import deque

class Tracer:
    def __init__(self):
        self.linenos = deque(maxlen=2)

    def trace(self, frame, event, arg):
        if event == 'line' and frame.f_code is not self.log.__code__:
            self.linenos.append(frame.f_lineno)
        return self.trace

    def log(self):
        print(self.linenos[0])

tracer = Tracer()
sys._getframe().f_trace = tracer.trace
sys.settrace(tracer.trace)

if True:
    assert True
else:
    pass
tracer.log()