# search.py
import sys
import math
from collections import deque
import heapq
import matplotlib.pyplot as plt

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
            elif line.startswith('Destinations:'):  # note plural here!
                section = 'dest'
                continue

            # --- handle each section ---
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

# Heuristic function: Euclidean distance
def heuristic(a, b, nodes):
    (x1, y1) = nodes[a]
    (x2, y2) = nodes[b]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def print_results(filename, method, goal, num_nodes, path):
    print(f"{filename} {method}")
    print(f"{goal} {num_nodes}")
    print(" -> ".join(path))

# Visualization function
def draw_graph(nodes, edges, path=None, method_name=""):
    plt.figure(figsize=(6, 6))

    # Plot nodes
    for node, (x, y) in nodes.items(): 
        plt.scatter(x, y, c='skyblue', s=500)
        plt.text(x, y, f"{node}", fontsize=12, ha='center', va='center', fontweight='bold')

    # Plot edges
    for src, neighbours, in edges.items():
        x1, y1 = nodes[src]
        for dest, cost in neighbours:
            x2, y2 = nodes[dest]
            plt.plot([x1, x2], [y1, y2], 'gray', linestyle='--', linewidth=1)
            midx, midy = (x1 + x2) / 2, (y1 + y2) / 2
            plt.text(midx, midy, f"{cost}", fontsize=8, color='darkgreen')
    
    if path:
        for i in range(len(path) - 1):
            x1, y1 = nodes[path[i]]
            x2, y2 = nodes[path[i + 1]]
            plt.plot([x1, x2], [y1, y2], color='red', linewidth=3, zorder=5)
    
    plt.title(f"Route Finding using {method_name}")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.show()

# Depth-First Search
def dfs(edges, start, goal):
    stack = [(start, [start])]
    visited = set()
    count = 0

    while stack:
        node, path = stack.pop()
        count += 1

        if node in goal:
            return node, count, path
        
        if node not in visited:
            visited.add(node)
            for neighbor, _ in sorted(edges.get(node, []), reverse=True):
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))

    return None, count, []

# Breadth-First Search 
def bfs(edges, start, goal):
    queue = deque([(start, [start])])
    visited = set()
    count = 0

    while queue:
        node, path = queue.popleft()
        count += 1

        if node in goal:
            return node, count, path
        
        if node not in visited:
            visited.add(node)
            for neighbor, _ in sorted(edges.get(node, [])):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))

    return None, count, []

# Greedy Best-First Search
def gbfs(nodes, edges, start, goal):
    goal = goal[0]  # Assume single goal for heuristic
    frontier = []
    heapq.heappush(frontier, (0, start, [start]))
    visited = set()
    count = 0

    while frontier:
        _, node, path = heapq.heappop(frontier)
        count += 1

        if node in goal:
            return node, count, path
        
        if node not in visited:
            visited.add(node)
            for neighbor, _ in edges.get(node, []):
                if neighbor not in visited:
                    h = heuristic(neighbor, goal, nodes)
                    heapq.heappush(frontier, (h, neighbor, path + [neighbor]))

    return None, count, []


# A* Search
def astar(nodes, edges, start, goal):
    goal = goal[0]  # Assume single goal for heuristic
    frontier = []
    heapq.heappush(frontier, (0, 0, start, [start]))
    visited = {}
    count = 0

    while frontier:
        f, g, node, path = heapq.heappop(frontier)
        count += 1

        if node in goal:
            return node, count, path
        
        if node not in visited or g < visited[node]:
            visited[node] = g
            for neighbor, cost in sorted(edges.get(node, [])):
                g2 = g + cost
                f2 = g2 + heuristic(neighbor, goal, nodes)
                heapq.heappush(frontier, (f2, g2, neighbor, path + [neighbor]))

    return None, count, []

def custom_uninformed(edges, start, goal):
    return dfs(edges, start, goal)

def custom_informed(nodes, edges, start, goal):
    return astar(nodes, edges, start, goal)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python search.py <filename> <method>")
        sys.exit(1)

    filename, method = sys.argv[1], sys.argv[2].upper()
    nodes, edges, origin, destinations = load_problem(filename)

    if method == "DFS":
        goal, count, path = dfs(edges, origin, destinations)
    elif method == "BFS":
        goal, count, path = bfs(edges, origin, destinations)
    elif method == "GBFS":
        goal, count, path = gbfs(nodes, edges, origin, destinations)
    elif method in ("A*", "AS"):
        goal, count, path = astar(nodes, edges, origin, destinations)
    elif method == "CUS1":
        goal, count, path = custom_uninformed(edges, origin, destinations)
    elif method == "CUS2":
        goal, count, path = custom_informed(nodes, edges, origin, destinations)
    else:
        print("Unknown method:", method)
        sys.exit(1)

    if goal:
        print_results(filename, method, goal, count, path)
        draw_graph(nodes, edges, path, method_name=method)
    else:
        print(f"{filename} {method}\nNo path found.")



        