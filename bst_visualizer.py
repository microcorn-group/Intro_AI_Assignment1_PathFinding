import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import deque
import math

class BSTNode:
    """Binary Search Tree Node"""
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.visit_order = None
        self.is_visited = False  # Track if node has been visited/highlighted

class BST:
    """Binary Search Tree implementation"""
    def __init__(self):
        self.root = None
    
    def insert(self, value):
        """Insert a value into the BST"""
        if self.root is None:
            self.root = BSTNode(value)
        else:
            self._insert_recursive(self.root, value)
    
    def _insert_recursive(self, node, value):
        """Recursive helper for insert"""
        if value < node.value:
            if node.left is None:
                node.left = BSTNode(value)
            else:
                self._insert_recursive(node.left, value)
        else:
            if node.right is None:
                node.right = BSTNode(value)
            else:
                self._insert_recursive(node.right, value)
    
    def _traverse(self, node, result, order='inorder'):
        """Generic recursive traversal - order: 'inorder', 'preorder', 'postorder'"""
        if node is None:
            return
        if order == 'preorder':
            result.append(node.value)
        self._traverse(node.left, result, order)
        if order == 'inorder':
            result.append(node.value)
        self._traverse(node.right, result, order)
        if order == 'postorder':
            result.append(node.value)
    
    def inorder_traversal(self):
        """Return in-order traversal result"""
        result = []
        self._traverse(self.root, result, 'inorder')
        return result
    
    def preorder_traversal(self):
        """Return pre-order traversal result"""
        result = []
        self._traverse(self.root, result, 'preorder')
        return result
    
    def postorder_traversal(self):
        """Return post-order traversal result"""
        result = []
        self._traverse(self.root, result, 'postorder')
        return result
    
    def set_visit_order(self, visited_list):
        """Set visit order numbers for each node"""
        visited_dict = {node: order + 1 for order, node in enumerate(visited_list)}
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


def create_search_tree_from_visited_order(visited_order):
    """
    Build a *search tree* showing ALL explored nodes from:
        visited_order = [(node, parent), (node, parent), ...]
    
    This creates the complete exploration tree, showing every node
    discovered by the search algorithm, not just the final path.
    """
    if not visited_order:
        return None

    # Map raw values -> BSTNode objects
    tree_nodes = {}
    root = None
    all_nodes = set()

    # First pass: create all nodes and identify root
    for node, parent in visited_order:
        all_nodes.add(node)
        if node not in tree_nodes:
            tree_nodes[node] = BSTNode(node)
        
        if parent is None:
            root = tree_nodes[node]

    # Second pass: build parent-child relationships
    for node, parent in visited_order:
        if parent is not None:
            if parent not in tree_nodes:
                tree_nodes[parent] = BSTNode(parent)
                all_nodes.add(parent)
            
            parent_node = tree_nodes[parent]
            child_node = tree_nodes[node]
            
            # Place child left/right by value
            if node < parent:
                if parent_node.left is None:
                    parent_node.left = child_node
            else:
                if parent_node.right is None:
                    parent_node.right = child_node

    bst = BST()
    bst.root = root

    # Set visit order for ALL discovered nodes
    visit_nodes = [n for n, _ in visited_order]
    bst.set_visit_order(visit_nodes)
    
    return bst


def create_bst_from_all_nodes(all_nodes):
    """
    Create a Binary Search Tree from ALL graph nodes.
    This shows the complete tree structure with all nodes visible initially,
    then they light up one by one as the search explores them.
    """
    if not all_nodes:
        return None
    
    # Sort nodes to create a balanced BST
    sorted_nodes = sorted(all_nodes)
    
    def build_balanced_bst(node_list):
        if not node_list:
            return None
        mid = len(node_list) // 2
        node = BSTNode(node_list[mid])
        node.left = build_balanced_bst(node_list[:mid])
        node.right = build_balanced_bst(node_list[mid+1:])
        return node
    
    bst = BST()
    bst.root = build_balanced_bst(sorted_nodes)
    return bst


def calculate_tree_layout(node, x=0, y=0, dx=100):
    """Calculate positions for tree nodes"""
    if node is None:
        return []
    
    positions = [(node.value, x, y)]
    
    if node.left is not None:
        positions.extend(calculate_tree_layout(node.left, x - dx, y - 100, dx / 2))
    
    if node.right is not None:
        positions.extend(calculate_tree_layout(node.right, x + dx, y - 100, dx / 2))
    
    return positions


def draw_tree_edges(ax, node, positions_dict, x=0, y=0, color='#66BB6A', linewidth=2.5):
    """Draw edges between tree nodes"""
    if node is None:
        return
    if node.left is not None:
        x_child, y_child = positions_dict[node.left.value]
        ax.plot([x, x_child], [y, y_child], '-', linewidth=linewidth,
                color=color, zorder=1)
        draw_tree_edges(ax, node.left, positions_dict, x_child, y_child, color, linewidth)
    if node.right is not None:
        x_child, y_child = positions_dict[node.right.value]
        ax.plot([x, x_child], [y, y_child], '-', linewidth=linewidth,
                color=color, zorder=1)
        draw_tree_edges(ax, node.right, positions_dict, x_child, y_child, color, linewidth)


def setup_bst_visualization(ax_bst, bst, bst_positions_dict):
    """
    Draw the complete search tree structure (static setup).
    Returns a dict of node_circles and node_texts for animation.
    
    Nodes start INACTIVE (gray), then light up during animation.
    """
    if bst.root is None:
        return {}, {}
    
    bst_positions = list(bst_positions_dict.keys())
    node_circles = {}
    node_texts = {}
    node_badges = {}
    
    # Draw edges (static)
    if bst_positions:
        root_x, root_y = bst_positions_dict[bst.root.value]
        draw_tree_edges(ax_bst, bst.root, bst_positions_dict, root_x, root_y,
                       color='#CCCCCC', linewidth=2)
    
    # Draw all nodes (inactive/gray at first)
    def find_node(current, val):
        if current is None:
            return None
        if current.value == val:
            return current
        left = find_node(current.left, val)
        return left if left else find_node(current.right, val)
    
    for value, (x, y) in bst_positions_dict.items():
        node_obj = find_node(bst.root, value)
        
        # Initial inactive state: light gray
        circle = patches.Circle((x, y), 22,
                               facecolor='#F0F0F0',      # light gray (inactive)
                               edgecolor='#CCCCCC',      # gray border
                               linewidth=2.5, zorder=5)
        ax_bst.add_patch(circle)
        node_circles[value] = circle
        
        # Node value text
        text = ax_bst.text(x, y, str(value), fontsize=13, ha='center', va='center',
                          fontweight='bold', color='#999999', zorder=6)
        node_texts[value] = text
        
        # Visit order badge (hidden initially)
        badge = ax_bst.text(x, y - 38, "", fontsize=9, ha='center', va='top',
                           fontweight='bold', color='#FFFFFF',
                           bbox=dict(boxstyle='round,pad=0.4',
                                    facecolor='#FF6B00', edgecolor='#CC5500',
                                    alpha=0, linewidth=1.5), zorder=7)
        node_badges[value] = badge
    
    return node_circles, node_texts, node_badges


def highlight_node(node_circles, node_texts, node_badges, node_value, visit_num):
    """
    Highlight a node when visited (called during animation).
    Changes from gray (inactive) to bright orange (active).
    """
    if node_value in node_circles:
        # Active state: bright orange
        node_circles[node_value].set_facecolor('#FF9800')
        node_circles[node_value].set_edgecolor('#F57C00')
        node_circles[node_value].set_linewidth(3)
        
        # Bright text
        node_texts[node_value].set_color('#FFFFFF')
        node_texts[node_value].set_fontweight('bold')
        
        # Show visit badge
        badge = node_badges[node_value]
        badge.set_text(f"#{visit_num}")
        bbox = badge.get_bbox_patch()
        if bbox:
            bbox.set_facecolor('#FF6B00')
            bbox.set_alpha(1.0)


def get_all_nodes_dict(bst):
    """Get all nodes as value-only list for animation"""
    return [n.value for n in bst.get_all_nodes()]