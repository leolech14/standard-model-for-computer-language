"""
Graph Algorithms
================

Shared algorithms for graph analysis: Gini coefficient, Tarjan SCC, BFS components.
"""

from typing import Dict, List, Set
from collections import defaultdict


def gini_coefficient(values: List[int]) -> float:
    """Calculate Gini coefficient for degree distribution inequality."""
    n = len(values)
    if n == 0:
        return 0.0
    avg = sum(values) / n
    if avg == 0:
        return 0.0
    sorted_vals = sorted(values)
    gini_sum = sum((2 * i - n + 1) * sorted_vals[i] for i in range(n))
    return gini_sum / (n * n * avg)


def tarjan_scc_iterative(adj: Dict[str, List[str]], nodes: Set[str]) -> List[List[str]]:
    """
    Find strongly connected components using iterative Tarjan's algorithm.
    Returns list of SCCs with 2+ nodes (cycles).
    """
    index_counter = 0
    index = {}
    lowlink = {}
    on_stack = set()
    stack = []
    sccs = []

    for start in nodes:
        if start in index:
            continue

        # Iterative DFS with explicit call stack
        call_stack = [(start, 0, iter(adj.get(start, [])))]

        while call_stack:
            node, state, neighbors = call_stack[-1]

            if state == 0:
                # First visit
                index[node] = index_counter
                lowlink[node] = index_counter
                index_counter += 1
                stack.append(node)
                on_stack.add(node)
                call_stack[-1] = (node, 1, neighbors)

            # Process neighbors
            try:
                neighbor = next(neighbors)
                if neighbor not in index:
                    call_stack.append((neighbor, 0, iter(adj.get(neighbor, []))))
                elif neighbor in on_stack:
                    lowlink[node] = min(lowlink[node], index[neighbor])
            except StopIteration:
                # All neighbors processed
                call_stack.pop()

                if call_stack:
                    parent, _, _ = call_stack[-1]
                    lowlink[parent] = min(lowlink[parent], lowlink[node])

                if lowlink[node] == index[node]:
                    scc = []
                    while True:
                        w = stack.pop()
                        on_stack.discard(w)
                        scc.append(w)
                        if w == node:
                            break
                    if len(scc) > 1:
                        sccs.append(scc)

    return sccs


def bfs_components(adj: Dict[str, Set[str]], nodes: Set[str]) -> List[Set[str]]:
    """Find connected components using BFS. Returns list of component sets."""
    visited = set()
    components = []

    for start in nodes:
        if start in visited:
            continue
        component = set()
        queue = [start]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            component.add(node)
            for neighbor in adj.get(node, set()):
                if neighbor not in visited:
                    queue.append(neighbor)
        if component:
            components.append(component)

    return components
