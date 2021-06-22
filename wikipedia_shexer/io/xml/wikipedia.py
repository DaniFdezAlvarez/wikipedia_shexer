
_PAGE_NODE = "<page>"
_END_PAGE_NODE = "</page>"

class WikimediaDumpYielder(object):

    def __init__(self, source_file):
        self._source_file = source_file
        self._yielded = 0
        self._tmp_limit = 0

    def yield_xml_nodes(self, limit=-1):
        self._tmp_limit = limit
        self._yielded = 0
        with open(self._source_file, "r", encoding="utf-8") as in_stream:
            buffer = []
            for a_line in in_stream:
                a_line = a_line.strip()
                if a_line.startswith(_PAGE_NODE):
                    buffer = []
                    buffer.append(a_line)
                elif a_line.startswith(_END_PAGE_NODE):
                    buffer.append(a_line)
                    if self._is_a_relevant_page(buffer):
                        yield "\n".join(buffer)
                        self._yielded += 1
                    if self._stop_condition_met():
                        break
                else:
                    buffer.append(a_line)

    def _is_a_relevant_page(self, buffer):
        return True

    def _stop_condition_met(self):
        return self._yielded == self._tmp_limit


_RELATIVE_POSITION_TITLE_LINE = 1
_FIRST_CHAR_TITLE_LINE = 7
_LAST_CHAR_TITLE_LINE = -8
class WikimediaDumpYielderTitleFilter(WikimediaDumpYielder):



    def __init__(self, source_file, target_titles):
        super().__init__(source_file)
        self._target_pages = set(target_titles) if type(target_titles) != set else target_titles


    def _is_a_relevant_page(self, buffer):
        return self._find_title_in_lines_list(buffer) in self._target_pages


    def _find_title_in_lines_list(self, buffer):
        """
        This works under some strong structural assumptions.

        1º: It recevies a buffer of lines which make together a valid xml node.
        2º: all the lines are stripped, i.e., there are no blanks at the begginign nor the end of the lines.
        3º: the second line of the buffer contains a <title> subnode.
        4º: the tags of the title subnode are written <title> and </title> respectively (no blanks, no attirbutes).
        5º: The actual title is placed between these tags, and it is already stripped w.r.t. the tags.

        :param buffer:
        :return:
        """
        return buffer[_RELATIVE_POSITION_TITLE_LINE][_FIRST_CHAR_TITLE_LINE:_LAST_CHAR_TITLE_LINE]

    def _stop_condition_met(self):
        return self._yielded == self._tmp_limit or self._yielded == len(self._target_pages)
