import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import deque
import math
import time

# --- 1. BST Data Structure ---

class BSTNode:
    """Binary Search Tree Node"""
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.visit_order = None
        self.is_visited = False

class BST:
    """Binary Search Tree implementation"""
    def __init__(self):
        self.root = None
    
    def insert(self, value):
        """Insert a value into the BST following BST property: left < parent < right"""
        if self.root is None:
            self.root = BSTNode(value)
        else:
            self._insert_recursive(self.root, value)
    
    def _insert_recursive(self, node, value):
        """Recursive helper for insert - maintains BST property"""
        if value < node.value:
            if node.left is None:
                node.left = BSTNode(value)
            else:
                self._insert_recursive(node.left, value)
        elif value > node.value:
            if node.right is None:
                node.right = BSTNode(value)
            else:
                self._insert_recursive(node.right, value)
    
    def set_visit_order(self, visited_list_values):
        """Set visit order numbers for each node"""
        visited_dict = {value: order + 1 for order, value in enumerate(visited_list_values)}
        self._set_visit_recursive(self.root, visited_dict)
    
    def _set_visit_recursive(self, node, visited_dict):
        """Recursive helper to set visit order"""
        if node is None:
            return
        if node.value in visited_dict:
            node.visit_order = visited_dict[node.value]
        self._set_visit_recursive(node.left, visited_dict)
        self._set_visit_recursive(node.right, visited_dict)
    
    def get_all_nodes(self):
        """Get all nodes in a list (for tracking)"""
        result = []
        self._collect_nodes(self.root, result)
        return result
    
    def _collect_nodes(self, node, result):
        """Recursively collect all nodes"""
        if node is None:
            return
        result.append(node)
        self._collect_nodes(node.left, result)
        self._collect_nodes(node.right, result)

# --- 2. Tree Construction Functions ---

def create_bst_from_all_nodes(all_nodes):
    """
    Create a BALANCED Binary Search Tree from a list of node values.
    This prevents degenerate trees by using the midpoint approach.
    """
    if not all_nodes:
        return None
    
    # Sort the nodes
    sorted_nodes = sorted(list(set(all_nodes)))
    
    def build_balanced_bst(node_list):
        """Recursively build a balanced BST from sorted list using midpoint"""
        if not node_list:
            return None
        
        # Find the middle element
        mid = len(node_list) // 2
        node = BSTNode(node_list[mid])
        
        # Recursively build left and right subtrees
        node.left = build_balanced_bst(node_list[:mid])
        node.right = build_balanced_bst(node_list[mid+1:])
        
        return node
    
    bst = BST()
    bst.root = build_balanced_bst(sorted_nodes)
    return bst


def create_exploration_tree_from_visited_order(visited_order, start_node):
    """
    Create an accurate exploration tree from the visited_order list.
    
    Args:
        visited_order: List of tuples (node, parent) showing exploration relationships
        start_node: The start node (root of exploration tree)
    
    Returns:
        BST object representing the actual search tree
    """
    if not visited_order:
        return None
    
    bst = BST()
    
    # Create a map of node_value -> BSTNode for quick lookup
    node_map = {}
    
    # First pass: Create all nodes and set the root
    for node, parent in visited_order:
        if node not in node_map:
            node_map[node] = BSTNode(node)
    
    bst.root = node_map.get(start_node)
    if not bst.root:
        return None
    
    # Second pass: Build parent-child relationships
    for node, parent in visited_order:
        if parent is None:
            # This is the root
            continue
        
        child_node = node_map.get(node)
        parent_node = node_map.get(parent)
        
        if child_node and parent_node:
            # Add child to parent (simple binary approach: left/right alternating)
            if parent_node.left is None:
                parent_node.left = child_node
            elif parent_node.right is None:
                parent_node.right = child_node
            else:
                # For more than 2 children, add to left (BST limitation for n-ary trees)
                pass
    
    return bst


def create_bst_from_visited_order(visited_order):
    """
    Create a BST from the actual visited order of the search algorithm.
    """
    if not visited_order:
        return None
    
    bst = BST()
    node_map = {}
    
    for idx, node_info in enumerate(visited_order):
        if isinstance(node_info, tuple):
            node, parent = node_info
        else:
            node = node_info
            parent = None
        
        new_bst_node = BSTNode(node)
        new_bst_node.visit_order = idx + 1
        node_map[node] = new_bst_node
        
        if bst.root is None:
            bst.root = new_bst_node
        elif parent and parent in node_map:
            parent_node = node_map[parent]
            if parent_node.left is None:
                parent_node.left = new_bst_node
            else:
                parent_node.right = new_bst_node
    
    return bst

# --- 3. Layout and Drawing Functions ---

def calculate_tree_layout(node, x=0, y=0, dx=150):
    """
    Calculate positions for tree nodes.
    FIXED: Proper parameter names (x, y, dx)
    """
    if node is None:
        return []
    
    dy = 120
    positions = [(node.value, x, y)]
    
    if node.left is not None:
        left_width = get_subtree_width(node.left)
        left_x = x - dx - (left_width * dx) / 2
        left_positions = calculate_tree_layout(node.left, left_x, y - dy, dx * 0.8)
        positions.extend(left_positions)
    
    if node.right is not None:
        right_width = get_subtree_width(node.right)
        right_x = x + dx + (right_width * dx) / 2
        right_positions = calculate_tree_layout(node.right, right_x, y - dy, dx * 0.8)
        positions.extend(right_positions)
    
    return positions


def get_subtree_width(node):
    """Calculate the width of a subtree"""
    if node is None:
        return 0
    
    if node.left is None and node.right is None:
        return 1
    
    left_width = get_subtree_width(node.left)
    right_width = get_subtree_width(node.right)
    
    return left_width + right_width if (left_width + right_width) > 0 else 1


def draw_tree_edges(ax, node, positions_dict, color='#AABBC3', linewidth=2.0):
    """Draw edges between tree nodes"""
    if node is None or node.value not in positions_dict:
        return
    
    x, y = positions_dict[node.value]

    if node.left is not None and node.left.value in positions_dict:
        x_child, y_child = positions_dict[node.left.value]
        ax.plot([x, x_child], [y, y_child], '-', linewidth=linewidth,
                color=color, zorder=1, alpha=0.7)
        draw_tree_edges(ax, node.left, positions_dict, color, linewidth)
    
    if node.right is not None and node.right.value in positions_dict:
        x_child, y_child = positions_dict[node.right.value]
        ax.plot([x, x_child], [y, y_child], '-', linewidth=linewidth,
                color=color, zorder=1, alpha=0.7)
        draw_tree_edges(ax, node.right, positions_dict, color, linewidth)


def setup_bst_visualization(ax_bst, bst, bst_positions_dict):
    """
    Draw the complete search tree structure (static setup).
    """
    if bst.root is None:
        return {}, {}, {}
    
    node_circles = {}
    node_texts = {}
    node_badges = {}
    
    # Draw edges
    if bst.root.value in bst_positions_dict:
        draw_tree_edges(ax_bst, bst.root, bst_positions_dict)
    
    # Draw nodes
    for value, (x, y) in bst_positions_dict.items():
        circle = patches.Circle((x, y), 25,
                               facecolor='#F5F5F5',
                               edgecolor='#AABBC3',
                               linewidth=2.0, zorder=5)
        ax_bst.add_patch(circle)
        node_circles[value] = circle
        
        text = ax_bst.text(x, y, str(value), fontsize=14, ha='center', va='center',
                          fontweight='bold', color='#455A64', zorder=6)
        node_texts[value] = text
        
        badge = ax_bst.text(x + 18, y + 18, "", fontsize=10, ha='center', va='center',
                           fontweight='heavy', color='#FFFFFF',
                           bbox=dict(boxstyle='circle,pad=0.2',
                                    facecolor='#03A9F4', edgecolor='#0288D1',
                                    alpha=0.0, linewidth=0.0), zorder=7)
        node_badges[value] = badge
    
    return node_circles, node_texts, node_badges


def highlight_node(node_circles, node_texts, node_badges, node_value, visit_num):
    """Highlight a node when visited"""
    if node_value in node_circles:
        node_circles[node_value].set_facecolor('#FFB300')
        node_circles[node_value].set_edgecolor('#FF8F00')
        node_circles[node_value].set_linewidth(3.5)
        node_texts[node_value].set_color('#FFFFFF')
        
        badge = node_badges[node_value]
        badge.set_text(f"{visit_num}")
        bbox = badge.get_bbox_patch()
        if bbox:
            bbox.set_facecolor('#03A9F4')
            bbox.set_edgecolor('#0288D1')
            bbox.set_alpha(1.0)
            bbox.set_linewidth(1.5)

# --- 4. Animation/Run Function ---

def animate_traversal(bst, traversal_order_values, node_circles, node_texts, node_badges, fig):
    """Highlights nodes during traversal"""
    print(f"Starting traversal visualization for: {traversal_order_values}")
    
    for step, node_value in enumerate(traversal_order_values):
        visit_num = step + 1
        highlight_node(node_circles, node_texts, node_badges, node_value, visit_num)
        
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(0.7)
    
    print("Traversal complete.")


def visualize_bst_traversal(all_node_values, traversal_order_values, traversal_name):
    """Main function to set up and run the visualization"""
    bst = create_bst_from_all_nodes(all_node_values)
    if bst is None:
        print("Cannot visualize an empty tree.")
        return

    # FIXED: Correct parameter passing
    positions_list = calculate_tree_layout(bst.root, x=0, y=0, dx=150)
    bst_positions_dict = {value: (x, y) for value, x, y in positions_list}
    
    if not bst_positions_dict:
        print("No nodes to display.")
        return
         
    all_x = [x for v, (x, y) in bst_positions_dict.items()]
    all_y = [y for v, (x, y) in bst_positions_dict.items()]

    plt.ion()
    fig, ax = plt.subplots(figsize=(12, 8))
    
    ax.set_title(f'BST Traversal Visualization: {traversal_name}', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    x_min, x_max = min(all_x), max(all_x)
    y_min, y_max = min(all_y), max(all_y)
    ax.set_xlim(x_min - 50, x_max + 50)
    ax.set_ylim(y_min - 50, y_max + 50)
    ax.invert_yaxis()

    node_circles, node_texts, node_badges = setup_bst_visualization(ax, bst, bst_positions_dict)

    fig.canvas.draw()
    fig.canvas.flush_events()
    time.sleep(1)
    
    animate_traversal(bst, traversal_order_values, node_circles, node_texts, node_badges, fig)
    
    plt.ioff()
    plt.show()

# --- 5. Example Usage ---

if __name__ == '__main__':
    ALL_NODES = [50, 30, 70, 20, 40, 60, 80, 15, 25, 35, 45, 55, 65, 75, 85]
    INORDER_TRAVERSAL = [15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85]

    print("--- Running In-order Traversal Visualization ---")
    visualize_bst_traversal(
        all_node_values=ALL_NODES,
        traversal_order_values=INORDER_TRAVERSAL,
        traversal_name="In-order"
    )
