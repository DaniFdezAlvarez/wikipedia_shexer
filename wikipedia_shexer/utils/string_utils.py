import re

DOT_NUMBER = re.compile("[0-9]+\.[0-9]+")
ANY_NUMBER = "99"


def dot_numbers_to_any_number(text):
    return DOT_NUMBER.sub(ANY_NUMBER, text)