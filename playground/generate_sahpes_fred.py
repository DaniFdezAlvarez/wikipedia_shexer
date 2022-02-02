from wikipedia_shexer.core.fred_shape_extractor import FredShapeExtractor
from playground.config import API_KEY
from shexer.consts import SHEXC



def run(petitons_already_performed,
        titles_file,
        triples_out_file,
        shapes_out_file,
        wiki_dump_file,
        api_key):


    extractor = FredShapeExtractor(api_key=api_key,
                                   petitions_already_performed=petitons_already_performed,
                                   all_classes_mode=True)

    extractor.extract_shapes_of_titles_file(titles_file=titles_file,
                                            triples_out_file=triples_out_file,
                                            shapes_out_file=shapes_out_file,
                                            shapes_format=SHEXC,
                                            shape_threshold=0,
                                            wikipedia_dump_file=wiki_dump_file)
    print("Petitions performed up to now: {}.".format(extractor.petitions_performed))

if __name__ == "__main__":
    print("Starting complete pipeline of shape extraction...")

    BASE = 51
    wikipedia_dump_file = r"F:\datasets\enwiki-20210501-pages-articles-multistream.xml" \
                          r"\enwiki-20210501-pages-articles-multistream.xml"
    titles_file = r"F:\datasets\fred\bands\all_band_titles.csv"
    triples_out_file = r"F:\datasets\fred\bands\all_band_triples.nt"
    shapes_out_file = r"F:\datasets\fred\bands\all_band_shapes.shex"
    run(petitons_already_performed=BASE,
        titles_file=titles_file,
        triples_out_file=triples_out_file,
        shapes_out_file=shapes_out_file,
        wiki_dump_file=wikipedia_dump_file,
        api_key=API_KEY)
    print("Done!")