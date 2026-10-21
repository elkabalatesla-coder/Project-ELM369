"""Deterministic dependency ordering with missing-node and cycle detection."""
from typing import Dict, Iterable, List, Mapping, Set


class DependencyError(ValueError):
    """Raised when a dependency graph is incomplete or cyclic."""


def topological_order(graph: Mapping[str, Iterable[str]]) -> List[str]:
    """Return a stable topological order; graph maps node to prerequisite nodes."""
    nodes: Set[str] = set(graph)
    normalized: Dict[str, Set[str]] = {node: set(deps) for node, deps in graph.items()}
    missing = sorted({dep for deps in normalized.values() for dep in deps if dep not in nodes})
    if missing:
        raise DependencyError("missing_dependencies:" + ",".join(missing))

    remaining = {node: set(deps) for node, deps in normalized.items()}
    ready = sorted(node for node, deps in remaining.items() if not deps)
    ordered: List[str] = []
    while ready:
        node = ready.pop(0)
        ordered.append(node)
        for candidate in sorted(remaining):
            if node in remaining[candidate]:
                remaining[candidate].remove(node)
                if not remaining[candidate] and candidate not in ordered and candidate not in ready:
                    ready.append(candidate)
        ready.sort()
    if len(ordered) != len(nodes):
        cyclic = sorted(node for node, deps in remaining.items() if deps)
        raise DependencyError("dependency_cycle:" + ",".join(cyclic))
    return ordered
