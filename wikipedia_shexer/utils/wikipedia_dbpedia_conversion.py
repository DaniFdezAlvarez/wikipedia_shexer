from wikipedia_shexer.utils.const import DBPEDIA_EN_BASE, WIKIPEDIA_EN_BASE
import urllib.parse


def page_id_to_DBpedia_id(page_id):
    return DBPEDIA_EN_BASE + urllib.parse.unquote(page_id)


def dbpedia_id_to_page_title(dbpedia_id):
    return dbpedia_id[dbpedia_id.rfind("/" ) +1:]


def html_wikilink_to_dbpedia_id(html_wikilink):
    page_link = html_wikilink.attrs['href'] if 'href' in html_wikilink.attrs else None
    page_link = page_link.replace("/wiki/", "") if page_link is not None else None
    if page_link is not None:
        return page_id_to_DBpedia_id(page_link)
    return None

def html_wikilink_to_page_id(html_wikilink):
    page_link = html_wikilink.attrs['href'] if 'href' in html_wikilink.attrs else None
    page_link = page_link.replace("/wiki/", "") if page_link is not None else None
    return page_link

def page_title_to_wikilink_to_page_id(page_title):
    return page_title[:1].capitalize() + page_title.replace(" ", "_").strip()[1:]


def page_title_to_complete_url(page_title):
    return WIKIPEDIA_EN_BASE + page_title


