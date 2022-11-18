import itertools

from graphviz import Digraph
from pm4py.util import exec_utils, constants
from enum import Enum
import tempfile
import hashlib
from uuid import uuid4
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.objects.petri_net.obj import PetriNet, Marking


class Parameters(Enum):
    FORMAT = "format"
    BGCOLOR = "bgcolor"


def apply(dct_folded_nets, parameters=None):
    if parameters is None:
        parameters = {}

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, constants.DEFAULT_BGCOLOR)

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph("pt", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})
    viz.attr('node', shape='ellipse', fixedsize='false')

    otypes_color = {}
    for ot in dct_folded_nets:
        otypes_color[ot] = "#" + str(hashlib.md5(ot.encode("utf-8")).hexdigest())[-6:]

    matched_transitions = []
    matched_trans_labels = set()

    for ot in dct_folded_nets:
        net, im, fm = dct_folded_nets[ot]
        for trans in net.transitions:
            if trans.label not in matched_trans_labels:
                matched_transitions.append({ot: [(ot, trans)]})
                if trans.label is not None:
                    matched_trans_labels.add(trans.label)
                    for other_ot in dct_folded_nets:
                        net2, im2, fm2 = dct_folded_nets[other_ot]
                        for trans2 in net2.transitions:
                            if trans != trans2 and trans2.label == trans.label:
                                if other_ot not in matched_transitions[-1]:
                                    matched_transitions[-1][other_ot] = []
                                matched_transitions[-1][other_ot].append((other_ot, trans2))

    matched_transitions2 = []
    for i in range(len(matched_transitions)):
        all_values = itertools.product(*list(matched_transitions[i].values()))
        for tup in all_values:
            matched_transitions2.append(list(tup))

    matched_transitions_corr = {}
    for i in range(len(matched_transitions2)):
        for trans in matched_transitions2[i]:
            if trans[1] not in matched_transitions_corr:
                matched_transitions_corr[trans[1]] = set()
            matched_transitions_corr[trans[1]].add(i)

    nodes_uuids = [str(uuid4()) for i in range(len(matched_transitions2))]
    for i in range(len(matched_transitions2)):
        label = matched_transitions2[i][0][1].label
        if label is not None:
            viz.node(nodes_uuids[i], label, shape="box")
        else:
            viz.node(nodes_uuids[i], " ", shape="box", style="filled", fillcolor="black")

    added_places = {}

    for ot in dct_folded_nets:
        net, im, fm = dct_folded_nets[ot]
        this_color = otypes_color[ot]
        for place in net.places:
            added_places[place] = str(uuid4())
            label = " "
            if place in im:
                label = str(im[place])
            elif place in fm:
                label = "<&#9632;>"
            viz.node(added_places[place], label, shape="circle", style="filled", fillcolor=this_color)
        for arc in net.arcs:
            label = " "
            if hasattr(arc, "histogram"):
                label = str(arc.histogram).replace(", ", "\n")
            if isinstance(arc.source, PetriNet.Place):
                for i in matched_transitions_corr[arc.target]:
                    viz.edge(added_places[arc.source], nodes_uuids[i], label=label, color=this_color)
            else:
                for i in matched_transitions_corr[arc.source]:
                    viz.edge(nodes_uuids[i], added_places[arc.target], label=label, color=this_color)

    viz.attr(overlap='false')
    viz.attr(splines='false')
    viz.attr(rankdir='LR')
    viz.format = image_format

    return viz
