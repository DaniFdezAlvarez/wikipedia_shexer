import re
from wikipedia_shexer.utils.dump_wikipedia_utils import DumpWikipediaUtils
from wikipedia_shexer.io.xml.wikipedia_dump_yielder import WikimediaDumpYielder


source_file = r"F:\datasets\enwiki-20210501-pages-articles-multistream.xml\enwiki-20210501-pages-articles-multistream.xml"

yielder = WikimediaDumpYielder(source_file=source_file)


_ANY_TAG = re.compile("<[a-zA-Z1-9]+( [^>]+)?>")

tags = set()
for a_node in yielder.yield_xml_nodes(limit=20000):
    try:
        model = DumpWikipediaUtils.extract_model_abstract(xml_node=a_node)
        if model is not None:
            for a_match in _ANY_TAG.finditer(model):
                tags.add(a_match.group().split(" ")[0])
    except ValueError as e:
        if str(e).startswith("Wrong input format. Template"):
            print("A case here!")
        else:
            raise e
print(tags)




print("Done!")