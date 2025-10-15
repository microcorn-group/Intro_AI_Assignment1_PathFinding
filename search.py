import sys
import math
from collections import deque
import heapq
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ------------------------------
# LOAD GRAPH DATA
# ------------------------------
def load_problem(filename): 
    nodes = {}
    edges = {}
    origin = None
    destinations = []

    with open(filename, 'r') as f:
        section = None
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('Nodes:'):
                section = 'nodes'
                continue
            elif line.startswith('Edges:'):
                section = 'edges'
                continue
            elif line.startswith('Origin:'):
                section = 'origin'
                continue
            elif line.startswith('Destinations:'):
                section = 'dest'
                continue

            if section == 'nodes':
                node, coords = line.split(':')
                x, y = coords.strip(" ()").split(',')
                nodes[node.strip()] = (float(x), float(y))

            elif section == 'edges':
                left, cost = line.split(':')
                a, b = left.strip(" ()").split(',')
                cost = float(cost.strip())
                edges.setdefault(a.strip(), []).append((b.strip(), cost))

            elif section == 'origin':
                origin = line.strip()

            elif section == 'dest':
                destinations = [d.strip() for d in line.split(";")]

    return nodes, edges, origin, destinations

# ------------------------------
# HEURISTIC FUNCTION
# ------------------------------
def heuristic(a, b, nodes):
    (x1, y1) = nodes[a]
    (x2, y2) = nodes[b]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

# ------------------------------
# PRINT RESULTS
# ------------------------------
def print_results(filename, method, goal, num_nodes, path):
    print(f"{filename} {method}")
    print(f"{goal} {num_nodes}")
    print(" -> ".join(path))

# ------------------------------
# VISUALIZATION (Combined Graph + Animation)
# ------------------------------
def visualize_search(nodes, edges, visited_order, path, method_name, start, goals):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True)
    ax.set_title(f"Route Finding using {method_name}")

    # --- Draw edges and edge costs ---
    for src, neighbors in edges.items():
        x1, y1 = nodes[src]
        for dest, cost in neighbors:
            x2, y2 = nodes[dest]
            ax.plot([x1, x2], [y1, y2], color='gray', linestyle='--', linewidth=1)
            midx, midy = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(midx, midy, f"{cost:.1f}", fontsize=8, color='green', alpha=0.8)

    # --- Draw nodes ---
    scatters = {}
    for node, (x, y) in nodes.items():
        color = "lightgray"
        if node == start:
            color = "limegreen"  # Start
        elif node in goals:
            color = "red"  # Goal
        scatters[node] = ax.scatter(x, y, color=color, s=500, zorder=5, edgecolors='black')
        # label node clearly above the point
        ax.text(x, y + 0.2, f"{node}", fontsize=12, ha='center', va='bottom', fontweight='bold')

    # --- Legend for clarity ---
    legend_patches = [
        plt.Line2D([], [], color='limegreen', marker='o', linestyle='None', markersize=10, label='Start Node'),
        plt.Line2D([], [], color='red', marker='o', linestyle='None', markersize=10, label='Goal Node'),
        plt.Line2D([], [], color='orange', marker='o', linestyle='None', markersize=10, label='Visited / Explored'),
        plt.Line2D([], [], color='lightgray', marker='o', linestyle='None', markersize=10, label='Unvisited'),
        plt.Line2D([], [], color='red', linewidth=3, label='Final Path'),
    ]
    ax.legend(handles=legend_patches, loc='upper right', fontsize=8, framealpha=0.9)

    # --- Animation update ---
    def update(frame):
        if frame < len(visited_order):
            current = visited_order[frame]
            if current not in (start, *goals):
                scatters[current].set_color('orange')
            ax.set_title(f"Route Finding using {method_name} | Nodes Expanded: {frame + 1}")
        elif frame == len(visited_order):
            # Draw the final path
            for i in range(len(path) - 1):
                x1, y1 = nodes[path[i]]
                x2, y2 = nodes[path[i + 1]]
                ax.plot([x1, x2], [y1, y2], color='red', linewidth=3, zorder=6)
            ax.set_title(f"Route Finding using {method_name} | Final Path Found!")
        return list(scatters.values())

    total_frames = len(visited_order) + 10
    ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=600, repeat=False)

    plt.tight_layout()
    plt.show()

# ------------------------------
# SEARCH ALGORITHMS
# ------------------------------
def dfs(edges, start, goal):
    stack = [(start, [start])]
    visited = set()
    visited_order = []
    count = 0

    while stack:
        node, path = stack.pop()
        count += 1
        visited_order.append(node)

        if node in goal:
            return node, count, path, visited_order
        
        if node not in visited:
            visited.add(node)
            for neighbor, _ in sorted(edges.get(node, []), reverse=True):
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))

    return None, count, [], visited_order


def bfs(edges, start, goal):
    queue = deque([(start, [start])])
    visited = set()
    visited_order = []
    count = 0

    while queue:
        node, path = queue.popleft()
        count += 1
        visited_order.append(node)

        if node in goal:
            return node, count, path, visited_order
        
        if node not in visited:
            visited.add(node)
            for neighbor, _ in sorted(edges.get(node, [])):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))

    return None, count, [], visited_order


def gbfs(nodes, edges, start, goal):
    goal = goal[0]
    frontier = []
    heapq.heappush(frontier, (0, start, [start]))
    visited = set()
    visited_order = []
    count = 0

    while frontier:
        _, node, path = heapq.heappop(frontier)
        count += 1
        visited_order.append(node)

        if node in goal:
            return node, count, path, visited_order

        if node not in visited:
            visited.add(node)
            for neighbor, _ in edges.get(node, []):
                if neighbor not in visited:
                    h = heuristic(neighbor, goal, nodes)
                    heapq.heappush(frontier, (h, neighbor, path + [neighbor]))

    return None, count, [], visited_order


def astar(nodes, edges, start, goal):
    goal = goal[0]
    frontier = []
    heapq.heappush(frontier, (0, 0, start, [start]))
    visited = {}
    visited_order = []
    count = 0

    while frontier:
        f, g, node, path = heapq.heappop(frontier)
        count += 1
        visited_order.append(node)

        if node in goal:
            return node, count, path, visited_order

        if node not in visited or g < visited[node]:
            visited[node] = g
            for neighbor, cost in sorted(edges.get(node, [])):
                g2 = g + cost
                f2 = g2 + heuristic(neighbor, goal, nodes)
                heapq.heappush(frontier, (f2, g2, neighbor, path + [neighbor]))

    return None, count, [], visited_order

def custom_uninformed(edges, start, goal):
    """
    Custom uninformed search using a priority queue ordered by accumulated path cost.

    This function behaves similarly to Dijkstra's algorithm (uniform-cost search), but
    is tailored for the assignment as a custom uninformed method. Key points:

    - Uses a min-heap (`frontier`) where each entry is a tuple:
        (accumulated_cost, creation_order, node, path)
      `accumulated_cost` (g) is the total cost from the start node to `node`.
      `creation_order` is a tiebreaker to ensure a stable ordering when costs tie.
      `path` stores the nodes visited along the route to `node` for easy reconstruction.

    - `base_cost_to_node` keeps the best-known cost to reach each node; a newly
      discovered (or better) path updates this map and pushes a new entry onto the heap.

    - `visited_order` records the order nodes are popped from the frontier. This is
      useful for visualization/animation of the search process.

    - The function returns a 4-tuple:
        (goal_node_or_None, nodes_expanded_count, path_list, visited_order)

    Note: `goal` may contain multiple targets; this implementation checks membership
    (node in goal) so it will accept any of the provided destinations.
    """

    # Counter used to break ties in the heap when two entries have the same cost
    creation_counter = 0
    frontier = []
    # Track the best known cost to each node (g-values). Initialize start with cost 0.
    base_cost_to_node = {start: 0}

    # Push the start node onto the heap. Heap entries: (g, order, node, path)
    heapq.heappush(frontier, (0, creation_counter, start, [start]))

    visited_order = []
    count = 0

    while frontier:
        # Pop the lowest-cost entry
        g, _, node, path = heapq.heappop(frontier)
        count += 1
        visited_order.append(node)

        # If this node is one of the goals, return immediately with the path found
        if node in goal:
            return node, count, path, visited_order

        # Expand neighbours in numeric order for deterministic behavior (keys are node ids)
        for neighbor, cost_to_neighbor in sorted(edges.get(node, []), key=lambda x: int(x[0])):
            g2 = g + cost_to_neighbor
            # If we found a cheaper path to neighbor, record it and push to frontier
            if g2 < base_cost_to_node.get(neighbor, float('inf')):
                creation_counter += 1
                base_cost_to_node[neighbor] = g2
                heapq.heappush(frontier, (g2, creation_counter, neighbor, path + [neighbor]))

    # No path found
    return None, count, [], visited_order

def custom_informed(nodes, edges, start, goal, weight=2.0):
    """
    Custom informed search using A* with a weighted heuristic.

    This function is a variant of the A* search algorithm, modified to use a weighted
    heuristic. The weight parameter allows tuning the influence of the heuristic on
    the search process. A higher weight biases the search more towards the heuristic,
    potentially speeding up the search at the cost of optimality.
    - Uses a min-heap (`frontier`) where each entry is a tuple:
        (f, g, node, path)
      `f` is the total estimated cost (g + weight * h).
      `g` is the accumulated cost from the start node to `node`.
      `path` stores the nodes visited along the route to `node` for easy reconstruction.
    - `visited` keeps track of the best-known cost to reach each node; a newly
      discovered (or better) path updates this map and pushes a new entry onto the heap.
    - `visited_order` records the order nodes are popped from the frontier. This is
        useful for visualization/animation of the search process.
    - The function returns a 4-tuple:
        (goal_node_or_None, nodes_expanded_count, path_list, visited_order)
    Note: `goal` may contain multiple targets; this implementation checks membership
    (node in goal) so it will accept any of the provided destinations.
    """

    goal = goal[0]
    frontier = []
    heapq.heappush(frontier, (0, 0, start, [start]))
    visited = {}
    visited_order = []
    count = 0

    while frontier:
        f, g, node, path = heapq.heappop(frontier)
        count += 1
        visited_order.append(node)

        if node == goal:
            return node, count, path, visited_order
        if node not in visited or g < visited[node]:
            visited[node] = g
            for neighbor, cost in sorted(edges.get(node, [])):
                g2 = g + cost
                h = heuristic(neighbor, goal, nodes)
                f2 = g2 + weight * h
                heapq.heappush(frontier, (f2, g2, neighbor, path + [neighbor]))
    return None, count, [], visited_order

# ------------------------------
# MAIN EXECUTION
# ------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python search.py <filename> <method>")
        sys.exit(1)

    filename, method = sys.argv[1], sys.argv[2].upper()
    nodes, edges, origin, destinations = load_problem(filename)

    if method == "DFS":
        goal, count, path, visited_order = dfs(edges, origin, destinations)
    elif method == "BFS":
        goal, count, path, visited_order = bfs(edges, origin, destinations)
    elif method == "GBFS":
        goal, count, path, visited_order = gbfs(nodes, edges, origin, destinations)
    elif method in ("A*", "AS"):
        goal, count, path, visited_order = astar(nodes, edges, origin, destinations)
    elif method == "CUS1":
        goal, count, path, visited_order = custom_uninformed(edges, origin, destinations)
    elif method == "CUS2":
        goal, count, path, visited_order = custom_informed(nodes, edges, origin, destinations)
    else:
        print("Unknown method:", method)
        sys.exit(1)

    if goal:
        print_results(filename, method, goal, count, path)
        visualize_search(nodes, edges, visited_order, path, method, origin, destinations)
        
    else:
        print(f"{filename} {method}\nNo path found.")
# ------------------------------