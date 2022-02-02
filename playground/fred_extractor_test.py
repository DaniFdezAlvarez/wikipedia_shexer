from wikipedia_shexer.core.fred_triple_extractor import FredTripleExtractor
from playground.config import API_KEY

BASE = 51
wikipedia_dump_file = r"F:\datasets\enwiki-20210501-pages-articles-multistream.xml" \
                      r"\enwiki-20210501-pages-articles-multistream.xml"
titles_file = r"F:\datasets\fred\bands\all_band_titles.csv"
triples_out_file = r"F:\datasets\fred\bands\all_band_triples.nt"

print("Starting...")
extractor = FredTripleExtractor(api_key=API_KEY,
                                petitions_already_performed=BASE)
print("Extractor built! Going for the actual extraction...")
try:
    extractor.extract_triples_of_titles_file(titles_file=titles_file,
                                         triples_out_file=triples_out_file,
                                         wikipedia_dump_file=wikipedia_dump_file)
    print("Process finished without error!")
finally:
    print("Petitions performed: {}.".format(extractor.petitions_performed))
print("Done!")