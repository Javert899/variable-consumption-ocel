import uuid

from pm4py.objects.log.obj import EventLog, Trace, Event
import pm4py
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import petri_utils
from pm4py.objects.petri_net import semantics
from copy import copy
from collections import Counter

def __map_consecutive_activities_log(log, activity_key="concept:name"):
    new_log = EventLog()
    max_map = {}
    list_trace_maps = []
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
        list_trace_maps.append(trace_map)
    return new_log, max_map, list_trace_maps


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


def __replay_trace(trace, net, im, fm, list_trace_maps, j):
    activated_transitions = []
    marking = copy(im)
    trans_map = {}
    for trans in net.transitions:
        if trans.label is not None:
            if trans.label not in trans_map:
                trans_map[trans.label] = []
            trans_map[trans.label].append(trans)
    for i in range(len(trace)-1):
        enabled = semantics.enabled_transitions(net, marking)
        curr_ev = trace[i]["concept:name"].split("@@")[0]
        curr_tokens = list_trace_maps[j][trace[i]["concept:name"]]
        next_tokens = list_trace_maps[j][trace[i+1]["concept:name"]]
        trans = [x for x in enabled if x.label == curr_ev]
        trans = [x for x in trans if int(x.name.split("#@#")[1])+1 == curr_tokens and int(x.name.split("#@#")[2])+1 == next_tokens]
        trans = trans[0]
        marking = semantics.execute(trans, net, marking)
        activated_transitions.append(trans)
    enabled = semantics.enabled_transitions(net, marking)
    curr_ev = trace[len(trace) - 1]["concept:name"].split("@@")[0]
    curr_tokens = list_trace_maps[j][trace[len(trace) - 1]["concept:name"]]
    trans = [x for x in enabled if x.label == curr_ev and int(x.name.split("#@#")[1])+1 == curr_tokens]
    trans = trans[0]
    marking = semantics.execute(trans, net, marking)
    activated_transitions.append(trans)
    enabled = list(semantics.enabled_transitions(net, marking))
    trans = enabled[0]
    semantics.execute(trans, net, marking)
    activated_transitions.append(trans)
    return activated_transitions



def apply(log):
    new_log, max_map, list_trace_maps = __map_consecutive_activities_log(log)
    prefix_tree = pm4py.discover_prefix_tree(new_log)
    net = PetriNet("")
    source = PetriNet.Place("source")
    sink = PetriNet.Place("sink")
    net.places.add(source)
    net.places.add(sink)
    im = Marking({source: 1})
    fm = Marking({sink: 1})
    __add_tree_to_net(prefix_tree, max_map, net, source, sink)
    trans_count = []
    for j, trace in enumerate(new_log):
        trans_count = trans_count + __replay_trace(trace, net, im, fm, list_trace_maps, j)
    trans_count = dict(Counter(trans_count))
    for trans in trans_count:
        if trans_count[trans] == 0:
            petri_utils.remove_transition(net, trans)
    trans_count = {x: y for x, y in trans_count.items() if y >= 1}
    return net, im, fm, trans_count


def fold_petri_net(net, im, fm, trans_count):
    added_transitions = {}
    added_arcs = set()
    new_net = PetriNet()
    for place in net.places:
        new_net.places.add(place)
    for trans in trans_count:
        trans_name_split = trans.name.split("#@#")[0]
        if trans_name_split not in added_transitions:
            if "##" in trans_name_split:
                new_trans = PetriNet.Transition(trans_name_split, trans_name_split.split("##")[0])
            else:
                new_trans = PetriNet.Transition(trans_name_split, None)
            new_net.transitions.add(new_trans)
            added_transitions[trans_name_split] = new_trans
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
            trans_count_in[trans_name_split][trans_in] = trans_count[tr]
            trans_count_out[trans_name_split][trans_out] = trans_count[tr]
        else:
            trans_count_in[trans_name_split] = {1: trans_count[tr]}
            trans_count_out[trans_name_split] = {1: trans_count[tr]}
    for arc in net.arcs:
        if isinstance(arc.source, PetriNet.Place):
            trans_name_split = arc.target.name.split("#@#")[0]
            arc_desc = arc.source.name + "->" + trans_name_split
            source_obj = arc.source
            if trans_name_split in added_transitions:
                target_obj = added_transitions[trans_name_split]
                if arc_desc not in added_arcs:
                    if trans_name_split in trans_count_in:
                        arc = petri_utils.add_arc_from_to(source_obj, target_obj, new_net, weight=1)
                        arc.histogram = trans_count_in[trans_name_split]
                        added_arcs.add(arc_desc)
        else:
            trans_name_split = arc.source.name.split("#@#")[0]
            arc_desc = trans_name_split + "->" + arc.target.name
            target_obj = arc.target
            if trans_name_split in added_transitions:
                source_obj = added_transitions[trans_name_split]
                if arc_desc not in added_arcs:
                    if trans_name_split in trans_count_out:
                        arc = petri_utils.add_arc_from_to(source_obj, target_obj, new_net, weight=1)
                        arc.histogram = trans_count_out[trans_name_split]
                        added_arcs.add(arc_desc)
    return new_net, im, fm
