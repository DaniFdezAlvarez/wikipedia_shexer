from wikipedia_shexer.io.line_reader.base_line_reader import BaseLineReader

class FileLineReader(BaseLineReader):

    def __init__(self, source_file, skip_first_line=False):
        super().__init__(skip_first_line)
        self._source_file = source_file

    def read_lines(self):
        with open(self._source_file, "r", errors="ignore", encoding="utf-8") as in_stream:
            if self._skip_first_line:
                in_stream.readline()
            for a_line in in_stream:
                yield a_line