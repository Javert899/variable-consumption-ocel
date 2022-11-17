from graphviz import Digraph
from pm4py.util import exec_utils, constants
from enum import Enum
import tempfile


class Parameters(Enum):
    FORMAT = "format"


def apply(list_nets, list_ims, list_fms, parameters=None):
    if parameters is None:
        parameters = {}

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph("pt", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})
    viz.attr('node', shape='ellipse', fixedsize='false')

    otypes_color = {}

    viz.attr(overlap='false')
    viz.attr(splines='false')
    viz.attr(rankdir='LR')
    viz.format = image_format

    return viz
