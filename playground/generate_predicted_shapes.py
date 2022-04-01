from wikipedia_shexer.core.wikipedia_shape_extractor import WikipediaShapeExtractor
from sklearn import svm

def run():
    # triples_file = r"F:\datasets\300from200_triples_with_model.ttl"
    # training_rows_file = r"F:\datasets\300from200_row_features.csv"
    # typing_file = r"F:\datasets\instance-types_lang=en_specific.ttl"
    # ontology_file = r"F:\datasets\dbpedia_2021_07.owl"
    # wikilinks_file = r"F:\datasets\300from200_some_links.nt"
    # out_shapes_file = r"F:\datasets\300from200_shapes.nt"

    # triples_file = r"F:\datasets\some_bands_triples.ttl"
    # training_rows_file = r"F:\datasets\300from200_row_features.csv"
    # titles_file = r"F:\datasets\some_band_names.csv"
    # new_rows_file = r"F:\datasets\some_bands_candidate_features.csv"
    # typing_file = r"F:\datasets\instance-types_lang=en_specific.ttl"
    # # typing_file = r"F:\datasets\300from200_some_types.nt"
    # ontology_file = r"F:\datasets\dbpedia_2021_07.owl"
    # # wikilinks_file = r"F:\datasets\300from200_some_links.nt"
    # wikilinks_file = r"F:\datasets\wikilinks_lang=en.ttl"
    # out_shapes_file = r"F:\datasets\some_bands_shapes.shex"

    typing_file=r"F:\datasets\instance-types_lang=en_specific.ttl"
    ontology_file=r"F:\datasets\dbpedia_2021_07.owl"

    # new_rows_file = r"F:\datasets\clean300from200\300from200_all_candidate_features_CLEAN.csv"
    # triples_out_file = r"F:\datasets\clean300from200\300from200_all_triples_no_dumbs.ttl"
    # shapes_out_file = r"F:\datasets\clean300from200\300from200_all_shapes_no_dumbs.shex"
    # trainig_data_rows = r"F:\datasets\clean300from200\300from200_row_features.csv"

    # new_rows_file = r"F:\datasets\ontology_range_fixed\300from200_all_candidate_features_ontf_no_heads.csv"
    # triples_out_file = r"F:\datasets\ontology_range_fixed\sense_fixed\300from200_all_triples_0.ttl"
    # shapes_out_file = r"F:\datasets\ontology_range_fixed\sense_fixed\300from200_all_shapes_0.shex"

    trainig_data_rows = r"F:\datasets\clean300from200\300from200_row_features.csv"

    new_rows_file = r"F:\datasets\300from200_candidates_no_training_data_no_heads.csv"
    triples_out_file = r"F:\datasets\seitma_l\no_training\not_sliced\300from200_all_triples_no_training_0.ttl"
    shapes_out_file = r"F:\datasets\seitma_l\no_training\not_sliced\300from200_all_shapes_no_training_0.shex"



    print("ini!")
    t_sha = WikipediaShapeExtractor(typing_file=typing_file,
                                    wikilinks_file="No need, indeed",
                                    ontology_file=ontology_file,
                                    all_classes_mode=True)
    print("Built stuff!")
    t_sha.extract_shapes_of_rows(rows_file=new_rows_file,
                                 triples_out_file=triples_out_file,
                                 shapes_out_file=shapes_out_file,
                                 training_data_file=trainig_data_rows,
                                 callback=svm.SVC,
                                 include_typing_triples=True,
                                 shape_threshold=0)
    # t_sha.extract_shapes_of_titles_file(titles_file=titles_file,
    #                                     include_typing_triples=True,
    #                                     triples_out_file=triples_file,
    #                                     shapes_out_file=out_shapes_file,
    #                                     callback=svm.SVC,
    #                                     training_data_file=training_rows_file,
    #                                     rows_out_file=new_rows_file)

    print("Done!")

if __name__ == "__main__":
    run()
