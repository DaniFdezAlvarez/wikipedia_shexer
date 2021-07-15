class BaseLineReader(object):

    def __init__(self, skip_first_line=False):
        self._skip_first_line = skip_first_line

    def read_lines(self):
        raise NotImplementedError()