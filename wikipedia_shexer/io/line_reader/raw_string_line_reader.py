from wikipedia_shexer.io.line_reader.base_line_reader import BaseLineReader

class RawStringLineReader(BaseLineReader):

    def __init__(self, raw_string, skip_first_line=False):
        super().__init__(skip_first_line)
        self._raw_string = raw_string

    def read_lines(self):
        for a_line in self._raw_string.split("\n")[1 if self._skip_first_line else 0:]:
            if a_line.strip() != "":
                yield a_line
