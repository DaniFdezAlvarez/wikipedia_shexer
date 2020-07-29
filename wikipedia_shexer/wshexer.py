import requests
import bs4
from wikipedia_shexer.utils.string_utils import dot_numbers_to_any_number
from wikidata.client import Client

WIKIDATA_CLIENT = Client()
P31_PROP = WIKIDATA_CLIENT.get('P31')
P279_PROP = WIKIDATA_CLIENT.get('P279')

API_WIKIPEDIA = "https://en.wikipedia.org/w/api.php?"


class WShexer(object):

    @staticmethod
    def find_type_for_wikidata_id(q_id):

        entity = WIKIDATA_CLIENT.get(q_id, load=True)
        q_type = entity[P31_PROP] if P31_PROP in entity else None
        q_class = entity[P279_PROP] if P279_PROP in entity else None
        en_label = q_type.attributes['labels']['en']['value'] if q_type is not None else None
        en_label = q_class.attributes['labels']['en']['value'] if q_class is not None and en_label is None else en_label
        return en_label

    @staticmethod
    def find_wikidata_id_for_a_page(title_page):
        params = {
            'action': 'query',
            'prop': 'pageprops',
            'titles': title_page,
            'format': 'json'
        }
        r = requests.get(API_WIKIPEDIA, params=params)
        result_query = r.json()['query']
        pages = result_query['pages'] if 'pages' in result_query else None

        if pages is None:
            return None

        page_id = None if len(pages) != 1 else list(pages.keys())[0]
        if page_id is None:
            return None
        return pages[page_id]['pageprops']['wikibase_item'] \
            if 'pageprops' in pages[page_id] and 'wikibase_item' in pages[page_id]['pageprops'] \
            else None

    @staticmethod
    def find_types_related_with_wikipedia_pages(pages, just_summary=False):
        result = []
        for a_page in pages:
            result.append(WShexer.find_types_related_with_a_wikipedia_page(page_title=a_page,
                                                                           just_summary=just_summary))
            # page_dict = WShexer.find_types_related_with_a_wikipedia_page(a_page)
            # for a_key in page_dict:
            #     if a_key not in result:
            #         result[a_key] = 0
            #     result[a_key] += page_dict[a_key]
        return result

    @staticmethod
    def find_types_related_with_a_wikipedia_page(page_title, just_summary=False):
        tuples = WShexer.sentence_aparittion_and_title_groups_of_each_wikilink(page_title=page_title,
                                                                               just_summary=just_summary)
        titles = set([a_tuple[2] for a_tuple in tuples])
        result = {}
        for a_title in titles:
            q_id = WShexer.find_wikidata_id_for_a_page(a_title)
            if q_id is None:
                print("Mecawen...", a_title)
            a_type = WShexer.find_type_for_wikidata_id(q_id) if q_id is not None else None
            if a_type is not None:
                print(a_title, a_type)
                if a_type not in result:
                    result[a_type] = 0
                result[a_type] += 1
            else:
                # print(a_title)
                pass
        return result

    @staticmethod
    def html_text_of_a_page(title, just_summary):
        response = requests.get("https://en.wikipedia.org/wiki/" + title)
        if response is not None:
            html = bs4.BeautifulSoup(response.text, 'html.parser')
            main_content = html.select("#mw-content-text")[0]
            if not just_summary:
                return main_content
            else:
                return WShexer._remove_html_out_of_summary(main_content)

    @staticmethod
    def sentence_aparittion_and_title_groups_of_each_wikilink(page_title, just_summary=False):
        result = []
        main_html = WShexer.html_text_of_a_page(page_title, just_summary)
        wiki_links = WShexer._wikilinks_in_html_content(main_html)
        for a_wiki_link in wiki_links:
            title = a_wiki_link.attrs['title'] if 'title' in a_wiki_link.attrs else None
            if title is not None:
                paragraph = WShexer._paragraph_for_a_wiki_link(main_html, a_wiki_link)
                if paragraph is not None:
                    paragraph = dot_numbers_to_any_number(paragraph)
                    sentences = WShexer._find_sentences_in_paragraph_for_a_wiki_link(paragraph, a_wiki_link)
                    for a_sentence in sentences:
                        result.append(
                            (a_sentence, a_wiki_link.text, title)
                        )
        return result

    @staticmethod
    def _remove_html_out_of_summary(html):
        """
        The asumption is that the received html contains a list of sorted elements., children of the main dic of content
        of the page. Once we find the first valid paragraph (a non-empty "p"), then the rest of the summary's paragraphs
        come in a row. The first element which is not a "p" after that, indicates the end of the summary.

        :param html:
        :param page_title:
        :return:
        """
        paragraph_level_children = html.select("div.mw-parser-output > *")
        first_valid_paragraph = False
        result = []
        for child in paragraph_level_children:
            if child.name == "p" and not WShexer._is_empty_paragraph(child):
                first_valid_paragraph = True
            if first_valid_paragraph:
                if child.name != "p":
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
    def _wikilinks_in_html_content(html):
        return [a_link for a_link in html.select("a") if 'href' in a_link.attrs and "/wiki/" in a_link.attrs['href']]

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
