from wikipedia_shexer.utils.dbpedia_utils import DBpediaUtils


dbrs = DBpediaUtils.find_dbo_entities_in_wikipedia_page(page_id="Madrid",
                                                        just_summary=True)
print("---")
for a_dbr in dbrs:
    print(a_dbr)
    print(DBpediaUtils.get_types_of_a_dbpedia_node(a_dbr))

    # http: // dbpedia.org / resource / https: // en.wiktionary.orgmonocentric
    # http: // dbpedia.org / resource / Help: IPA / Spanish