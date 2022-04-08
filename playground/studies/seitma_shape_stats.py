import re
import os

_BLANKS = re.compile("  +")

_IGNORE = ["{", "}", ""]

_RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
_PREFIX_RDF_TYPE = "rdf:type"

_SPOS_CONSTS = 0
_SPOS_NAME = 1

_CONSTPOS_COMM = 0
_CONSTPOS_SENSE = 1
_CONSTPOS_CARD = 2
_CONSTPOS_NODE = 3

_COMMPOS_RATIO = 0
_COMMPOS_NODE = 1
_COMMPOS_CARD = 2

_CARD_OPT = "?"
_CARD_KLEENE = "*"
_CARD_POS = "+"
_MACRO_CARDS = [_CARD_OPT, _CARD_KLEENE, _CARD_POS]
_CARD_EXACT = "E"
_CARD_ONE = "1"

_NODE_IRI = "I"
_NODE_TYPE = "T"
_NODE_OTHER = "O"

_C_DIRECT = "d"
_C_INVERSE = "i"

_RATIO_RANGES = 5

class SeitmaShapeStats(object):

    def __init__(self):
        # PARSING

        self._shapes = []

        self._curr_comments = []
        self._curr_consts = []

        self._curr_const_sense = ""
        self._curr_const_card = ""
        self._curr_const_node = ""

        self._first_shape = True
        self._first_const_shape = True

        self._curr_s_name = ""

        #STATS

        #Grouped
        self._grouped_consts_ratios_pre = { i : 0 for i in range(_RATIO_RANGES, 101, _RATIO_RANGES)}
        self._grouped_comms_ratios_pre = { i: 0 for i in range(_RATIO_RANGES, 101, _RATIO_RANGES)}

        #Shape counts
        self._n_shapes_pre = 0

        #Const conunts
        self._n_consts_pre = 0
        self._max_consts_in_shape_pre = 0
        self._avg_consts_shape_pre = 0
        self._avg_ratio_consts_pre = 0
        self._iri_node_consts_pre = 0
        self._type_node_consts_pre = 0
        self._other_node_consts_pre = 0
        self._direct_consts_pre = 0
        self._indirect_consts_pre = 0
        self._kleene_consts_pre = 0
        self._pos_consts_pre = 0
        self._opt_consts_pre = 0
        self._one_consts_pre = 0
        self._exact_consts_pre = 0
        self._avg_const_ratio_per_shape_pre = 0

        #Comment counts
        self._n_comments_pre = 0
        self._avg_comments_per_shape_pre = 0
        self._avg_comments_per_const_pre = 0
        self._avg_ratio_comms_pre = 0
        self._iri_comms_pre = 0
        self._other_node_comms_pre = 0
        self._pos_card_comms_pre = 0
        self._one_card_comms_pre = 0
        self._exact_card_comms_pre = 0
        self._avg_ratio_comms_per_shape_pre = 0
        self._avg_ratio_comms_per_const_pre = 0



    def _store_current_s(self):
        if self._first_shape:
            self._first_shape = False
        else:
            self._shapes.append( (self._curr_consts,
                                  self._curr_s_name) ) # Tuple

    def _flush_last_shape(self):
        self._store_current_s()
        self._first_shape = True

    def _flush_last_const(self):
        self._store_current_const()
        self._reset_current_const()
        self._first_const_shape = True

    def _reset_shape(self, a_line):
        self._flush_last_const()
        self._curr_consts = []
        self._curr_s_name = a_line


    def _store_current_const(self):
        if self._first_const_shape:
            self._first_const_shape = False
        else:
            self._curr_consts.append( (
                self._curr_comments,
                self._curr_const_sense,
                self._curr_const_card,
                self._curr_const_node
            ) )

    def _reset_current_const(self):
        self._curr_comments = []

    def _annotate_curr_card(self, a_card):
        if a_card in _MACRO_CARDS:
            self._curr_const_card = a_card
        elif a_card == "":
            self._curr_const_card = _CARD_ONE
        else:  # JUST ONE OPTION LEFT: EXACT
            self._curr_const_card = _CARD_EXACT

    def _annotate_curr_node(self, a_node):
        self._curr_const_node = _NODE_OTHER if "@" in a_node else _NODE_IRI

    def _process_current_constraint_card_and_node(self, a_line):
        # print(a_line)
        if _RDF_TYPE in a_line or _PREFIX_RDF_TYPE in a_line:
            self._curr_const_node = _NODE_TYPE
            self._curr_const_card = _CARD_ONE
        else:
            a_line = a_line[:a_line.rfind("#")].strip() if a_line.endswith("%") else a_line
            a_line = a_line[:a_line.rfind(";")].strip() if ";" in a_line else a_line
            pieces = a_line.split(" ")
            inverse_offset = 1 if pieces[0] == "^" else 0
            self._annotate_curr_card(pieces[-1] if len(pieces) == 3 + inverse_offset else "")
            self._annotate_curr_node(a_line)

    def _process_new_indirect_constraint(self, a_line):
        self._curr_const_sense = _C_INVERSE
        self._process_current_constraint_card_and_node(a_line)

    def _process_new_direct_constraint(self, a_line):
        self._curr_const_sense = _C_DIRECT
        self._process_current_constraint_card_and_node(a_line)

    def _process_new_constraint(self, a_line):
        self._store_current_const()
        self._reset_current_const()

        if a_line.startswith("^"):
            self._process_new_indirect_constraint(a_line)
        else:
            self._process_new_direct_constraint(a_line)


    def _yield_file_lines(self, in_file, skip=2):
        with open(in_file, "r") as in_str:
            while skip != 0:
                in_str.readline()
                skip -=1
            for a_line in in_str:
                yield _BLANKS.sub(" ", a_line).strip()


    def _process_new_shape(self, a_line):
        self._store_current_s()
        self._reset_shape(a_line)

    def _card_in_brackets(self, target_str):
        if int(target_str[1:-1]) == 1:
            return _CARD_ONE
        else:
            return _CARD_EXACT


    def _process_comment_parts(self, a_line):
        ratio = float(a_line[1:a_line.find("%")].strip())
        node = _NODE_IRI if "@" not in a_line else _NODE_OTHER
        card = _CARD_POS if a_line.endswith(_CARD_POS) \
            else self._card_in_brackets(a_line[a_line.find("{"):])
        return ratio, node, card



    def _process_new_comment(self, a_line):
        ratio, node, card = self._process_comment_parts(a_line)
        self._curr_comments.append(
            (
                ratio, node, card
            )
        )


    def _profile_shapes(self, in_shapes_file, shape_init, skip=2):
        for a_line in self._yield_file_lines(in_file=in_shapes_file,
                                             skip=skip):
            if a_line.startswith(shape_init):
                self._process_new_shape(a_line)
            elif a_line.startswith("#"):
                self._process_new_comment(a_line)
            elif a_line in _IGNORE:
                pass
            else:
                self._process_new_constraint(a_line)
        self._flush_last_const()
        self._flush_last_shape()

    def _write_results(self, out_stats_file, results):
        if out_stats_file is None:
            print("\n".join(results))
        else:
            with open(out_stats_file, "w") as out_str:
                out_str.write("\n".join(results))

    def _count_consts(self):
        total = 0
        curr_max = 0

        acumm_ratios_per_shape = []

        ratio_consts_acumm = 0
        iri_node = 0
        type_node = 0

        direct_sense = 0

        pos_card = 0
        kleene_card = 0
        opt_card = 0
        one_card = 0

        for a_shape in self._shapes:
            curr_len = len(a_shape[_SPOS_CONSTS])
            total += curr_len
            if curr_len >= curr_max:
                curr_max = curr_len
                print("NEW MAX! {}, {}".format(curr_len, a_shape[_SPOS_NAME]))

            acumm_const_ratio_shape = 0

            for a_const in a_shape[_SPOS_CONSTS]:
                # ratio
                cons_ratio = a_const[_CONSTPOS_COMM][0][_COMMPOS_RATIO] \
                    if len(a_const[_CONSTPOS_COMM]) > 0 else 100.0
                ratio_consts_acumm += cons_ratio
                acumm_const_ratio_shape += cons_ratio

                # node
                if a_const[_CONSTPOS_NODE] == _NODE_IRI:
                    iri_node += 1
                elif a_const[_CONSTPOS_NODE] == _NODE_TYPE:
                    type_node += 1
                # sense
                if a_const[_CONSTPOS_SENSE] == _C_DIRECT:
                    direct_sense += 1
                # card
                if a_const[_CONSTPOS_CARD] == _CARD_POS:
                    pos_card += 1
                elif a_const[_CONSTPOS_CARD] == _CARD_KLEENE:
                    kleene_card += 1
                elif a_const[_CONSTPOS_CARD] == _CARD_ONE:
                    one_card += 1
                elif a_const[_CONSTPOS_CARD] == _CARD_OPT:
                    opt_card += 1
            if len(a_shape[_SPOS_CONSTS]) == 0:
                acumm_ratios_per_shape.append(0.0)
            else:
                acumm_ratios_per_shape.append(acumm_const_ratio_shape / len(a_shape[_SPOS_CONSTS]))


        self._n_consts_pre = total  ####
        self._max_consts_in_shape_pre = curr_max  ####
        self._avg_consts_shape_pre = self._n_consts_pre * 1.0 / self._n_shapes_pre  ####
        self._avg_ratio_consts_pre = ratio_consts_acumm / self._n_consts_pre  ####

        self._iri_node_consts_pre = iri_node  ####
        self._type_node_consts_pre = type_node  ####
        self._other_node_consts_pre = total - iri_node - type_node  ####

        self._direct_consts_pre = direct_sense  ####
        self._indirect_consts_pre = total - direct_sense  ####

        self._kleene_consts_pre = kleene_card  ####
        self._pos_consts_pre = pos_card  ####
        self._opt_consts_pre = opt_card  ####
        self._one_consts_pre = one_card  ####
        self._exact_consts_pre = total - pos_card - opt_card - one_card - kleene_card  ####

        self._avg_const_ratio_per_shape_pre = sum(acumm_ratios_per_shape) / self._n_shapes_pre  ####

    def _count_comments(self):
        total = 0
        ratio_comms_acumm = 0

        node_iri = 0

        pos_card = 0
        one_card = 0

        acumm_ratios_per_shape = []
        acumm_ratios_per_const = []

        for a_shape in self._shapes:
            acumm_shape_ratio = 0
            n_comms_shape = 0

            for a_const in a_shape[_SPOS_CONSTS]:
                total += len(a_const[_CONSTPOS_COMM])

                acumm_const_ratio = 0

                for a_comm in a_const[_CONSTPOS_COMM]:
                    n_comms_shape += 1
                    # ratio
                    ratio_comms_acumm += a_comm[_COMMPOS_RATIO]
                    acumm_shape_ratio += a_comm[_COMMPOS_RATIO]
                    acumm_const_ratio += a_comm[_COMMPOS_RATIO]

                    #node
                    if a_comm[_COMMPOS_NODE] == _NODE_IRI:
                        node_iri += 1

                    #card
                    if a_comm[_COMMPOS_CARD] == _CARD_POS:
                        pos_card += 1
                    elif a_comm[_COMMPOS_CARD] == _CARD_ONE:
                        one_card += 1

                acumm_ratios_per_const.append(
                    acumm_const_ratio / len(a_const[_CONSTPOS_COMM])
                    if  len(a_const[_CONSTPOS_COMM]) > 0
                    else 100.0
                )
            acumm_ratios_per_shape.append(
                acumm_shape_ratio / n_comms_shape if
                n_comms_shape > 0
                else 100.0
            )

        self._n_comments_pre = total  ####
        self._avg_comments_per_shape_pre = total * 1.0 / self._n_shapes_pre  ####
        self._avg_comments_per_const_pre = total * 1.0 / self._n_consts_pre  ####
        self._avg_ratio_comms_pre = ratio_comms_acumm / total  ####
        self._iri_comms_pre = node_iri  ####
        self._other_node_comms_pre = total - node_iri  ####
        self._pos_card_comms_pre = pos_card  ####
        self._one_card_comms_pre = one_card  ####
        self._exact_card_comms_pre = total - pos_card - one_card  ####
        self._avg_ratio_comms_per_shape_pre = sum(acumm_ratios_per_shape) / self._n_shapes_pre  ####
        self._avg_ratio_comms_per_const_pre = sum(acumm_ratios_per_const) / self._n_consts_pre  ####


    def _compute_devs(self):
        acumm_consts_per_shape = 0
        acumm_comms_per_shape = 0
        acumm_comms_per_const = 0

        for a_shape in self._shapes:
            acumm_consts_per_shape += abs(len(a_shape[_SPOS_CONSTS]) - self._avg_consts_shape_pre)
            shape_comms = 0
            for a_const in a_shape[_SPOS_CONSTS]:
                acumm_comms_per_const += abs(len(a_const[_CONSTPOS_COMM]) - self._avg_comments_per_const_pre)
                shape_comms += len(a_const[_CONSTPOS_COMM])
            acumm_comms_per_shape += abs(shape_comms - self._avg_comments_per_shape_pre)

        self._dev_consts_per_shape_pre = acumm_consts_per_shape / self._n_shapes_pre  ####
        self._dev_comms_per_shape_pre = acumm_comms_per_shape / self._n_shapes_pre  ####
        self._dev_comms_per_const_pre = acumm_comms_per_const / self._n_consts_pre  ####


    def _superior_bound_range(self, a_ratio):
        # rest = a_ratio / _RATIO_RANGES
        # rest5 = rest * _RATIO_RANGES
        # resfin = rest5 + _RATIO_RANGES
        # result =  int((a_ratio % _RATIO_RANGES) * _RATIO_RANGES + _RATIO_RANGES)

        low_bound = int(a_ratio / _RATIO_RANGES) * _RATIO_RANGES
        result = low_bound if low_bound == a_ratio else low_bound + _RATIO_RANGES
        return result

    def _group_ratios(self):
        for a_shape in self._shapes:
            for a_const in a_shape[_SPOS_CONSTS]:
                cons_ratio = a_const[_CONSTPOS_COMM][0][_COMMPOS_RATIO] \
                    if len(a_const[_CONSTPOS_COMM]) > 0 else 100.0
                self._grouped_consts_ratios_pre[self._superior_bound_range(cons_ratio)] += 1  ##
                for a_comm in a_const[_CONSTPOS_COMM]:
                    self._grouped_comms_ratios_pre[self._superior_bound_range(a_comm[_COMMPOS_RATIO])] += 1  ##

    def _stats_precom(self):
        self._n_shapes_pre = len(self._shapes) ####
        self._count_consts()
        self._count_comments()
        self._compute_devs()
        self._group_ratios()



    # "Ratios freq consts : {} ".format(self._ratios_freq_consts()),
    # "Ratios freq comms : {} ".format(self._ratios_freq_comms()),

    def _dev_comms_per_const(self):
        return self._dev_comms_per_const_pre

    def _dev_comms_per_shape(self):
        return self._dev_comms_per_shape_pre

    def _dev_consts_per_shape(self):
        return self._dev_consts_per_shape_pre

    def _avg_ratio_commts_per_const(self):
        return self._avg_ratio_comms_per_const_pre

    def _avg_ratio_commts_per_shape(self):
        return self._avg_ratio_comms_per_shape_pre

    def _avg_ratio_consts_per_shape(self):
        return self._avg_const_ratio_per_shape_pre

    def _n_shapes(self):
        return self._n_shapes_pre

    def _n_consts(self):
        return self._n_consts_pre

    def _n_comments(self):
        return self._n_comments_pre

    def _avg_consts_shape(self):
        return self._avg_consts_shape_pre

    def _avg_comments_shape(self):
        return self._avg_comments_per_shape_pre

    def _avg_comments_consts(self):
        return self._avg_comments_per_const_pre

    def _avg_ratio_consts(self):
        return self._avg_ratio_consts_pre

    def _avg_ratio_comms(self):
        return self._avg_ratio_comms_pre

    def _shape_most_consts(self):
        return self._max_consts_in_shape_pre

    def _iri_consts(self):
        return self._iri_node_consts_pre

    def _other_consts(self):
        return self._other_node_consts_pre

    def _type_consts(self):
        return self._type_node_consts_pre

    def _direct_consts(self):
        return self._direct_consts_pre

    def _inverse_consts(self):
        return self._indirect_consts_pre

    def _pos_consts(self):
        return self._pos_consts_pre

    def _kleene_consts(self):
        return self._kleene_consts_pre

    def _1_consts(self):
        return self._one_consts_pre

    def _opt_consts(self):
        return self._opt_consts_pre

    def _exact_consts(self):
        return self._exact_consts_pre

    def _iri_comms(self):
        return self._iri_comms_pre

    def _non_iri_comms(self):
        return self._other_node_comms_pre

    def _pos_comms(self):
        return self._pos_card_comms_pre

    def _1_comms(self):
        return self._one_card_comms_pre

    def _exact_comms(self):
        return self._exact_card_comms_pre

    def _ratios_freq_consts(self):
        l_ratios = [(key, value) for key,value in self._grouped_consts_ratios_pre.items()]
        l_ratios.sort(key=lambda x:x[0])
        l_ratios = ["{}-{}: {} \t {}".format(item[0]-_RATIO_RANGES,
                                             item[0],
                                             item[1],
                                             float(item[1])/self._n_consts_pre)
                    for item in l_ratios]
        return "\n" + "\n".join(l_ratios)

    def _ratios_freq_comms(self):
        l_ratios = [(key, value) for key, value in self._grouped_comms_ratios_pre.items()]
        l_ratios.sort(key=lambda x: x[0])
        l_ratios = ["({},{}]: {} \t {}".format(item[0] - _RATIO_RANGES,
                                             item[0],
                                             item[1],
                                             float(item[1]) / self._n_comments_pre)
                    for item in l_ratios]
        return "\n" + "\n".join(l_ratios)

    def _run_stats(self, out_stats_file):
        self._stats_precom()
        results = [
            "Number of shapes : {} ".format(self._n_shapes()),
            "Number of consts : {} ".format(self._n_consts()),
            "Number of comments: {} ".format(self._n_comments()),
            "Avg const per shape : {} ".format(self._avg_consts_shape()),
            "Avg comments per shape : {} ".format(self._avg_comments_shape()),
            "Avg comments per const : {} ".format(self._avg_comments_consts()),
            "Avg ratio consts : {} ".format(self._avg_ratio_consts()),
            "Avg ratio comms : {} ".format(self._avg_ratio_comms()),
            "Shape with more consts : {} ".format(self._shape_most_consts()),
            "IRI consts : {} ".format(self._iri_consts()),
            "OTHER consts : {} ".format(self._other_consts()),
            "TYPE consts : {} ".format(self._type_consts()),
            "Direct consts : {} ".format(self._direct_consts()),
            "Inverse consts : {} ".format(self._inverse_consts()),
            "+ consts : {} ".format(self._pos_consts()),
            "* consts : {} ".format(self._kleene_consts()),
            "1 consts : {} ".format(self._1_consts()),
            "? consts : {} ".format(self._opt_consts()),
            "exact consts : {} ".format(self._exact_consts()),
            "IRI comments : {} ".format(self._iri_comms()),
            "Non-IRI comments : {} ".format(self._non_iri_comms()),
            "+ comments : {} ".format(self._pos_comms()),
            "1 comments : {} ".format(self._1_comms()),
            "exact comments : {} ".format(self._exact_comms()),
            "Avg ratio consts per shape : {} ".format(self._avg_ratio_consts_per_shape()),
            "Avg ratio comms per shape : {} ".format(self._avg_ratio_commts_per_shape()),
            "Avg ratio comms per const : {} ".format(self._avg_ratio_commts_per_const()),
            "Dev const per shape : {} ".format(self._dev_consts_per_shape()),
            "Dev comms per shape : {} ".format(self._dev_comms_per_shape()),
            "Dev comms per const : {} ".format(self._dev_comms_per_const()),
            "Ratios freq consts : {} ".format(self._ratios_freq_consts()),
            "Ratios freq comms : {} ".format(self._ratios_freq_comms()),
        ]
        self._write_results(out_stats_file=out_stats_file,
                            results=results)


    def run(self, in_shapes_file, out_stats_file=None, shape_init=":", skip=2):
        self._profile_shapes(in_shapes_file=in_shapes_file,
                             shape_init=shape_init,
                             skip=skip)
        self._run_stats(out_stats_file)

class SeitmaFMultiShapeStats(SeitmaShapeStats):

    def __init__(self):
        super().__init__()

    def run(self, in_directory, out_stats_file=None, shape_init=":", skip=2):
        self._profile_shapes(in_directory=in_directory,
                             shape_init=shape_init,
                             skip=skip)
        self._run_stats(out_stats_file)

    def _yield_file_lines(self, in_directory, skip=2):

        for root, dirs, files in os.walk(in_directory):
            for name in files:
                if name.endswith(".shex"):
                    for a_line in super()._yield_file_lines(in_file=os.path.join(root,name),
                                                            skip=skip):
                        yield a_line


    def _profile_shapes(self, in_directory, shape_init, skip=2):
        for a_line in self._yield_file_lines(in_directory=in_directory,
                                             skip=skip):
            if a_line.startswith(shape_init):
                self._process_new_shape(a_line)
            elif a_line.startswith("#"):
                self._process_new_comment(a_line)
            elif a_line in _IGNORE:
                pass
            else:
                self._process_new_constraint(a_line)
        self._flush_last_const()
        self._flush_last_shape()


if __name__ == "__main__":
    # SeitmaShapeStats().run(in_shapes_file=r"F:\datasets\seitma_l\no_training\not_sliced\300from200_all_shapes_no_training_0.shex")
    # SeitmaShapeStats().run(
    #     in_shapes_file=r"C:\Users\Dani\repos-git\tomo\sup_material\seitma_data\seitma_f_target_shapes.shex",
    #     skip=15)

    SeitmaFMultiShapeStats().run(
        in_directory=r"F:\datasets\fred\shapes_extra_inverse",
        skip=15)



    print("Done!")