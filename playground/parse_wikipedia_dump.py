import re
from wikipedia_shexer.utils.dump_wikipedia_utils import DumpWikipediaUtils
from wikipedia_shexer.io.xml.wikipedia_dump_yielder import WikimediaDumpYielder


source_file = r"F:\datasets\enwiki-20210501-pages-articles-multistream.xml\enwiki-20210501-pages-articles-multistream.xml"

yielder = WikimediaDumpYielder(source_file=source_file)


_ANY_TAG = re.compile("<[a-zA-Z1-9]+( [^>]+)?>")

counter = 0
for a_node in yielder.yield_xml_nodes(limit=20000):
    counter += 1
    if counter % 500 == 0:
        print(counter)
    try:
        model = DumpWikipediaUtils.extract_model_abstract(xml_node=a_node)
        if model is not None:
            print("_________________")
            print("u" + model + "u")
    except ValueError as e:
        if str(e).startswith("Wrong input format. Template"):
            print("A case here!")
            print(str(e))
        elif str(e).startswith("Looks like there is"):
            print("A case of the otehr stuff here!")
            print(str(e))
        else:
            raise e




print("Done!")