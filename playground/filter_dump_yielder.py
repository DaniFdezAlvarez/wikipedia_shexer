from wikipedia_shexer.io.xml.wikipedia import WikimediaDumpYielderTitleFilter

source_file = r"F:\datasets\enwiki-20210501-pages-articles-multistream.xml\enwiki-20210501-pages-articles-multistream.xml"

targets = ["Albedo",
           "ASCII",
           "Arithmetic mean",
           "Algiers",
           "Auteur Theory Film",
           "Colossus computer",
           "Contraction mapping",
           "Professional certification",
           "Carl Menger",
           "Climate Change",
           "List of cartoonists",
           "Civilization",
           "Soldier, Iowa"
           ]

yielder = WikimediaDumpYielderTitleFilter(source_file=source_file, target_titles=targets)

counter = 0
for a_node in yielder.yield_xml_nodes(limit=20):
    counter += 1
    print("wee", counter)

print("Done!")