from pm4py.algo.transformation.ocel.split_ocel import algorithm
from pm4py.objects.log.obj import EventLog, Trace


def apply(ocel, object_type, activity_key='concept:name'):
    ocel_splits = algorithm.apply(ocel)
    proj_log = EventLog()
    trace_maps = []
    max_map = {}
    max_tokens = 0
    for spli in ocel_splits:
        relations = spli.relations
        relations = relations[relations[ocel.object_type_column] == object_type]
        objects_number = relations.groupby(ocel.event_id_column)[ocel.object_id_column].agg(tuple).to_list()
        activities = relations.groupby(ocel.event_id_column).first()["ocel:activity"].to_list()
        all_objects = set()
        acti_objects = dict()
        i = 0
        while i < len(objects_number):
            act = activities[i]
            if act not in acti_objects:
                acti_objects[act] = set()
            acti_objects[act] = acti_objects[act].union(objects_number[i])
            all_objects = all_objects.union(objects_number[i])
            i = i + 1
        diff_acti_objects = dict()
        for act in acti_objects:
            diff_acti_objects[act] = all_objects.difference(acti_objects[act])
        trace_acti_count = {}
        trace = Trace()
        trace_map = {}
        i = 0
        while i < len(objects_number):
            act = activities[i]
            if len(all_objects.difference(objects_number[i])) > 0:
                act = "SKIP" + act
            if act not in trace_acti_count:
                trace_acti_count[act] = 1
            else:
                trace_acti_count[act] += 1
            act = act + "@@" + str(trace_acti_count[act])
            trace.append({activity_key: act})
            trace_map[act] = len(objects_number[i])
            if act not in max_map:
                max_map[act] = len(objects_number[i])
            else:
                max_map[act] = max(max_map[act], len(objects_number[i]))
            i = i + 1
        if len(trace) > 0:
            proj_log.append(trace)
            trace_maps.append(trace_map)
            max_tokens = max(max_tokens, len(all_objects))
    return proj_log, max_map, trace_maps, max_tokens
