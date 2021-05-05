
from wikipedia_shexer.io.line_reader.file_line_reader import FileLineReader
from wikipedia_shexer.io.line_reader.raw_string_line_reader import RawStringLineReader
from wikipedia_shexer.utils.obj_references import check_just_one_not_none

_S = 0
_P = 1
_O = 2


class BaseTriplesYielder(object):

    def __init__(self):
        pass

    def _decide_line_reader(self, raw_graph, source_file):
        check_just_one_not_none((source_file, "source_file"),
                                (raw_graph, "raw_graph"))
        if raw_graph is not None:
            return RawStringLineReader(raw_string=raw_graph)
        else:
            return FileLineReader(source_file=source_file)

    def yield_triples(self):
        raise NotImplementedError("Implement this method in derived classes")