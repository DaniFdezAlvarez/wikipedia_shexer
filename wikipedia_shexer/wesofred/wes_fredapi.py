import time
import shlex
import subprocess
from rdflib import Graph
from wikipedia_shexer.wesofred.key_limit_error import KeyLimitError

_MAX_PETITIONS = 7200
_MIN_TIME_BETWEEN_REQ = 15  # seconds


class WesFredApi(object):

    def __init__(self, api_key, petitions_already_performed=0,min_time_between=_MIN_TIME_BETWEEN_REQ):
        self._api_key = api_key
        self._petitions_in_day = petitions_already_performed
        self._time_between = min_time_between
        self._last_petition = time.time() - self._time_between  # So the first
                                   # query can be inmediatley performed

    def get_str_graph(self, text):
        return self._controlled_petition(text)

    def get_rdflib_graph(self, text):
        result = Graph()
        result.parse(data=self.get_str_graph(text), format="xml")
        return result

    @property
    def petitions_performed(self):
        return self._petitions_in_day

    def reset_petitions(self):
        self._petitions_in_day = 0

    def _update_petitions(self):
        self._petitions_in_day += 1

    def _perform_petition(self, text):
        try:
            result = subprocess.run(self._list_shell_command(text),
                                    stdout=subprocess.PIPE)
            return result.stdout.decode('utf-8')
            # result = subprocess.run(["echo", "hola"])
            # result = requests.get("http://wit.istc.cnr.it/stlab-tools/fred",
            #              data={
            #                  "text" : requests.utils.quote(text),
            #                  "semantic-subgraph" : True
            #              },
            #              headers={
            #                  "Authorization" : 'Bearer {}'.format(self._api_key),
            #                  "Accept" : 'application/rdf+xml'
            #              })
            # return result.text

        finally:
            self._last_petition = time.time()
        # return result.stdout.decode('utf-8')

    def _list_shell_command(self, sentence):
        # "curl -G -X " \
        # "GET -H " \
        # "\"Accept: application/rdf+xml\" " \
        # "-H \"Authorization: Bearer " + "KYe" + "\" " \
        # "--data-urlencode " \
        # "text=\"" + sentence + "\" " \
        # "-d semantic-subgraph=\"true\" " \
        # "http://wit.istc.cnr.it/stlab-tools/fred"
        # return ['curl',
        #         '-G',
        #         '-X',
        #         'GET',
        #         '-H',
        #         '"Accept: application/rdf+xml"',
        #         '-H',
        #         '"Authorization: Bearer {}"'.format(self._api_key),
        #         '--data-urlencode',
        #         'text="{}"'.format(sentence),
        #         '-d',
        #         'semantic-subgraph="true"',
        #         'http://wit.istc.cnr.it/stlab-tools/fred'
        #         ]
        cmd = "curl -G -X GET " \
              '-H "Accept: application/rdf+xml" ' \
              '-H "Authorization: Bearer ' + self._api_key + '"' +\
              ' --data-urlencode text="' + sentence+ '"' +\
              ' -d semantic-subgraph="true"' +\
              ' -d alignToFramester=true' + \
              ' -d wsd=true' + \
              ' -d alwaysmerge=true' + \
              ' -d roles=true' + \
              " http://wit.istc.cnr.it/stlab-tools/fred"
        return shlex.split(cmd)

    def _can_query_api(self):
        return self._petitions_in_day < _MAX_PETITIONS

    def _wait_needed_time(self):
        diff_time = time.time() -  self._last_petition
        if diff_time > self._time_between:
            return
        time.sleep(self._time_between - diff_time)

    def _controlled_petition(self, text):
        self._wait_needed_time()
        if not self._can_query_api():
            raise KeyLimitError("You can't perform more API requests today")
        try:
            self._update_petitions()
            return self._perform_petition(text)
        except BaseException as e:
            raise e
            # raise RuntimeError("API Error performing petition: {}".format(text))


    @staticmethod
    def preprocess_text(text):
        nt = text.replace("-", " ")
        nt = nt.replace("#", " ")
        nt = nt.replace(chr(96), "'")  # `->'
        nt = nt.replace("'nt ", " not ")
        nt = nt.replace("'ve ", " have ")
        nt = nt.replace(" what's ", " what is ")
        nt = nt.replace("What's ", "What is ")
        nt = nt.replace(" where's ", " where is ")
        nt = nt.replace("Where's ", "Where is ")
        nt = nt.replace(" how's ", " how is ")
        nt = nt.replace("How's ", "How is ")
        nt = nt.replace(" he's ", " he is ")
        nt = nt.replace(" she's ", " she is ")
        nt = nt.replace(" it's ", " it is ")
        nt = nt.replace("He's ", "He is ")
        nt = nt.replace("She's ", "She is ")
        nt = nt.replace("It's ", "It is ")
        nt = nt.replace("'d ", " had ")
        nt = nt.replace("'ll ", " will ")
        nt = nt.replace("'m ", " am ")
        nt = nt.replace(" ma'am ", " madam ")
        nt = nt.replace(" o'clock ", " of the clock ")
        nt = nt.replace(" 're ", " are ")
        nt = nt.replace(" y'all ", " you all ")

        nt = nt.strip()
        if nt[len(nt) - 1] != '.':
            nt = nt + "."

        return nt