import requests
import bs4



def _is_an_infobox(bsoup_element):
    return bsoup_element.name == "table" and \
           'class' in bsoup_element.attrs and \
           "infobox" in bsoup_element.attrs['class']


def _is_empty_paragraph(p_html):
    """
    There are empty paragraphs before starting the ones with content, labelled with a class mw-empty-elt

    :param p_html:
    :return:
    """
    if 'class' not in p_html.attrs:
        return False
    if 'mw-empty-elt' in p_html.attrs['class']:
        return True
    return False


def _remove_html_out_of_summary(html):
    """
    The assumption is that the received html contains a list of sorted elements., children of the main dic of content
    of the page. Once we find the first valid paragraph (a non-empty "p"), then the rest of the summary's paragraphs
    come in a row. The first element which is not a "p" after that, indicates the end of the summary.

    However, sometimes there is a paragraph before the abstract with specific pieces of information
    such as coordinates (information infobox-like). These pieces of information are placesbefore infoboxes, so
    the general case described before does not always apply

    :param html:
    :param page_title:
    :return:
    """
    paragraph_level_children = html.select("div.mw-parser-output > *")
    first_valid_paragraph = False
    result = []
    for child in paragraph_level_children:
        if child.name == "p" and not _is_empty_paragraph(child):
            first_valid_paragraph = True
        if first_valid_paragraph:
            if child.name != "p":
                if _is_an_infobox(child): # Special case
                    # Reset paragraphs. we wero not in the first valid ones, but rare
                    # exceptions placed before the infobox.
                    result = []
                    first_valid_paragraph = False
                else:  # End of abstract
                    break
            result.append(child)
    # return result
    new_html = bs4.BeautifulSoup('', 'html.parser')
    base_tag = new_html.new_tag("div")
    for a_p in result:
        base_tag.append(a_p)
    return base_tag



def html_text_of_an_url(url, just_summary):
    response = requests.get(url)
    if response is not None:
        html = bs4.BeautifulSoup(response.text, 'html.parser')
        main_content = html.select("#mw-content-text")[0]
        if not just_summary:
            return main_content
        else:
            return _remove_html_out_of_summary(main_content)

