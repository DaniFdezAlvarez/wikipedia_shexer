from wikipedia_shexer.wshexer import WShexer
import spacy

VERB = "VERB"

# print(len(WShexer.sentence_aparittion_and_title_groups_of_each_wikilink('Madrid', just_summary=True)))

# print(WShexer.find_types_related_with_a_wikipedia_page('New_York_City', just_summary=True))
a_list = ['Washington,_D.C.', 'New_York_City']
result = WShexer.find_types_related_with_wikipedia_pages(a_list, just_summary=True)

counter = 0
for a_dict in result:
    print("-------------")
    print(a_list[counter])
    for a_key in a_dict:
        print(a_key, "|",a_dict[a_key])
    print("------------")

# print(0)
# mentions_and_stuff = WShexer.sentence_aparittion_and_title_groups_of_each_wikilink(a_list[0], just_summary=True)
# print(1)
# nlp = spacy.load("en_core_web_sm")
# print(2)
# for a_stuff in mentions_and_stuff:
#     text = a_stuff[0]
#     doc = nlp(text)
#     print("----")
#     print(a_stuff[1], "|", text)
#     for a_token in doc:
#         if a_token.pos_ == VERB:
#             print(a_token)
#     print("----")
