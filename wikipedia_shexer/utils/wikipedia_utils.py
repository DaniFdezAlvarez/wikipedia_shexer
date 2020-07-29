import requests
import bs4
from wikipedia_shexer.utils.string_utils import dot_numbers_to_any_number


class WikipediaUtils(object):

    @staticmethod
    def html_text_of_a_page(title, just_summary):
        response = requests.get("https://en.wikipedia.org/wiki/" + title)
        if response is not None:
            html = bs4.BeautifulSoup(response.text, 'html.parser')
            main_content = html.select("#mw-content-text")[0]
            if not just_summary:
                return main_content
            else:
                return WikipediaUtils._remove_html_out_of_summary(main_content)

    @staticmethod
    def sentence_appearance_and_title_groups_of_each_wikilink(page_title, just_summary=False):
        result = []
        main_html = WikipediaUtils.html_text_of_a_page(page_title, just_summary)
        wiki_links = WikipediaUtils.wikilinks_in_html_content(main_html)
        for a_wiki_link in wiki_links:
            title = a_wiki_link.attrs['title'] if 'title' in a_wiki_link.attrs else None
            if title is not None:
                paragraph = WikipediaUtils._paragraph_for_a_wiki_link(main_html, a_wiki_link)
                if paragraph is not None:
                    paragraph = dot_numbers_to_any_number(paragraph)
                    sentences = WikipediaUtils._find_sentences_in_paragraph_for_a_wiki_link(paragraph, a_wiki_link)
                    for a_sentence in sentences:
                        result.append(
                            (a_sentence, a_wiki_link.text, title)
                        )
        return result

    @staticmethod
    def wikilinks_in_html_content(html):
        return [a_link for a_link in html.select("a") if WikipediaUtils._is_a_wikilink(a_link)]


    @staticmethod
    def _is_a_wikilink(bsoup_a):
        # 1 - The link contains a fererence
        # 2 - The reference is to a wikipedia page
        # 3 - There is enything deeper than "/wiki/"
        return 'href' in bsoup_a.attrs \
               and "/wiki/" in bsoup_a.attrs['href'] \
               and bsoup_a.attrs['href'].count("/") == 2

    @staticmethod
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
            if child.name == "p" and not WikipediaUtils._is_empty_paragraph(child):
                first_valid_paragraph = True
            if first_valid_paragraph:
                if child.name != "p":
                    if WikipediaUtils._is_an_infobox(child): # Special case
                        # Reset paragraphs. we wero not in the first valid ones, but rare
                        # exceptions placed before the infobox.
                        result = []
                        first_valid_paragraph = False
                    else: # End of abstract
                        break
                result.append(child)
        # return result
        new_html = bs4.BeautifulSoup('', 'html.parser')
        base_tag = new_html.new_tag("div")
        for a_p in result:
            base_tag.append(a_p)
        return base_tag

    @staticmethod
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



    @staticmethod
    def _is_an_infobox(bsoup_element):
        return bsoup_element.name == "table" and \
               'class' in bsoup_element.attrs and \
               "infobox" in bsoup_element.attrs['class']

    @staticmethod
    def _paragraph_for_a_wiki_link(html, wiki_link):
        selector = 'p:has(> a[href="' + wiki_link.attrs['href'] + '"])'
        paragraphs = html.select(selector)
        if len(paragraphs) == 1:
            return paragraphs[0].text
        else:
            return None

    @staticmethod
    def _find_sentences_in_paragraph_for_a_wiki_link(paragraph, a_wiki_link):
        sentences = paragraph.lower().split(".")
        target_text = a_wiki_link.text.lower()
        result = []
        for a_sentence in sentences:
            if target_text in a_sentence:
                result.append(a_sentence)
        return result