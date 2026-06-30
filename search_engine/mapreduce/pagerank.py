from __future__ import annotations


def compute_pagerank(
    graph: dict[str, list[str]],
    damping: float = 0.85,
    iterations: int = 20,
) -> dict[str, float]:
    nodes = set(graph)
    for links in graph.values():
        nodes.update(links)
    if not nodes:
        return {}

    ranks = {node: 1.0 / len(nodes) for node in nodes}
    base = (1.0 - damping) / len(nodes)

    for _ in range(iterations):
        next_ranks = {node: base for node in nodes}
        dangling_rank = sum(ranks[node] for node in nodes if not graph.get(node))
        dangling_share = damping * dangling_rank / len(nodes)

        for node in nodes:
            next_ranks[node] += dangling_share

        for source, targets in graph.items():
            valid_targets = [target for target in targets if target in nodes]
            if not valid_targets:
                continue
            share = damping * ranks[source] / len(valid_targets)
            for target in valid_targets:
                next_ranks[target] += share

        ranks = next_ranks

    total = sum(ranks.values()) or 1.0
    return {node: score / total for node, score in ranks.items()}

