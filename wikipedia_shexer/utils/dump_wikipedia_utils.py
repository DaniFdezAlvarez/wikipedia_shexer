# encoding: utf-8

import re
import wikitextparser as wtp
import xml.etree.ElementTree as xmlp

_TEMPLATE_PATTERN = re.compile("\{\{.+?\}\}")
_INI_TEMPLATE = re.compile("\{\{")
_END_TEMPLATE = re.compile("\}\}")
_FILE_PATTERN = re.compile("\[\[File:.+?\]\]")
_COMMENT = re.compile("\<!\-\-.*?\-\-\>")
_REDIRECTED_SEQUENCE = re.compile("#REDIRECT \[\[.+?\]\]")
# _REF_ELEM = re.compile("\<ref\>.*?</ref\>|\<ref\ .*?/\>")
_REF_ELEM = re.compile("<ref( [^>]+)?((/>)|(\>.*?</ref>))")
_INI_FILE_OR_IMAGE = re.compile("\[\[(File)|(Image):")
_LINE_JUMPS = re.compile("\n+")
_INI_LANG = re.compile('lang(\-[a-z]+)?\|', re.I)
_TRANSL_TEMPLATE = re.compile("transl", re.I)
_EMPTY_BRACKETS = re.compile("\([^a-z]*\)", re.I)
_CONSECUTIVE_WHITES = re.compile("  +")

# keep_templates = {
#     "(L|l)ang" : 2,
#     "(L|l)ang-*" : 1,
#     "transl" : 1,
# }

_SQUARE_BRACKETS = ['[', ']']

class DumpWikipediaUtils(object):

    @staticmethod
    def extract_model_abstract(xml_node):
        # pass
        root = xmlp.fromstring(xml_node)
        text_node = root.findall("./revision/text")
        if len(text_node) == 1:
            text = text_node[0].text
            if DumpWikipediaUtils._is_a_redirected_page(text):
                pass
            else:
                stuff = wtp.parse(text)
                print(DumpWikipediaUtils._clean_text(str(stuff.sections[0])))

                print("----------------------------------------------------")
        else:
            print("---------------------", len(text_node))


    @staticmethod
    def _is_a_redirected_page(target_text):
        if target_text.startswith("#REDIRECT"):  # Works for most of the cases and its cheaper than using re
            return True
        return _REDIRECTED_SEQUENCE.search(target_text) is not None  # Double check, looking for redirection elsewhere

    @staticmethod
    def _clean_text(original_text):
        result = _LINE_JUMPS.sub(" ", original_text)
        result = DumpWikipediaUtils._clean_files_and_images(result)
        result = _COMMENT.sub("", result)
        result = _REF_ELEM.sub("", result)
        result = DumpWikipediaUtils._clean_templates(result)
        result = DumpWikipediaUtils._clean_empty_brackets(result)  # TODO
        result = DumpWikipediaUtils._clean_consecutive_whites(result)  # TODO

        return result.strip()

    @staticmethod
    def _clean_consecutive_whites(original_text):
        return _CONSECUTIVE_WHITES.sub(" ", original_text)

    @staticmethod
    def _clean_empty_brackets(original_text):
       return _EMPTY_BRACKETS.sub(" ", original_text)

    @staticmethod
    def _clean_templates(original_text):
        pairs = DumpWikipediaUtils._find_template_index_pairs(original_text)
        useful_pairs = DumpWikipediaUtils._find_useful_template_pairs(pairs, original_text)
        return DumpWikipediaUtils._remove_templates_by_pairs(original_text, pairs, useful_pairs)  # _remove_content_by_index_pairs


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
        pairs = DumpWikipediaUtils._find_files_index_pairs(original_text)
        return DumpWikipediaUtils._remove_content_by_index_pairs(original_text, pairs)

    @staticmethod
    def _remove_templates_by_pairs(original_text, every_pair, useful_pairs, size_str_sequence=2):
        result = original_text
        for a_pair in reversed(every_pair):
            if a_pair not in useful_pairs:
                result = result[0:a_pair[0]] + result[a_pair[0] + size_str_sequence:]  #
            else:
                result = result[0:a_pair[0]] + \
                         DumpWikipediaUtils._solve_content_of_special_template(original_text[a_pair[0] + 2:a_pair[1]]) +\
                         result[a_pair[0] + size_str_sequence:]
        return result

    @staticmethod
    def _solve_content_of_special_template(template_text):  # Already without {{ and }}
        pieces = template_text.split("|")
        if _INI_LANG.match(template_text):
            if template_text[4] == "-":  # lang-.+ | TARGET
                return pieces[1].strip()
            else:  #  lang | a_lang, such as 'en' | TARGET
                return pieces[2].strip()
        else:  #  transl | TARGET
            return pieces[1].strip()

    @staticmethod
    def _remove_content_by_index_pairs(original_text, pairs, size_str_sequence=2):  # size of '}}' and ']]'
        result = original_text
        for i,e in reversed(pairs):
            result = result[0:i] + result[e+size_str_sequence:]  #
        return result

    @staticmethod
    def _find_files_index_pairs(original_text):
        pairs = []
        inis = [i.start() for i in _INI_FILE_OR_IMAGE.finditer(original_text)]
        for i in inis:
            pairs.append((i, DumpWikipediaUtils._find_next_unnested_closing_bracket(original_text, i)))
        return pairs

    @staticmethod
    def _find_next_unnested_closing_bracket(target_str, current_ini):
        curr_nesting = 0
        e = DumpWikipediaUtils._find_next_double_bracket(target_str=target_str,
                                                         init_index=current_ini + 2)
        while not (target_str[e] == "]" and curr_nesting == 0):
            if target_str[e] == "[":
                curr_nesting += 1
            else:  # target_str[e] == "]":
                curr_nesting -= 1
            e = DumpWikipediaUtils._find_next_double_bracket(target_str=target_str,
                                                             init_index=e+2)
        return e

    @staticmethod
    def _find_next_double_bracket(target_str, init_index):
        for i in range(init_index, len(target_str)):
            if target_str[i] in _SQUARE_BRACKETS and i < len(target_str) - 1 and target_str[i] == target_str[i+1]:
                return i
        raise ValueError("Looks like there is a malformed content here. a dobule square"
                         " bracket was expected at some point, but it didn't shown up")

    @staticmethod
    def _find_template_index_pairs(original_text):
        if "= Allan Dwan" in original_text:
            a = 2
        inis = [i.start() for i in _INI_TEMPLATE.finditer(original_text)]
        ends = [i.start() for i in _END_TEMPLATE.finditer(original_text)]

        if len(inis) != len(ends):
            raise ValueError("Wrong input format. Template brackets does not match")
        pairs = []
        i = e = 0
        current_ini_index = inis[i]
        current_nesting = 0
        while i < len(inis):
            if i == len(inis) - 1: # A
                if current_nesting == 0:
                    pairs.append((current_ini_index, ends[i]))
                    i += 1
                else:
                    current_nesting -= 1
                    e += 1
            elif ends[e] < inis[i + 1]: # B  --> Next close before next openning
                if current_nesting == 0:  # --> No nesting, match current pair
                    pairs.append((current_ini_index, ends[e]))
                    # print(original_text[current_ini_index:ends[e]])
                    e += 1
                    i = e
                    current_ini_index = inis[i]
                else: # C  # Nesting , then reduce nesting and wait next iter
                    current_nesting -= 1
                    e += 1
            else:  # ends[e] > inis[i+1]  # D  --> Next close after next opening, nesting
                current_nesting += 1
                # e += 1
                i += 1
        return pairs







