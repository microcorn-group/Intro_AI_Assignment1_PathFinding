import sys
import math
from collections import deque
import heapq
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
from matplotlib.patches import FancyBboxPatch

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
# INTERACTIVE VISUALIZATION WITH UI CONTROLS
# ------------------------------
def visualize_search(nodes, edges, visited_order, path, method_name, start, goals, filename=None):
    # Create figure with extra space for controls
    fig = plt.figure(figsize=(14, 9))
    fig.patch.set_facecolor('#F5F5F5')
    
    # Main graph axes
    ax = plt.subplot2grid((12, 12), (0, 0), colspan=12, rowspan=9)
    ax.set_facecolor('#FFFFFF')
    ax.set_xlabel("X Coordinate", fontsize=12, fontweight='bold', color='#333333')
    ax.set_ylabel("Y Coordinate", fontsize=12, fontweight='bold', color='#333333')
    ax.grid(True, alpha=0.25, linestyle='--', linewidth=0.8, color='#CCCCCC')
    
    # Set axis limits with padding
    x_coords = [coord[0] for coord in nodes.values()]
    y_coords = [coord[1] for coord in nodes.values()]
    x_margin = (max(x_coords) - min(x_coords)) * 0.2 or 1
    y_margin = (max(y_coords) - min(y_coords)) * 0.2 or 1
    ax.set_xlim(min(x_coords) - x_margin, max(x_coords) + x_margin)
    ax.set_ylim(min(y_coords) - y_margin, max(y_coords) + y_margin)
    
    # Add subtle border to the plot area
    for spine in ax.spines.values():
        spine.set_edgecolor('#BBBBBB')
        spine.set_linewidth(1.5)

    # State management
    state = {
        'current_method': method_name,
        'animation': None,
        'is_playing': False,
        'current_frame': 0,
        'path_lines': [],
        'edge_lines': [],
        'scatters': {},
        'visit_labels': {},
        'node_labels': {}
    }

    # --- Draw edges and edge costs ---
    for src, neighbors in edges.items():
        x1, y1 = nodes[src]
        for dest, cost in neighbors:
            x2, y2 = nodes[dest]
            line, = ax.plot([x1, x2], [y1, y2], color='#A8A8A8', linestyle='-', 
                           linewidth=2, zorder=1, alpha=0.5)
            state['edge_lines'].append(line)
            
            midx, midy = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(midx, midy, f"{cost:.1f}", fontsize=10, color='#2E7D32', 
                   fontweight='bold', ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.35', facecolor='#E8F5E9', 
                            edgecolor='#4CAF50', alpha=0.9, linewidth=1.5), zorder=2)

    # --- Draw nodes ---
    for node, (x, y) in nodes.items():
        if node == start:
            color = "#4CAF50"  # Material Green
            size = 900
            edge_color = '#2E7D32'
            edge_width = 3.5
        elif node in goals:
            color = "#F44336"  # Material Red
            size = 900
            edge_color = '#C62828'
            edge_width = 3.5
        else:
            color = "#ECEFF1"  # Light Blue Grey
            size = 750
            edge_color = '#78909C'
            edge_width = 2.5
            
        scatter = ax.scatter(x, y, color=color, s=size, zorder=5, 
                            edgecolors=edge_color, linewidths=edge_width, alpha=0.95)
        state['scatters'][node] = scatter
        
        # Node label
        label = ax.text(x, y, f"{node}", fontsize=15, ha='center', va='center', 
                       fontweight='bold', color='#212121', zorder=6)
        state['node_labels'][node] = label
        
        # Visit order label (initially empty)
        visit_label = ax.text(x, y - 0.5, "", fontsize=9, ha='center', 
                             va='top', color='#1976D2', fontweight='bold', zorder=6,
                             bbox=dict(boxstyle='round,pad=0.3', facecolor='#E3F2FD', 
                                      edgecolor='#2196F3', alpha=0, linewidth=1))
        state['visit_labels'][node] = visit_label

    # Info box with enhanced styling
    info_box = ax.text(0.02, 0.98, "", transform=ax.transAxes, fontsize=11,
                      verticalalignment='top', family='monospace',
                      bbox=dict(boxstyle='round,pad=0.8', facecolor='#FFF9C4', 
                               edgecolor='#FFA726', alpha=0.95, linewidth=2.5),
                      fontweight='bold', color='#424242', linespacing=1.6)

    # --- Legend with enhanced styling ---
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4CAF50', 
                  markersize=12, markeredgecolor='#2E7D32', markeredgewidth=2.5,
                  label='🚀 Start Node', linestyle='None'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#F44336', 
                  markersize=12, markeredgecolor='#C62828', markeredgewidth=2.5,
                  label='🎯 Goal Node', linestyle='None'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF9800', 
                  markersize=12, markeredgecolor='#F57C00', markeredgewidth=2.5,
                  label='👁 Explored', linestyle='None'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ECEFF1', 
                  markersize=12, markeredgecolor='#78909C', markeredgewidth=2.5,
                  label='⚪ Unvisited', linestyle='None'),
        plt.Line2D([0], [0], color='#D32F2F', linewidth=4, label='✓ Final Path'),
    ]
    legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=10, 
                      framealpha=0.97, edgecolor='#757575', fancybox=True,
                      shadow=True, title='Legend', title_fontsize=11)
    legend.get_frame().set_facecolor('#FAFAFA')
    legend.get_frame().set_linewidth(2)

    # --- Button axes (at bottom with better spacing) ---
    button_row = 10
    ax_bfs = plt.subplot2grid((12, 12), (button_row, 0), colspan=2, rowspan=1)
    ax_dfs = plt.subplot2grid((12, 12), (button_row, 2), colspan=2, rowspan=1)
    ax_gbfs = plt.subplot2grid((12, 12), (button_row, 4), colspan=2, rowspan=1)
    ax_astar = plt.subplot2grid((12, 12), (button_row, 6), colspan=2, rowspan=1)
    ax_reset = plt.subplot2grid((12, 12), (button_row, 8), colspan=2, rowspan=1)
    ax_pause = plt.subplot2grid((12, 12), (button_row, 10), colspan=2, rowspan=1)

    # Create buttons with Material Design colors
    btn_bfs = Button(ax_bfs, 'BFS', color='#64B5F6', hovercolor='#42A5F5')
    btn_dfs = Button(ax_dfs, 'DFS', color='#64B5F6', hovercolor='#42A5F5')
    btn_gbfs = Button(ax_gbfs, 'GBFS', color='#FFB74D', hovercolor='#FFA726')
    btn_astar = Button(ax_astar, 'A*', color='#FFB74D', hovercolor='#FFA726')
    btn_reset = Button(ax_reset, '🔄 Reset', color='#81C784', hovercolor='#66BB6A')
    btn_pause = Button(ax_pause, '⏸ Pause', color='#FFD54F', hovercolor='#FFCA28')
    
    # Style button text
    for btn in [btn_bfs, btn_dfs, btn_gbfs, btn_astar, btn_reset, btn_pause]:
        btn.label.set_fontsize(11)
        btn.label.set_fontweight('bold')
        btn.label.set_color('#212121')

    # Function to run search algorithm
    def run_algorithm(method):
        state['current_method'] = method
        
        if method == "BFS":
            goal, count, new_path, new_visited = bfs(edges, start, goals)
        elif method == "DFS":
            goal, count, new_path, new_visited = dfs(edges, start, goals)
        elif method == "GBFS":
            goal, count, new_path, new_visited = gbfs(nodes, edges, start, goals)
        elif method == "A*":
            goal, count, new_path, new_visited = astar(nodes, edges, start, goals)
        
        return goal, count, new_path, new_visited

    # Reset visualization
    def reset_viz():
        # Clear path lines
        for line in state['path_lines']:
            line.remove()
        state['path_lines'].clear()
        
        # Reset node colors
        for node in state['scatters']:
            if node == start:
                state['scatters'][node].set_color('#4CAF50')
                state['scatters'][node].set_edgecolor('#2E7D32')
            elif node in goals:
                state['scatters'][node].set_color('#F44336')
                state['scatters'][node].set_edgecolor('#C62828')
            else:
                state['scatters'][node].set_color('#ECEFF1')
                state['scatters'][node].set_edgecolor('#78909C')
        
        # Clear visit labels
        for label in state['visit_labels'].values():
            label.set_text("")
            label.set_bbox(dict(boxstyle='round,pad=0.3', facecolor='#E3F2FD', 
                               edgecolor='#2196F3', alpha=0, linewidth=1))
        
        state['current_frame'] = 0
        info_box.set_text("")
        ax.set_title("", fontsize=15, fontweight='bold', pad=20, color='#424242')
        fig.canvas.draw_idle()

    # Animation update function with enhanced visuals
    def update(frame, visited_order, path, method):
        state['current_frame'] = frame
        
        if frame < len(visited_order):
            current = visited_order[frame]
            visit_num = frame + 1
            
            if current not in (start, *goals):
                state['scatters'][current].set_color('#FF9800')
                state['scatters'][current].set_edgecolor('#F57C00')
                state['scatters'][current].set_alpha(0.95)
            
            state['visit_labels'][current].set_text(f"#{visit_num}")
            # Make the visit label background visible when visited
            state['visit_labels'][current].set_bbox(dict(boxstyle='round,pad=0.3', 
                                                         facecolor='#E3F2FD', 
                                                         edgecolor='#2196F3', 
                                                         alpha=0.9, linewidth=1))
            
            # Calculate progress percentage
            progress = (visit_num / len(visited_order)) * 100
            progress_bar = '█' * int(progress / 10) + '░' * (10 - int(progress / 10))
            
            info_box.set_text(f"🔍 Algorithm: {method}\n"
                            f"📊 Progress: [{progress_bar}] {progress:.0f}%\n"
                            f"🔢 Nodes Explored: {visit_num} / {len(visited_order)}\n"
                            f"📍 Current Node: {current}\n"
                            f"⚡ Status: Searching...")
            
            ax.set_title(f"🗺️ Path Finding Visualization — {method} Algorithm", 
                        fontsize=15, fontweight='bold', pad=20, color='#1976D2')
            
        elif frame == len(visited_order):
            # Draw final path with enhanced styling
            for line in state['path_lines']:
                line.remove()
            state['path_lines'].clear()
            
            # Calculate total path cost
            path_cost = 0
            for i in range(len(path) - 1):
                x1, y1 = nodes[path[i]]
                x2, y2 = nodes[path[i + 1]]
                line, = ax.plot([x1, x2], [y1, y2], color='#D32F2F', 
                              linewidth=5, zorder=4, alpha=0.85, 
                              solid_capstyle='round')
                state['path_lines'].append(line)
                
                # Calculate cost for this edge
                for neighbor, cost in edges.get(path[i], []):
                    if neighbor == path[i + 1]:
                        path_cost += cost
                        break
            
            progress_bar = '█' * 10
            info_box.set_text(f"🔍 Algorithm: {method}\n"
                            f"📊 Progress: [{progress_bar}] 100%\n"
                            f"🔢 Nodes Explored: {len(visited_order)}\n"
                            f"📏 Path Length: {len(path)} nodes\n"
                            f"💰 Total Cost: {path_cost:.1f}\n"
                            f"✅ Status: COMPLETE!")
            info_box.set_bbox(dict(boxstyle='round,pad=0.8', facecolor='#C8E6C9', 
                                  edgecolor='#4CAF50', alpha=0.95, linewidth=2.5))
            
            ax.set_title(f"🗺️ Path Finding Visualization — {method} Algorithm ✓ COMPLETE", 
                        fontsize=15, fontweight='bold', pad=20, color='#2E7D32')
        
        return [info_box]

    # Button callbacks
    def on_bfs(event):
        reset_viz()
        goal, count, new_path, new_visited = run_algorithm("BFS")
        if goal:
            state['is_playing'] = True
            if state['animation']:
                state['animation'].event_source.stop()
            state['animation'] = animation.FuncAnimation(
                fig, update, fargs=(new_visited, new_path, "BFS"),
                frames=len(new_visited) + 15, interval=700, repeat=False, blit=False)
            fig.canvas.draw_idle()

    def on_dfs(event):
        reset_viz()
        goal, count, new_path, new_visited = run_algorithm("DFS")
        if goal:
            state['is_playing'] = True
            if state['animation']:
                state['animation'].event_source.stop()
            state['animation'] = animation.FuncAnimation(
                fig, update, fargs=(new_visited, new_path, "DFS"),
                frames=len(new_visited) + 15, interval=700, repeat=False, blit=False)
            fig.canvas.draw_idle()

    def on_gbfs(event):
        reset_viz()
        goal, count, new_path, new_visited = run_algorithm("GBFS")
        if goal:
            state['is_playing'] = True
            if state['animation']:
                state['animation'].event_source.stop()
            state['animation'] = animation.FuncAnimation(
                fig, update, fargs=(new_visited, new_path, "GBFS"),
                frames=len(new_visited) + 15, interval=700, repeat=False, blit=False)
            fig.canvas.draw_idle()

    def on_astar(event):
        reset_viz()
        goal, count, new_path, new_visited = run_algorithm("A*")
        if goal:
            state['is_playing'] = True
            if state['animation']:
                state['animation'].event_source.stop()
            state['animation'] = animation.FuncAnimation(
                fig, update, fargs=(new_visited, new_path, "A*"),
                frames=len(new_visited) + 15, interval=700, repeat=False, blit=False)
            fig.canvas.draw_idle()

    def on_reset(event):
        if state['animation']:
            state['animation'].event_source.stop()
        state['is_playing'] = False
        reset_viz()

    def on_pause(event):
        if state['animation']:
            if state['is_playing']:
                state['animation'].event_source.stop()
                state['is_playing'] = False
                btn_pause.label.set_text('▶ Resume')
            else:
                state['animation'].event_source.start()
                state['is_playing'] = True
                btn_pause.label.set_text('⏸ Pause')
            fig.canvas.draw_idle()

    # Connect buttons
    btn_bfs.on_clicked(on_bfs)
    btn_dfs.on_clicked(on_dfs)
    btn_gbfs.on_clicked(on_gbfs)
    btn_astar.on_clicked(on_astar)
    btn_reset.on_clicked(on_reset)
    btn_pause.on_clicked(on_pause)

    # Add title to the figure
    fig.suptitle('🎯 Interactive Pathfinding Algorithm Visualizer', 
                fontsize=17, fontweight='bold', color='#1565C0', y=0.98)
    
    # Initial animation with smoother interval
    state['is_playing'] = True
    state['animation'] = animation.FuncAnimation(
        fig, update, fargs=(visited_order, path, method_name),
        frames=len(visited_order) + 15, interval=600, repeat=False, blit=False)

    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
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

# ------------------------------
# CUSTOM METHODS (REUSE EXISTING)
# ------------------------------
def custom_uninformed(edges, start, goal):
    return dfs(edges, start, goal)

def custom_informed(nodes, edges, start, goal):
    return astar(nodes, edges, start, goal)

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