"""Schema graph helpers for table suggestions and SQL join-path hints.

Builds an undirected adjacency graph from each table/view's foreign-key
`references`, and provides helpers to find bridge tables and join paths.
"""

from collections import deque


def all_objects(schema_data):
    """Combine a schema's tables and views into a single name -> def map."""
    return {
        **schema_data.get('tables', {}),
        **schema_data.get('views', {}),
    }


def build_adjacency(objects):
    """Return {object_name: [(neighbour, from_cols, to_cols), ...]}.

    The graph is undirected: an FK from A(sourceCol) -> B(targetCol) is added
    in both directions so joins can be traversed either way.
    """
    adj = {name: [] for name in objects}
    for name, table_def in objects.items():
        for ref in table_def.get('references', []):
            target = ref.get('target')
            if target not in objects:
                continue
            source_cols = ref.get('sourceCol', [])
            target_cols = ref.get('targetCol', [])
            # A.source_cols = B.target_cols
            adj[name].append((target, source_cols, target_cols))
            # Reverse: B.target_cols = A.source_cols (join can be written either way)
            adj[target].append((name, target_cols, source_cols))
    return adj


def shortest_path(adj, start, goal):
    """Return the node list of the shortest path start -> goal, or None."""
    if start == goal:
        return [start]
    prev = {start: None}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        if cur == goal:
            break
        for (nxt, _from, _to) in adj.get(cur, []):
            if nxt not in prev:
                prev[nxt] = cur
                queue.append(nxt)
    if goal not in prev:
        return None
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    return path


def build_join_paths(objects, object_names):
    """Return a deduplicated list of join-edge hints among the given objects.

    Each hint is a dict: {"left": col, "right_table": table, "right": col}.
    Only the shortest path between each selected pair is used, so a bridge
    table may appear in multiple paths but edges are deduplicated by
    (left, right_table, right).
    """
    adj = build_adjacency(objects)
    edges = {}
    names = sorted(object_names)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            path = shortest_path(adj, a, b)
            if not path or len(path) < 2:
                continue
            for k in range(len(path) - 1):
                left, right = path[k], path[k + 1]
                # find the FK edge(s) between these two nodes
                for (nxt, from_cols, to_cols) in adj.get(left, []):
                    if nxt == right:
                        for fc, tc in zip(from_cols, to_cols):
                            key = (left, fc, right, tc)
                            edges.setdefault(key, {
                                "left_table": left,
                                "left": fc,
                                "right_table": right,
                                "right": tc,
                            })
    return list(edges.values())


def compact_context(schema_data, object_names):
    """Return a compact schema dict for the LLM (used by table suggestions).

    Includes each object's name, description (markdown), column names with
    short descriptions, and FK references. Deliberately omits per-column types
    and the (often large) 'statement' SQL to keep the call fast.
    """
    objects = all_objects(schema_data)
    context = {}
    for name in object_names:
        table_def = objects.get(name)
        if not table_def:
            continue
        context[name] = {
            "description": [
                {k: v for k, v in entry.items() if v is not None}
                for entry in table_def.get("markdown", [])
            ],
            "columns": {
                col_key: col.get("description")
                for col_key, col in table_def.get("columns", {}).items()
                if col.get("description")
            },
            "foreign_keys": [
                {
                    "from_columns": ref.get("sourceCol", []),
                    "to_table": ref.get("target"),
                    "to_columns": ref.get("targetCol", []),
                }
                for ref in table_def.get("references", [])
            ],
        }
    return context