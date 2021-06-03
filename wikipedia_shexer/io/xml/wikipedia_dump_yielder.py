
_PAGE_NODE = "<page>"
_END_PAGE_NODE = "</page>"

class WikimediaDumpYielder(object):

    def __init__(self, source_file):
        self._source_file = source_file
        self._yielded = 0

    def yield_xml_nodes(self, limit=-1):
        with open(self._source_file, "r", encoding="utf-8") as in_stream:
            buffer = []
            for a_line in in_stream:
                a_line = a_line.strip()
                if a_line.startswith(_PAGE_NODE):
                    buffer = []
                    buffer.append(a_line)
                elif a_line.startswith(_END_PAGE_NODE):
                    buffer.append(a_line)
                    yield "\n".join(buffer)
                    self._yielded += 1
                    if self._yielded == limit:
                        break
                else:
                    buffer.append(a_line)

