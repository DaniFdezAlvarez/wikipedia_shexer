class _BaseCSVYielder(object):

    def __init__(self, line_yielder):
        self._line_yielder = line_yielder

    def yield_lines(self):
        raise NotImplementedError()

    def list_lines(self):
        return [a_line for a_line in self.yield_lines()]


class CSVBasicYielder(_BaseCSVYielder):

    def __init__(self, line_yielder):
        super().__init__(line_yielder)

    def yield_lines(self):
        for a_line in self._line_yielder.read_lines():
            a_line = a_line.strip()
            if a_line != "":
                yield a_line


class CSVYielderQuotesFilter(_BaseCSVYielder):

    def __init__(self, line_yielder):
        super().__init__(line_yielder)

    def yield_lines(self):
        for a_line in self._line_yielder.read_lines():
            if a_line.startswith('"'):
                a_line = a_line[1:]
            if a_line.endswith('"'):
                a_line = a_line[:-1]
            a_line = a_line.strip()
            if a_line != "":
                yield a_line
