# encoding: utf-8

import re
import wikitextparser as wtp
import xml.etree.ElementTree as xmlp
from wikipedia_shexer.io.xml.wikipedia import WikipediaDumpYielder, WikipediaDumpYielderTitleFilter
from lxml import html

_TEMPLATE_PATTERN = re.compile("\{\{.+?\}\}")
_INI_TEMPLATE = re.compile("\{\{")
_END_TEMPLATE = re.compile("\}\}")
_FILE_PATTERN = re.compile("\[\[File:.+?\]\]")
_COMMENT = re.compile("\<!\-\-.*?\-\-\>")
_REDIRECTED_SEQUENCE = re.compile("#REDIRECT \[\[.+?\]\]", re.I)
# _REF_ELEM = re.compile("\<ref\>.*?</ref\>|\<ref\ .*?/\>")
_REF_ELEM = re.compile("<ref( [^>]+)?((/>)|(\>.*?</ref>))")
_MATH_ELEM = re.compile("<math( [^>]+)?((/>)|(\>.*?</math>))")
_CHEM_ELEM = re.compile("<chem( [^>]+)?((/>)|(\>.*?</chem>))")
_SUP_ELEM = re.compile("<sup( [^>]+)?((/>)|(\>.*?</sup>))")
_SUB_ELEM = re.compile("<sub( [^>]+)?((/>)|(\>.*?</sub>))")
_PRE_ELEM = re.compile("<pre( [^>]+)?((/>)|(\>.*?</pre>))")
_GALLERY_ELEM = re.compile("<gallery( [^>]+)?((/>)|(\>.*?</gallery>))")
_CODE_ELEM = re.compile("<code( [^>]+)?((/>)|(\>.*?</code>))")
_TIMELINE_ELEM = re.compile("<timeline( [^>]+)?((/>)|(\>.*?</timeline>))")

_INI_FILE_OR_IMAGE = re.compile("\[\[((File)|(Image)):")
_LINE_JUMPS = re.compile("\n+")
_INI_LANG = re.compile('lang(\-[a-z]+)?\|', re.I)
_TRANSL_TEMPLATE = re.compile("transl\|", re.I)
_EMPTY_BRACKETS = re.compile("\([^a-z]*\)", re.I)
_CONSECUTIVE_WHITES = re.compile("  +")
_CONSECUTIVE_QUOTES = re.compile("''+")

_ANY_TAG = re.compile("<[a-zA-Z1-9]+( [^>]+)?>")

_SQUARE_BRACKETS = ['[', ']']


# class DumpWikipediaUtils(object):

class WikipediaDumpExtractor(object):

    def __init__(self, source_file):
        self._source_file = source_file
        self._yielder = None
        self._success = 0
        self._empty = 0
        self._errors = 0

    def _yield_target_models(self, limit):
        for an_xml_node in self._yielder.yield_xml_nodes():
            try:
                a_model = self._extract_model_abstract_from_xml_node(an_xml_node)
                if a_model is None:
                    self._empty += 1
                else:
                    self._success += 1
                    yield a_model
                    if self._success == limit:
                        break
            except ValueError as e:
                self._errors += 1
                print(str(e))

    def extract_titles_model(self, list_of_titles):
        self._update_structures(targets=list_of_titles)
        for a_model in self._yield_target_models(limit=-1):
            yield a_model

    def extract_every_model(self, limit=-1):
        self._update_structures(targets=None)
        for a_model in self._yield_target_models(limit=limit):
            print("wee")
            yield a_model

    def extract_title_model(self, target_title):
        self._update_structures(targets=[target_title])
        for a_model in self._yield_target_models(limit=1):
            yield a_model

    def _extract_model_abstract_from_xml_node(self, xml_node):
        text_summary = self._extract_text_summary(xml_node)
        if text_summary is None:
            return None

    def _update_structures(self, targets):
        self._update_counts()
        self._update_yielder(targets)

    def _update_counts(self):
        self._success = 0
        self._empty = 0
        self._errors = 0

    def _update_yielder(self, targets):
        self._yielder = WikipediaDumpYielder(source_file=self._source_file) if targets is None \
            else WikipediaDumpYielderTitleFilter(source_file=self._source_file,
                                                 target_titles=targets)

    def _extract_text_summary(self, xml_node):
        root = xmlp.fromstring(xml_node)
        text_node = root.findall("./revision/text")
        if len(text_node) == 1:
            text = text_node[0].text
            if not WikipediaDumpExtractor._is_a_redirected_page(text):
                stuff = wtp.parse(text)
                res = WikipediaDumpExtractor._clean_text(str(stuff.sections[0]))
                return res
        else:
            raise ValueError("Check the structure of the following node (cant find any content): {}".format(xml_node))
        return None

    @staticmethod
    def _is_a_redirected_page(target_text):
        if target_text.startswith("#REDIRECT"):  # Works for most of the cases and its cheaper than using re
            return True
        return _REDIRECTED_SEQUENCE.search(target_text) is not None  # Double check, looking for redirection elsewhere

    @staticmethod
    def _clean_text(original_text):
        result = _LINE_JUMPS.sub(" ", original_text)
        result = _COMMENT.sub(" ", result)
        result = WikipediaDumpExtractor._clean_avoidable_tags(result)
        result = WikipediaDumpExtractor._clean_templates(result)
        result = WikipediaDumpExtractor._clean_files_and_images(result)
        result = _REF_ELEM.sub(" ", result)
        result = WikipediaDumpExtractor._clean_empty_brackets(result)
        result = WikipediaDumpExtractor._clean_consecutive_whites(result)
        result = WikipediaDumpExtractor._clean_consecutive_quotes(result)
        result = WikipediaDumpExtractor._clean_every_remaining_tag(result)
        result = result.strip()
        return result if result != "" else None

    @staticmethod
    def _clean_every_remaining_tag(original_text):
        return str(html.fromstring("<di>{}</div>".format(original_text)).text_content())

    @staticmethod
    def _clean_avoidable_tags(original_text):
        result = original_text
        result = _MATH_ELEM.sub(" ", result)
        result = _CHEM_ELEM.sub(" ", result)
        result = _SUB_ELEM.sub(" ", result)
        result = _SUP_ELEM.sub(" ", result)
        result = _PRE_ELEM.sub(" ", result)
        result = _GALLERY_ELEM.sub(" ", result)
        result = _CODE_ELEM.sub(" ", result)
        result = _TIMELINE_ELEM.sub(" ", result)

        return result

    @staticmethod
    def _clean_consecutive_whites(original_text):
        return _CONSECUTIVE_WHITES.sub(" ", original_text)

    @staticmethod
    def _clean_consecutive_quotes(original_text):
        return _CONSECUTIVE_QUOTES.sub(" ", original_text)

    @staticmethod
    def _clean_empty_brackets(original_text):
        return _EMPTY_BRACKETS.sub(" ", original_text)

    @staticmethod
    def _clean_templates(original_text):
        pairs = WikipediaDumpExtractor._find_template_index_pairs(original_text)
        useful_pairs = WikipediaDumpExtractor._find_useful_template_pairs(pairs, original_text)
        return WikipediaDumpExtractor._remove_templates_by_pairs(original_text, pairs,
                                                                 useful_pairs)  # _remove_content_by_index_pairs

    @staticmethod
    def _find_useful_template_pairs(pairs, original_text):
        result = []
        for a_pair in pairs:
            content = original_text[a_pair[0] + 2:a_pair[1]]  # + 2 --> len({{)
            if _INI_LANG.match(content) is not None:
                result.append(a_pair)
            elif _TRANSL_TEMPLATE.match(content) is not None:
                result.append(a_pair)
        return result

    @staticmethod
    def _clean_files_and_images(original_text):
        pairs = WikipediaDumpExtractor._find_files_index_pairs(original_text)
        return WikipediaDumpExtractor._remove_content_by_index_pairs(original_text, pairs)

    @staticmethod
    def _remove_templates_by_pairs(original_text, every_pair, useful_pairs, size_str_sequence=2):
        result = original_text
        for a_pair in reversed(every_pair):
            if a_pair not in useful_pairs:
                result = result[0:a_pair[0]] + result[a_pair[1] + size_str_sequence:]  #
            else:
                result = result[0:a_pair[0]] + \
                         WikipediaDumpExtractor._solve_content_of_special_template(
                             original_text[a_pair[0] + 2:a_pair[1]]) + \
                         result[a_pair[1] + size_str_sequence:]
        return result

    @staticmethod
    def _solve_content_of_special_template(template_text):  # Already without {{ and }}
        pieces = template_text.split("|")
        if _INI_LANG.match(template_text):
            if template_text[4] == "-":  # lang-.+ | TARGET
                return pieces[1].strip()
            else:  # lang | a_lang, such as 'en' | TARGET
                return pieces[2].strip()
        else:  # transl | TARGET
            return pieces[1].strip()

    @staticmethod
    def _remove_content_by_index_pairs(original_text, pairs, size_str_sequence=2):  # size of '}}' and ']]'
        result = original_text
        for i, e in reversed(pairs):
            result = result[0:i] + result[e + size_str_sequence:]  #
        return result

    @staticmethod
    def _find_files_index_pairs(original_text):
        pairs = []
        inis = [i.start() for i in _INI_FILE_OR_IMAGE.finditer(original_text)]
        for i in inis:
            pairs.append((i, WikipediaDumpExtractor._find_next_unnested_closing_bracket(original_text, i)))
        return pairs

    @staticmethod
    def _find_next_unnested_closing_bracket(target_str, current_ini):
        curr_nesting = 0
        e = WikipediaDumpExtractor._find_next_double_bracket(target_str=target_str,
                                                             init_index=current_ini + 2)
        while not (target_str[e] == "]" and curr_nesting == 0):
            if target_str[e] == "[":
                curr_nesting += 1
            else:  # target_str[e] == "]":
                curr_nesting -= 1
            e = WikipediaDumpExtractor._find_next_double_bracket(target_str=target_str,
                                                                 init_index=e + 2)
        return e

    @staticmethod
    def _find_next_double_bracket(target_str, init_index):
        for i in range(init_index, len(target_str)):
            if target_str[i] in _SQUARE_BRACKETS and i < len(target_str) - 1 and target_str[i] == target_str[i + 1]:
                return i
        raise ValueError("Looks like there is a malformed content here. a dobule square"
                         " bracket was expected at some point, but it didn't shown up.\n{}".format(target_str))

    @staticmethod
    def _find_template_index_pairs(original_text):
        inis = [i.start() for i in _INI_TEMPLATE.finditer(original_text)]
        ends = [i.start() for i in _END_TEMPLATE.finditer(original_text)]

        if len(inis) == 0:
            return []
        if len(inis) != len(ends):
            raise ValueError("Wrong input format. Template brackets does not match.\n{}".format(original_text))

        pairs = []
        i = e = 0
        current_ini_index = inis[i]
        current_nesting = 0
        while i < len(inis):
            if i == len(inis) - 1:  # A
                if current_nesting == 0:
                    pairs.append((current_ini_index, ends[i]))
                    i += 1
                else:
                    current_nesting -= 1
                    e += 1
            elif ends[e] < inis[i + 1]:  # B  --> Next close before next openning
                if current_nesting == 0:  # --> No nesting, match current pair
                    pairs.append((current_ini_index, ends[e]))
                    e += 1
                    i = e
                    current_ini_index = inis[i]
                else:  # C  # Nesting , then reduce nesting and wait next iter
                    current_nesting -= 1
                    e += 1
            else:  # ends[e] > inis[i+1]  # D  --> Next close after next opening, nesting
                current_nesting += 1
                # e += 1
                i += 1
        return pairs
