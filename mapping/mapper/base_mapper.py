from typing import List, Dict, Set

import re
from query_tools import Resource


def get_prefix(uri):
    uri_pattern = re.compile("<?(http(?:s)?://(?:[^/]+/)+)([\w\d()]*)>?")
    prefix_pattern = re.compile("(\w+):(\S+)")
    if uri_pattern.match(uri):
        s_uri = uri_pattern.match(uri)
        return s_uri.group(1), s_uri.group(2)
    if prefix_pattern.search(uri):
        s_uri = prefix_pattern.match(uri)
        return s_uri.group(1), s_uri.group(2)
    raise TypeError("uri doesn't match")


def create_batches(resources: List[Resource], batch_size: int = 100) -> List[Set[Resource]]:
    """
    Helper function to divide a resource list on a list of batches.

    :param resources: resources to be divided.
    :param batch_size: batch size of each group.
    :return: list of Resources batches
    """
    n_batches = len(resources) // batch_size
    resources_batches = []
    for idx in range(n_batches):
        resources_batches.append(set(resources[idx*batch_size:(idx + 1)*batch_size]))
    if len(resources) < batch_size or len(resources) % batch_size != 0:
        resources_batches.append(set(resources[n_batches*batch_size:]))
    return resources_batches


class Mapper:
    """
    Represent entity mapper from a source KB to a target KB.
    """

    def map(self, resources: Set[Resource], add_prefixes: bool = True) -> List[Dict]:
        """
        Given a set of resources, do mapping process an return a list of results.

        :param resources: resources to be mapped.
        :param add_prefixes: if True, adds PREFIX statements in the map query.
        :return: list with all the equivalences for each resource.
        """
        return []

    def map_resource_batches(self, resource: Set[Resource], add_prefixes: bool = False) -> Dict:
        """
        Perform mapping process dividing the resources on batches since the map query can map
        limited number of resources per call.

        :param resource: resources to be divided and mapped.
        :param add_prefixes: if True, adds PREFIX statements in the map query.
        :return: dictionary with all the equivalences for all resources.
        """
        return {}


