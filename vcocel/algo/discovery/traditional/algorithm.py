import uuid

from pm4py.objects.log.obj import EventLog, Trace, Event
import pm4py
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import petri_utils
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.objects.log.util import filtering_utils


def __map_consecutive_activities_log(log, activity_key="concept:name"):
    new_log = EventLog()
    max_map = {}
    for trace in log:
        curr_act = None
        map_acti_count = {}
        new_trace = Trace()
        new_log.append(new_trace)
        trace_map = {}
        for event in trace:
            activity = event[activity_key]
            if activity != curr_act:
                curr_act = activity
                if activity not in map_acti_count:
                    map_acti_count[activity] = 1
                else:
                    map_acti_count[activity] += 1
                new_eve = Event({activity_key: activity+"@@"+str(map_acti_count[activity])})
                new_trace.append(new_eve)
                trace_map[activity+"@@"+str(map_acti_count[activity])] = 1
            else:
                trace_map[activity + "@@" + str(map_acti_count[activity])] += 1
        for el in trace_map:
            if not el in max_map:
                max_map[el] = trace_map[el]
            max_map[el] = max(max_map[el], trace_map[el])
    return new_log, max_map


def __add_tree_to_net(prefix_tree, max_map, net, coming_place, sink):
    max_cons = 1
    max_prod = 1
    exiting_place = coming_place
    for el in prefix_tree.children:
        max_cons = max(max_cons, max_map[el.label])
    if prefix_tree.label is not None:
        exiting_place = PetriNet.Place(str(uuid.uuid4()))
        net.places.add(exiting_place)
        max_prod = max_map[prefix_tree.label]
        for i in range(max_prod):
            for j in range(max_cons):
                activityy = prefix_tree.label.split("@@")[0]
                trans_name = prefix_tree.label.replace("@@", "##") + str(id(prefix_tree)) + "#@#"+str(i)+"#@#"+str(j)
                trans = PetriNet.Transition(trans_name, activityy)
                net.transitions.add(trans)
                petri_utils.add_arc_from_to(coming_place, trans, net, weight=i+1)
                petri_utils.add_arc_from_to(trans, exiting_place, net, weight=j+1)
    for el in prefix_tree.children:
        __add_tree_to_net(el, max_map, net, exiting_place, sink)
    for i in range(max_prod):
        trans = PetriNet.Transition(str(uuid.uuid4()), None)
        net.transitions.add(trans)
        petri_utils.add_arc_from_to(exiting_place, trans, net, weight=i+1)
        petri_utils.add_arc_from_to(trans, sink, net, weight=1)


def __discover_net_variable_consumption(log):
    new_log, max_map = __map_consecutive_activities_log(log)
    prefix_tree = pm4py.discover_prefix_tree(new_log)
    net = PetriNet("")
    source = PetriNet.Place("source")
    sink = PetriNet.Place("sink")
    net.places.add(source)
    net.places.add(sink)
    im = Marking({source: 1})
    fm = Marking({sink: 1})
    __add_tree_to_net(prefix_tree, max_map, net, source, sink)
    for trace in new_log:
        for ev in trace:
            ev["concept:name"] = ev["concept:name"].split("@@")[0]
    pm4py.view_petri_net(net, im, fm, format="svg")
    aligned_traces = alignments.apply(new_log, net, im, fm, variant=alignments.Variants.VERSION_DIJKSTRA_LESS_MEMORY, parameters={"ret_tuple_as_trans_desc": True})
    trans_count = {x: 0 for x in net.transitions}
    trans_ids = {x.name: x for x in net.transitions}
    for trace in aligned_traces:
        for move in trace["alignment"]:
            if move[0][1] in trans_ids:
                trans_count[trans_ids[move[0][1]]] += 1
    for trans in trans_count:
        if trans_count[trans] == 0:
            petri_utils.remove_transition(net, trans)
    trans_count = {x: y for x, y in trans_count.items() if y >= 1}
    return net, im, fm, trans_count


def __fold_petri_net(net, im, fm, trans_count):
    added_transitions = {}
    added_arcs = set()
    new_net = PetriNet()
    for place in net.places:
        new_net.places.add(place)
    for trans in net.transitions:
        trans_name_split = trans.name.split("#@#")[0]
        if trans_name_split not in added_transitions:
            if "##" in trans_name_split:
                new_trans = PetriNet.Transition(trans_name_split, trans_name_split.split("##")[0])
            else:
                new_trans = PetriNet.Transition(trans_name_split, None)
            new_net.transitions.add(new_trans)
            added_transitions[trans_name_split] = new_trans
        new_net.transitions.add(trans)
    for arc in net.arcs:
        if isinstance(arc.source, PetriNet.Place):
            trans_name_split = arc.target.name.split("#@#")[0]
            arc_desc = arc.source.name + "->" + trans_name_split
            source_obj = arc.source
            target_obj = added_transitions[trans_name_split]
        elif isinstance(arc.target, PetriNet.Place):
            trans_name_split = arc.source.name.split("#@#")[0]
            arc_desc = trans_name_split + "->" + arc.target.name
            source_obj = added_transitions[trans_name_split]
            target_obj = arc.target
        if arc_desc not in added_arcs:
            added_arcs.add(arc_desc)
            arc = petri_utils.add_arc_from_to(source_obj, target_obj, new_net, weight=1)
    trans_count_in = {}
    trans_count_out = {}
    for tr in trans_count:
        trans_name_split = tr.name.split("#@#")[0]
        if trans_name_split not in trans_count_in:
            trans_count_in[trans_name_split] = {}
            trans_count_out[trans_name_split] = {}
        if "#@#" in tr.name:
            trans_in = int(tr.name.split("#@#")[1]) + 1
            trans_out = int(tr.name.split("#@#")[2]) + 1
            print(tr.name, trans_in, trans_out)
            trans_count_in[trans_name_split][trans_in] = trans_count[tr]
            trans_count_out[trans_name_split][trans_out] = trans_count[tr]
        else:
            trans_count_in[trans_name_split] = {1: trans_count[tr]}
            trans_count_out[trans_name_split] = {1: trans_count[tr]}
    print(trans_count_in)
    print(trans_count_out)
    return new_net, im, fm
