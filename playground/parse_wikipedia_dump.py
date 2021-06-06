
from wikipedia_shexer.utils.dump_wikipedia_utils import DumpWikipediaUtils
from wikipedia_shexer.io.xml.wikipedia_dump_yielder import WikimediaDumpYielder


source_file = r"F:\datasets\enwiki-20210501-pages-articles-multistream.xml\enwiki-20210501-pages-articles-multistream.xml"

yielder = WikimediaDumpYielder(source_file=source_file)

for a_node in yielder.yield_xml_nodes(limit=500):
    model = DumpWikipediaUtils.extract_model_abstract(xml_node=a_node)



print("Done!")