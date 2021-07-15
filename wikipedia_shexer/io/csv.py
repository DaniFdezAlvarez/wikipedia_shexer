class CSVSerializator(object):

    @staticmethod
    def _sort_list_of_lists(target, field_index):
        target.sort(reverse=True, key=lambda x: x[field_index])

    @staticmethod
    def _write_iterable_lists(out_file, iterable, sep=";", headers_list=None):
        with open(out_file, "w") as out_stream:
            if headers_list:
                out_stream.write(sep.join(headers_list) + "\n")
            for a_list in iterable:
                out_stream.write(sep.join([str(elem) for elem in a_list]) + "\n")

    @staticmethod
    def _write_iterable_strs(out_file, iterable, headers_line=None):
        with open(out_file, "w") as out_stream:
            if headers_line:
                out_stream.write(headers_line + "\n")
            for a_line in iterable:
                out_stream.write(a_line + "\n")

    @staticmethod
    def serlialize_generator_list(out_file, generator, sep=";", headers_list=None, ):
        CSVSerializator._write_iterable_lists(out_file=out_file,
                                              iterable=generator,
                                              sep=sep,
                                              headers_list=headers_list)

    @staticmethod
    def serialize_list_of_lists(out_file, list_of_lists, sep=";", sorting_field_index=None, headers_list=None):
        if sorting_field_index:
            CSVSerializator._sort_list_of_lists(target=list_of_lists,
                                                field_index=sorting_field_index)
        CSVSerializator._write_iterable_lists(out_file=out_file,
                                              iterable=list_of_lists,
                                              sep=sep,
                                              headers_list=headers_list)

    @staticmethod
    def serialize_generator_strs(out_file, generator_str, headers_line=None):
        CSVSerializator._write_iterable_strs(out_file=out_file,
                                             iterable=generator_str,
                                             headers_line=headers_line)

    @staticmethod
    def serialize_list_of_strs(out_file, list_of_strs, sep=";", sorting_field_index=None, headers_line=None):
        if sorting_field_index:
            for i in range(len(list_of_strs)):  # Turn str list into list of lists splittig by 'sep'
                list_of_strs[i] = list_of_strs[i].split(sep)
            CSVSerializator.serialize_list_of_lists(out_file=out_file,
                                                    list_of_lists=list_of_strs,
                                                    sep=sep,
                                                    sorting_field_index=sorting_field_index,
                                                    headers_list=headers_line.split(sep))
        else:
            CSVSerializator._write_iterable_strs(out_file=out_file,
                                                 iterable=list_of_strs,
                                                 headers_line=headers_line)


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
