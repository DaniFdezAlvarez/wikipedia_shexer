from configparser import ConfigParser
import sys

def run(ini_file):
    parser = ConfigParser()
    parser.read(ini_file)


    print("Ontology file: {}".format(parser.get("ontology", "ontology_path")))
    print("Wikipedia dump file: {}".format(parser.get("wikipedia", "dump_path")))
    print("Important nodes file: {}".format(parser.get("targets", "nodes_path")))

    print("Dbepdia")
    print("Types: {}".format(parser.get("dbpedia", "types_path")))
    print("Wikilinks: {}".format(parser.get("dbpedia", "wikilinks_path")))

    dbp_dump_files = parser.get("dbpedia", "dump_path").split("|")
    print("Dump_files: {}".format(", ".join(dbp_dump_files)))


    print("Results will be outputed to: {}".format(parser.get("result", "result_path")))


if __name__ == "__main__":
    print("Input location: {}".format(sys.argv[0]))
    run(sys.argv[0])


