import re
from wikipedia_shexer.utils.string_utils import dot_numbers_to_any_number, remove_brackets, text_to_sentences, \
    find_all, remove_dots_and_tags, remove_brackets_and_numbers
from wikipedia_shexer.model.wikipedia import Abstract, Sentence, Mention
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import html_wikilink_to_page_id, page_title_to_complete_url
from wikipedia_shexer.utils.dbpedia_utils import DBpediaUtils
from wikipedia_shexer.utils.html_utils import html_text_of_an_url

_HREF_NON_WIKILINK = re.compile("href=\"http.+?\"")
_PLACEHOLDER_HREF = "href=\"noreply\""


class WikipediaUtils(object):

    @staticmethod
    def html_text_of_a_page(title, just_summary):
        return html_text_of_an_url(url=page_title_to_complete_url(title),
                                   just_summary=just_summary)

    @staticmethod
    def sentence_appearance_and_title_groups_of_each_wikilink(page_title, just_summary=False):
        result = []
        main_html = WikipediaUtils.html_text_of_a_page(page_title, just_summary)
        wiki_links = WikipediaUtils.wikilinks_in_html_content(main_html)
        for a_wiki_link in wiki_links:
            title = a_wiki_link.attrs['title'] if 'title' in a_wiki_link.attrs else None
            if title is not None:
                html_paragraph = WikipediaUtils._html_paragraph_for_a_wiki_link(main_html, a_wiki_link)
                if html_paragraph is not None:
                    text_paragraph = WikipediaUtils._text_of_html_content(html_paragraph)
                    sentences = WikipediaUtils._find_sentences_in_paragraph_for_a_wiki_link(text_paragraph, a_wiki_link)
                    for a_sentence in sentences:
                        result.append(
                            (a_sentence, a_wiki_link.text, title)
                        )
        return result

    @staticmethod
    def has_mention_a_back_link(page_id, page_mention, just_summary):
        mention_html = WikipediaUtils.html_text_of_a_page(page_mention,just_summary=just_summary)
        wikilinks_in_mention = WikipediaUtils.wikilinks_in_html_content(mention_html)
        for a_wikilink in wikilinks_in_mention:
            if 'title' in a_wikilink.attrs:
                if a_wikilink.attrs['title'] == page_id:
                    return True
        return False


    @staticmethod
    def extract_model_abstract(page_id, inverse=True):
        abstract = WikipediaUtils._build_base_model_asbtract(page_id)
        abstract.fill_internal_numeric_values()
        DBpediaUtils.find_true_triples_in_an_abstract(abstract=abstract,
                                                      inverse=inverse,
                                                      attach=True)

        return abstract



    @staticmethod
    def wikilinks_in_html_content(html):
        return [a_link for a_link in html.select("a") if WikipediaUtils._is_a_wikilink(a_link)]


    @staticmethod
    def _build_base_model_asbtract(page_id):
        """
        It return an abctract model object with sentences and mentions, but not true triples.
        Iu just uses the knowledge available in the wikipedia asbtract targeted (no other
        APIs for any other task)

        :param page_id:
        :return:
        """
        main_html = WikipediaUtils.html_text_of_a_page(title=page_id,
                                                       just_summary=True)
        abstract_text = WikipediaUtils._text_of_html_content(main_html)
        result = Abstract(page_id=page_id, text=abstract_text)
        sentences = WikipediaUtils._model_sentences_in_html_content(html_content=main_html,
                                                                    text_content=abstract_text)
        for a_sentence in sentences:
            result.add_sentence(a_sentence)

        return result

    @staticmethod
    def _model_sentences_in_html_content(html_content, text_content):
        already_visited = set()
        text_sentences = text_to_sentences(text_content)
        lists_of_mentions = [[] for i in text_sentences]  # Bidimensional array, same length that text_sentences
        wikilinks_html = WikipediaUtils.wikilinks_in_html_content(html_content)
        for a_wiki_link in wikilinks_html:
            title = a_wiki_link.attrs['title'] if 'title' in a_wiki_link.attrs else None
            if title is not None and a_wiki_link.attrs['href'] not in already_visited:
                already_visited.add(a_wiki_link.attrs['href'])
                text_sentence = WikipediaUtils._find_text_sentence_of_a_wikilink(wiki_link=a_wiki_link,
                                                                                 html_container=html_content)
                for i in range(0,len(text_sentences)):
                    if text_sentences[i] == text_sentence:
                        lists_of_mentions[i].append(a_wiki_link)
                        break

        result = []
        for i in range(0,len(text_sentences)):
            curr_sentence = Sentence(text=text_sentences[i])
            for a_wiki_link in lists_of_mentions[i]:
                curr_sentence.add_mention(Mention(entity_id=html_wikilink_to_page_id(a_wiki_link),
                                                  text=a_wiki_link.text))
            result.append(curr_sentence)
        return result


    @staticmethod
    def _find_text_sentence_of_a_wikilink(wiki_link, html_container):
        html_paragraph = WikipediaUtils._html_paragraph_for_a_wiki_link(html=html_container, wiki_link=wiki_link)
        text_paragraph = WikipediaUtils._text_of_html_content(html_paragraph)
        if text_paragraph.count(wiki_link.text) == 1:
            return WikipediaUtils._find_sentence_of_a_text_mention(content=text_paragraph,
                                                                   mention=wiki_link.text)
        else:
            return WikipediaUtils._find_sentence_of_a_repeated_mention_in_a_paragraph(html_paragraph=html_paragraph,
                                                                                      wiki_link=wiki_link)

    @staticmethod
    def _find_sentence_of_a_repeated_mention_in_a_paragraph(html_paragraph, wiki_link):
        html_text = remove_brackets_and_numbers(WikipediaUtils._replace_every_non_wikilink_href(str(html_paragraph)))
        wiki_index = html_text.find(wiki_link.attrs['href'])
        dot_positions = find_all(pattern="\.", text=html_text)
        i = 0
        while i < len(dot_positions) and wiki_index > dot_positions[i]:
            i += 1
        first = dot_positions[i-1] if i > 0 else 0
        last = dot_positions[i] if i < len(dot_positions) else len(html_text) - 1
        return remove_dots_and_tags(html_text[first:last])


    @staticmethod
    def _replace_every_non_wikilink_href(html_text):
        return _HREF_NON_WIKILINK.sub(_PLACEHOLDER_HREF, html_text)

    @staticmethod
    def _find_sentence_of_a_text_mention(content, mention):
        sentences = text_to_sentences(content)
        for a_sentence in sentences:
            if mention in a_sentence:
                return a_sentence
        return None


    @staticmethod
    def _text_of_html_content(html_content):
        return dot_numbers_to_any_number(remove_brackets(html_content.text))


    @staticmethod
    def _is_a_wikilink(bsoup_a):
        # 1 - The link contains a fererence
        # 2 - The reference is to a wikipedia page
        # 3 - There is enything deeper than "/wiki/"
        return 'href' in bsoup_a.attrs \
               and "/wiki/" in bsoup_a.attrs['href'] \
               and bsoup_a.attrs['href'].count("/") == 2


    @staticmethod
    def _html_paragraph_for_a_wiki_link(html, wiki_link):
        selector = 'p:has( a[href="' + wiki_link.attrs['href'] + '"])'
        paragraphs = html.select(selector)
        if len(paragraphs) >= 1:
            return paragraphs[0]
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