from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.error import HTTPError
from time import sleep

from SPARQLWrapper.SPARQLExceptions import EndPointInternalError

_FAKE_USER_AGENT = "Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)"
_RESULTS_KEY = "results"
_BINDINGS_KEY = "bindings"
_VALUE_KEY = "value"

_XML_LANG_FIELD = "xml:lang"

def _add_lang_if_needed(result_dict):
    result = result_dict[_VALUE_KEY]
    if _XML_LANG_FIELD in result_dict:
        result += '"' + result + '"@' + result_dict[_XML_LANG_FIELD]
    return result


def query_endpoint_several_variables(endpoint_url, str_query, variables, max_retries=10, sleep_time=5, fake_user_agent=True):
    """
    I returns a dict with this format:
    {
        variables[0] : [ res_var0_0, res_var0_1 ... res_var0_n],
        variables[1] : [ res_var1_0, res_var1_1 ... res_var1_n],
        ...
        variables[m] : [ res_varM_0, res_varM_1 ... res_varM_n],
    }

    where n is the number of result rows for the query and m the number of variables.


    :param endpoint_url:
    :param str_query:
    :param variables:
    :param max_retries:
    :param sleep_time:
    :param fake_user_agent:
    :return:
    """
    first_failure = True
    sparql = SPARQLWrapper(endpoint_url)
    if fake_user_agent:
        sparql.agent = _FAKE_USER_AGENT
    sparql.setQuery(str_query)
    sparql.setReturnFormat(JSON)
    last_error = None
    while max_retries > 0:
        try:
            result_query = sparql.query().convert()
            result = {variable_id: [] for variable_id in variables}
            for row in result_query[_RESULTS_KEY][_BINDINGS_KEY]:
                for variable_id in variables:
                    result[variable_id].append(row[variable_id][_VALUE_KEY])
            return result
        except (HTTPError, EndPointInternalError) as e:
            max_retries -= 1
            sleep(sleep_time)
            last_error = e
            if first_failure and not fake_user_agent:
                sparql.agent = _FAKE_USER_AGENT
                first_failure = not first_failure
    last_error.msg = "Max number of attempts reached, it is not possible to perform the query. Msg:\n" + last_error.msg


def query_endpoint_single_variable(endpoint_url, str_query, variable_id, max_retries=10, sleep_time=5, fake_user_agent=True):
    """
    It receives an SPARQL query with a single variable and returns a list with the resulting nodes

    :param endpoint_url:
    :param str_query:
    :param variable_id:
    :return:
    """
    macro_result = query_endpoint_several_variables(endpoint_url=endpoint_url,
                                                    str_query=str_query,
                                                    variables=[variable_id],
                                                    max_retries=max_retries,
                                                    sleep_time=sleep_time,
                                                    fake_user_agent=fake_user_agent)
    return macro_result[variable_id]
    # first_failure = True
    # sparql = SPARQLWrapper(endpoint_url)
    # if fake_user_agent:
    #     sparql.agent = _FAKE_USER_AGENT
    # sparql.setQuery(str_query)
    # sparql.setReturnFormat(JSON)
    # last_error = None
    # while max_retries > 0:
    #     try:
    #         result_query = sparql.query().convert()
    #         result = []
    #         for row in result_query[_RESULTS_KEY][_BINDINGS_KEY]:
    #             result.append(row[variable_id][_VALUE_KEY])
    #         return result
    #     except (HTTPError, EndPointInternalError) as e:
    #         max_retries -= 1
    #         sleep(sleep_time)
    #         last_error = e
    #         if first_failure and not fake_user_agent:
    #             sparql.agent = _FAKE_USER_AGENT
    #             first_failure = not first_failure
    # last_error.msg = "Max number of attempts reached, it is not possible to perform the query. Msg:\n" + last_error.msg


def query_endpoint_po_of_an_s(endpoint_url, str_query, p_id, o_id, max_retries=5, sleep_time=2, fake_user_agent=True):
    first_failure = True
    sparql = SPARQLWrapper(endpoint_url)
    if fake_user_agent:
        sparql.agent = _FAKE_USER_AGENT
    sparql.setQuery(str_query)
    sparql.setReturnFormat(JSON)
    last_error = None
    while max_retries > 0:
        try:
            result_query = sparql.query().convert()
            result = []
            for row in result_query[_RESULTS_KEY][_BINDINGS_KEY]:
                p_value = row[p_id][_VALUE_KEY]
                o_value = _add_lang_if_needed(row[o_id])
                result.append((p_value, o_value))
            return result
        except (HTTPError, EndPointInternalError) as e:
            max_retries -= 1
            sleep(sleep_time)
            last_error = e
            if first_failure and not fake_user_agent:
                sparql.agent = _FAKE_USER_AGENT
                first_failure = not first_failure
    last_error.msg = "Max number of attempt reached, it is not possible to perform the query. Msg:\n" + last_error.msg