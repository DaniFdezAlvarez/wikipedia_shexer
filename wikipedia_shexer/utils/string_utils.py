import re

DOT_NUMBER = re.compile("[0-9]+\.[0-9]+")
ANY_NUMBER = "99"

BRACKET_EXPRESSION = re.compile("\[.+?\]")

TAG = re.compile("<.+?>")
WHITES = re.compile("  +")
DOT = re.compile("\.")


def dot_numbers_to_any_number(text):
    return DOT_NUMBER.sub(ANY_NUMBER, text)

def remove_brackets(text):
    return BRACKET_EXPRESSION.sub("", text)

def remove_brackets_and_numbers(text):
    return dot_numbers_to_any_number(remove_brackets(text))

def text_to_sentences(text):
    return [elem.strip() for elem in text.split(".")]

def find_all(pattern, text):
    return [match.start() for match in re.finditer(pattern, text)]

def remove_dots_and_tags(text):
    text = TAG.sub(" ", text)  # tags
    text = DOT.sub(" ", text)  # dots
    text = WHITES.sub(" ", text) # too many consecutive whites
    return text.strip()

