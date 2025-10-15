
# Intro AI — Assignment 2a: Path Finding

This repository contains a small path-finding assignment implemented in Python. The code demonstrates several uninformed and informed search algorithms (DFS, BFS, Greedy Best-First Search, A*) on a simple graph defined in a plaintext problem file.

## Contents

- `search.py` — Main program implementing:
	- Depth-First Search (DFS)
	- Breadth-First Search (BFS)
	- Greedy Best-First Search (GBFS)
	- A* Search (A*)
	- Two custom method aliases (`CUS1`, `CUS2`) that map to DFS and A* respectively
	- Utilities to load a problem file, print results, and draw a plot of the graph and the final path using matplotlib
- `PathFinder-test.txt` — Example problem file with nodes, edges, origin and destinations

## Problem file format

The problem files are plain text and contain four sections: `Nodes:`, `Edges:`, `Origin:`, and `Destinations:`. Sections are case-sensitive and should appear exactly as shown. Example (from `PathFinder-test.txt`):

Nodes:
1: (4,1)
2: (2,2)
3: (4,4)
4: (6,3)
5: (5,6)
6: (7,5)

Edges:
(2,1): 4
(3,1): 5
(1,3): 5
... (each edge is written as `(from,to): cost`)

Origin:
2

Destinations:
5; 4

Notes:
- Node coordinates are used by the heuristic (Euclidean distance) and for plotting.
- Multiple destinations can be listed separated by semicolons (`;`). The current informed algorithms (GBFS, A*) assume a single goal and will use the first destination listed for the heuristic calculation.

## Requirements

- Python 3.8+ (should work with Python 3.7+, but 3.8+ is recommended)

All Python dependencies are listed in `requirements.txt`. It's recommended to use a virtual environment. To install the dependencies, run:

```powershell
python -m pip install -r .\requirements.txt
```

## Usage

Run the `search.py` script with two arguments: the problem filename and the search method.

Supported methods (case-insensitive):
- `DFS` — Depth-First Search
- `BFS` — Breadth-First Search
- `GBFS` — Greedy Best-First Search
- `A*` or `AS` — A* Search
- `CUS1` — Custom uninformed method (uniform-cost / Dijkstra-like search). Uses accumulated path cost ordering.
- `CUS2` — Custom informed method (wrapper for A*). Uses Euclidean distance as the heuristic and currently uses the first listed destination for heuristic computations when multiple destinations are provided.

Example (PowerShell):

```powershell
python .\search.py .\PathFinder-test.txt DFS
```

Expected output (example):

PathFinder-test.txt DFS
5 10
2 -> 3 -> 5

After the textual output the program will open a matplotlib window showing the nodes, edges (with costs), and the chosen path highlighted.

## Notes and caveats

- The input parser expects the exact section headers `Nodes:`, `Edges:`, `Origin:`, and `Destinations:` as shown. Empty lines are ignored.
- The informed search implementations (GBFS and A*) currently use only the first listed destination when computing heuristic distances. If you need multi-goal heuristics, the code will need to be extended.
- Edge definitions are directional as listed in the file (the example contains edges in both directions where appropriate). Make sure to list both (a,b) and (b,a) if you want a bidirectional connection with potentially different costs.
