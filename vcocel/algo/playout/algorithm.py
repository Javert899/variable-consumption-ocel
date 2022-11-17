from copy import copy
import random
from pm4py.objects.petri_net import semantics
from collections import Counter
from uuid import uuid4
from datetime import datetime
from pm4py.objects.ocel.obj import OCEL
import pandas as pd


def apply(dct_nets, dct_ims, dct_fms, no_comps=50, max_iter=1000):
    labels_appearing_ots = {}
    for ot in dct_nets:
        for trans in dct_nets[ot].transitions:
            if trans.label is not None:
                true_label = trans.label
                if true_label not in labels_appearing_ots:
                    labels_appearing_ots[true_label] = set()
                labels_appearing_ots[true_label].add(ot)
    events = []
    objects = []
    relations = []
    timest = 1000000
    added_objects = set()
    for ccc in range(no_comps):
        tokens_keeper = None
        tokens_keeper = {}
        for ot in dct_nets:
            tokens_keeper[ot] = {x: set(str(uuid4()) for i in range(y)) for x, y in dct_ims[ot].items()}
        markings = {}
        for ot in dct_nets:
            markings[ot] = copy(dct_ims[ot])
        continuee = True
        curr_iter = 0
        primitive_events = []
        while continuee:
            try:
                curr_iter += 1
                if curr_iter >= max_iter:
                    break
                #continuee = False
                ent = {}
                is_ok = False
                for ot in dct_nets:
                    ent[ot] = semantics.enabled_transitions(dct_nets[ot], markings[ot])
                    if ent[ot]:
                        is_ok = True
                if not is_ok:
                    break
                pick_ot = random.choice(list(dct_nets))
                if ent[pick_ot]:
                    cons_trans = random.choice(list(ent[pick_ot]))
                    trans_to_fire = [(pick_ot, cons_trans)]
                    is_ok = True
                    if cons_trans.label is not None:
                        true_label = cons_trans.label
                        for other_ot in labels_appearing_ots[true_label]:
                            if other_ot is not pick_ot:
                                other_trans = [x for x in ent[other_ot] if x.label is not None and x.label == true_label]
                                if not other_trans:
                                    is_ok = False
                                    break
                                else:
                                    trans_to_fire.append((other_ot, other_trans[0]))
                    if is_ok:
                        timest += 1
                        #continuee = True
                        picked_tokens_ot = {}
                        for el in trans_to_fire:
                            markings[el[0]] = semantics.execute(el[1], dct_nets[el[0]], markings[el[0]])
                            curr_tokens = copy(tokens_keeper[el[0]])
                            consumption_arc = list(el[1].in_arcs)[0]
                            production_arc = list(el[1].out_arcs)[0]
                            picked_tokens = random.sample(set(curr_tokens[consumption_arc.source]), consumption_arc.weight)
                            if production_arc.target not in curr_tokens:
                                curr_tokens[production_arc.target] = set()
                            for t in picked_tokens:
                                curr_tokens[consumption_arc.source].remove(t)
                            for t in picked_tokens:
                                curr_tokens[production_arc.target].add(t)
                            if not curr_tokens[consumption_arc.source]:
                                del curr_tokens[consumption_arc.source]
                            picked_tokens_ot[el[0]] = picked_tokens
                            tokens_keeper[el[0]] = curr_tokens
                        if cons_trans.label is not None:
                            visible_ot_count = {}
                            for el in trans_to_fire:
                                visible_ot_count[el[0]] = list(el[1].in_arcs)[0].weight
                            primitive_events.append((el[1].label, timest, picked_tokens_ot))
            except:
                continue
        for i in range(len(primitive_events)):
            acti = primitive_events[i][0]
            if acti.startswith("SKIP"):
                r = random.random()
                if r <= 0.5:
                    continue
                acti = acti.split("SKIP")[1]
            ev = {"ocel:eid": "EVENT_"+str(ccc)+"_"+str(len(events)), "ocel:activity": acti, "ocel:timestamp": datetime.fromtimestamp(primitive_events[i][1])}
            events.append(ev)
            for ot in primitive_events[i][2]:
                for obj in primitive_events[i][2][ot]:
                    if obj not in added_objects:
                        obje = {"ocel:oid": obj, "ocel:type": ot}
                        added_objects.add(obj)
                        objects.append(obje)
                    rel = copy(ev)
                    rel["ocel:oid"] = obj
                    rel["ocel:type"] = ot
                    relations.append(rel)
    events = pd.DataFrame(events)
    objects = pd.DataFrame(objects)
    relations = pd.DataFrame(relations)

    return OCEL(events=events, objects=objects, relations=relations)
