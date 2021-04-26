"""
Middleware between API view and EdgemanageAdapter
"""
import time
import logging

from django.conf import settings
from edgemanage3.edgemanage.adapter import EdgemanageAdapter
from edgemanage3.edgemanage import EdgeState
from api.models import Edge

logger = logging.getLogger(__name__)


def edge_query(dnet=None):
    """
    Perform a `edge_query`
    according to `EDGEMANAGE_CONFIG` and `EDGEMANAGE_DNET`

    - edge_query --dnet mynet --config ../edgemanage_test/edgemanage.yaml -v
    """

    output_data = []

    try:
        edgemanage_adapter = EdgemanageAdapter(
            settings.EDGEMANAGE_CONFIG, dnet or settings.EDGEMANAGE_DNET)
    except FileNotFoundError:
        raise KeyError('edge_query: dnet %s not found' % dnet)

    now = time.time()

    for edge in edgemanage_adapter.edge_list:

        edge_state = None

        try:
            edge_state = EdgeState(edge, edgemanage_adapter.get_config("healthdata_store"),
                                   nowrite=True)
        except Exception as err:
            raise Exception("failed to load state for edge %s: %s\n" % (edge, str(err)))

        if edge_state.state_entry_time:
            state_time = int(now - edge_state.state_entry_time)
        else:
            state_time = -1

        output_data.append({
            'edgename': edge_state.edgename,
            'mode': edge_state.mode,
            'state':  edge_state.state,
            'health': edge_state.health,
            'state_time': state_time,
            'comment': None if edge_state.comment == "" else edge_state.comment
        })

    return output_data


def edge_conf(dnet, edge, mode, comment, comment_user, no_syslog=False):
    """
    Perform a `edge_conf`
    according to `EDGEMANAGE_CONFIG` and `EDGEMANAGE_DNET`

    - edge_conf
        --dnet mynet
        --config edgemanage.yaml
        --mode unavailable
        --comment "out"
        lime20.prod.deflect.ca
    """
    try:
        edgemanage_adapter = EdgemanageAdapter(
            settings.EDGEMANAGE_CONFIG, dnet or settings.EDGEMANAGE_DNET)
    except FileNotFoundError:
        raise KeyError('edge_query: dnet %s not found' % dnet) from FileNotFoundError

    # create lock file
    if not edgemanage_adapter.lock_edge_conf():
        raise Exception("Couldn't acquire edge_conf lockfile")

    if edge not in edgemanage_adapter.edge_list:
        raise KeyError("Edge %s is not in the edge list of %s" %
                       (edge, dnet))

    if not edgemanage_adapter.edge_data_exist(edge):
        raise Exception("Edge %s is not initialised yet - not setting "
                        "status" % edge)

    try:
        edge_state = EdgeState(edge,
                               edgemanage_adapter.config["healthdata_store"],
                               nowrite=False)
    except Exception as err:
        raise Exception("failed to load state for edge %s: %s" %
                        (edge, str(err)))

    prev_state = {
        'mode': edge_state.mode,
        'comment': None if edge_state.comment == "" else edge_state.comment
    }

    edge_state.set_mode(mode)

    if comment:
        comment = "[%s] %s" % (comment_user, comment)
        edge_state.set_comment(comment)

        if not no_syslog:
            edgemanage_adapter.log_edge_conf(
                edge, mode, comment
            )

    elif mode == "available":
        edge_state.unset_comment()

    # release lock
    edgemanage_adapter.unlock_edge_conf()

    # "Set mode for %s to %s" % (edgename, mode)
    return {
        'edge': edge,
        'prev_state': prev_state,
        'current_state': {
            'mode': mode,
            'comment': comment
        }
    }


def dnet_query():
    """
    List all available dnet
    """
    try:
        edgemanage_adapter = EdgemanageAdapter(
            settings.EDGEMANAGE_CONFIG)
        dnets = edgemanage_adapter.dnet_query()
    except FileNotFoundError:
        raise FileNotFoundError('dnet_query: edgemanage error')

    return dnets


def update_dnet_edges():
    """
    Sync deflect-core dnet/edges from DB to edgemanage
    """
    mapping = {}
    edges = Edge.objects.only('dnet')  # lazyload dnets
    for edge in edges:
        dnet = edge.dnet.name
        if dnet in mapping:
            mapping[dnet].append(edge.hostname)
        else:
            mapping[dnet] = [edge.hostname]

    print('mapping', mapping)

    try:
        edgemanage_adapter = EdgemanageAdapter(
            settings.EDGEMANAGE_CONFIG)
        edgemanage_adapter.dump_dnet_and_edges(mapping)
    except Exception as err:
        logger.error(err)
