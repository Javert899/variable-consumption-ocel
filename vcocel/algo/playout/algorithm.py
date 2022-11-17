from copy import copy
import random
from pm4py.objects.petri_net import semantics
from collections import Counter


def apply(dct_nets, dct_ims, dct_fms, no_comps=50, max_iter=1000):
    labels_appearing_ots = {}
    for ot in dct_nets:
        for trans in dct_nets[ot].transitions:
            if trans.label is not None:
                true_label = trans.label.split("SKIP")[-1]
                if true_label not in labels_appearing_ots:
                    labels_appearing_ots[true_label] = set()
                labels_appearing_ots[true_label].add(ot)

    events = []
    objects = []
    relations = []
    timest = 1000000
    for i in range(no_comps):
        markings = {}
        for ot in dct_nets:
            markings[ot] = copy(dct_ims[ot])
        continuee = True
        curr_iter = 0
        primitive_events = []
        while continuee:
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
                print(markings)
                cons_trans = random.choice(list(ent[pick_ot]))
                trans_to_fire = [(pick_ot, cons_trans)]
                is_ok = True
                if cons_trans.label is not None:
                    true_label = cons_trans.label.split("SKIP")[-1]
                    for other_ot in labels_appearing_ots[true_label]:
                        if other_ot is not pick_ot:
                            other_trans = [x for x in ent[other_ot] if x.label is not None and x.label.split("SKIP")[-1] == true_label]
                            if not other_trans:
                                is_ok = False
                                break
                            else:
                                trans_to_fire.append((other_ot, other_trans[0]))
                if is_ok:
                    timest += 1
                    #continuee = True
                    for el in trans_to_fire:
                        markings[el[0]] = semantics.execute(el[1], dct_nets[el[0]], markings[el[0]])
                if cons_trans.label is not None:
                    visible_ot_count = {}
                    for el in trans_to_fire:
                        visible_ot_count[el[0]] = list(el[1].in_arcs)[0].weight
                    primitive_events.append((el[1].label, visible_ot_count))
        print(" ")
        print(primitive_events)
        input()
