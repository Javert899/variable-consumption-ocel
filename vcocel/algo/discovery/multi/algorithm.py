import pm4py

from vcocel.algo.discovery.projection import algorithm as projection_algorithm
from vcocel.algo.discovery.traditional import algorithm as traditional_algorithm


def apply(ocel, parameters=None):
    if parameters is None:
        parameters = {}

    obj_types = sorted(list(set(ocel.objects[ocel.object_type_column])))
    dct_nets = {}
    dct_folded_nets = {}
    dct_ims = {}
    dct_fms = {}
    for ot in obj_types:
        proj_log, max_map, trace_maps, max_tokens = projection_algorithm.apply(ocel, ot)
        net, im, fm, trans_count = traditional_algorithm.apply(proj_log, max_map, trace_maps, max_tokens)
        dct_nets[ot] = net
        dct_ims[ot] = im
        dct_fms[ot] = fm
        net, im, fm = traditional_algorithm.fold_petri_net(net, im, fm, trans_count)
        """
        for arc in net.arcs:
            if hasattr(arc, "histogram"):
                arc.weight = str(arc.histogram)
        pm4py.save_vis_petri_net(net, im, fm, ot+".svg")
        for arc in net.arcs:
            arc.weight = 1"""
        dct_folded_nets[ot] = [net, im, fm]

    return dct_nets, dct_ims, dct_fms, obj_types, dct_folded_nets
