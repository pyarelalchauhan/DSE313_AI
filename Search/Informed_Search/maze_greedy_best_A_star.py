"""
Informed Search Algorithms: Greedy Best-First Search and A* for Maze Solving
DSE313 AI - 2026

This module implements informed search algorithms that use heuristics to guide
the search towards the goal more efficiently than uninformed search (DFS/BFS).

Key Concepts:
- Heuristic h(n): Estimated cost from node n to goal
- Path cost g(n): Actual cost from start to node n
- Evaluation function f(n): Used to determine which node to expand next

Algorithms:
1. Greedy Best-First Search: f(n) = h(n) - expands node closest to goal
2. A* Search: f(n) = g(n) + h(n) - considers both path cost and heuristic

Heuristics for maze:
- Manhattan Distance: |x1-x2| + |y1-y2| (admissible for 4-directional movement)
- Euclidean Distance: sqrt((x1-x2)^2 + (y1-y2)^2) (admissible)
"""

import sys
import heapq


class Node:
    """
    Represents a node in the search tree.

    Attributes:
        state: Current position (row, col)
        parent: The node we came from (None for start)
        action: Action taken to reach this node (None for start)
        g_cost: Path cost from start to this node
        h_cost: Heuristic estimate to goal
        f_cost: Total evaluation = g_cost + h_cost (for A*) or just h_cost (for Greedy)
    """
    def __init__(self, state, parent, action, g_cost=0, h_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g_cost = g_cost  # Cost from start to this node
        self.h_cost = h_cost  # Heuristic estimate to goal
        self.f_cost = g_cost + h_cost  # Total estimated cost

    def __lt__(self, other):
        """For priority queue comparison - lower f_cost has higher priority."""
        return self.f_cost < other.f_cost


class PriorityQueueFrontier:
    """
    Priority queue frontier for informed search algorithms.

    Uses a min-heap to always return the node with lowest f_cost.
    This is the key difference from DFS (stack) and BFS (queue).

    Priority Queue: Best-first ordering based on f(n)
    - For Greedy: f(n) = h(n)
    - For A*: f(n) = g(n) + h(n)
    """
    def __init__(self):
        self.frontier = []  # List of (f_cost, counter, node) tuples
        self.counter = 0    # Tie-breaker for equal f_costs
        self.state_map = {} # state -> node mapping for quick lookup

    def add(self, node):
        """Add a node to the frontier."""
        heapq.heappush(self.frontier, (node.f_cost, self.counter, node))
        self.counter += 1
        self.state_map[node.state] = node

    def contains_state(self, state):
        """Check if a state is in the frontier."""
        return state in self.state_map

    def get_node(self, state):
        """Get the node for a given state (for updating if better path found)."""
        return self.state_map.get(state)

    def empty(self):
        """Check if frontier is empty."""
        return len(self.frontier) == 0

    def remove(self):
        """Remove and return the node with lowest f_cost."""
        if self.empty():
            raise Exception("empty frontier")
        while self.frontier:
            f_cost, counter, node = heapq.heappop(self.frontier)
            # Skip if this state was already removed (updated with better path)
            if node.state in self.state_map and self.state_map[node.state] == node:
                del self.state_map[node.state]
                return node
        raise Exception("empty frontier")

    def update_if_better(self, node):
        """
        Update a node if the new path is better (lower g_cost).
        This is important for A* to find optimal paths.
        """
        if node.state in self.state_map:
            existing = self.state_map[node.state]
            if node.g_cost < existing.g_cost:
                # Add new node (old one will be skipped during remove)
                self.add(node)
                return True
        return False


def manhattan_distance(state, goal):
    """
    Manhattan distance heuristic.

    h(n) = |row1 - row2| + |col1 - col2|

    This is ADMISSIBLE for 4-directional movement (never overestimates).
    The actual shortest path can never be less than the Manhattan distance
    because we can only move up, down, left, or right.

    Example:
        state = (6, 0), goal = (0, 11)
        h = |6-0| + |0-11| = 6 + 11 = 17
    """
    row1, col1 = state
    row2, col2 = goal
    return abs(row1 - row2) + abs(col1 - col2)


def euclidean_distance(state, goal):
    """
    Euclidean distance heuristic.

    h(n) = sqrt((row1 - row2)^2 + (col1 - col2)^2)

    This is also ADMISSIBLE because the straight-line distance is always
    less than or equal to any path distance.

    Note: Manhattan distance is usually preferred for grid mazes because
    it's tighter (closer to actual cost) for 4-directional movement.
    """
    row1, col1 = state
    row2, col2 = goal
    return ((row1 - row2) ** 2 + (col1 - col2) ** 2) ** 0.5


class Maze:
    """
    Maze class with support for informed search algorithms.

    Supports:
    - Greedy Best-First Search: Expands node with smallest h(n)
    - A* Search: Expands node with smallest f(n) = g(n) + h(n)

    Both algorithms use a priority queue frontier instead of stack (DFS) or queue (BFS).
    """

    def __init__(self, filename):
        """Load and parse a maze from a file."""

        # Read file
        with open(filename) as f:
            contents = f.read()

        # Validate start and goal
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determine height and width
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Build walls grid and find start/goal
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None
        self.num_explored = 0
        self.explored = set()

    def print(self):
        """Print the maze, showing solution if available."""
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    def neighbors(self, state):
        """
        Get all valid neighbors from a state.

        Returns list of (action, state, step_cost) tuples.
        Step cost is 1 for all moves in an unweighted maze.
        """
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c), 1))  # step_cost = 1
        return result

    def solve_greedy(self, heuristic=manhattan_distance):
        """
        Solve using Greedy Best-First Search.

        Greedy Best-First expands the node that appears to be closest to the goal.
        f(n) = h(n) only - ignores path cost!

        Properties:
        - Not optimal: May not find shortest path
        - Not complete: Can get stuck in loops without proper handling
        - Fast: Often finds a solution quickly
        - Greedy: Always picks the "seemingly" best option

        Parameters:
            heuristic: Function(state, goal) -> estimated cost (default: manhattan_distance)
        """
        self.num_explored = 0

        # Initialize with start node
        h = heuristic(self.start, self.goal)
        start_node = Node(
            state=self.start,
            parent=None,
            action=None,
            g_cost=0,
            h_cost=h
        )
        # For Greedy: f(n) = h(n), so we set f_cost = h_cost only
        start_node.f_cost = h

        frontier = PriorityQueueFrontier()
        frontier.add(start_node)

        self.explored = set()

        while True:
            if frontier.empty():
                raise Exception("no solution")

            # Get node with lowest h(n) - greedy choice!
            node = frontier.remove()
            self.num_explored += 1

            # Goal check
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            self.explored.add(node.state)

            # Expand neighbors
            for action, state, step_cost in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    h = heuristic(state, self.goal)
                    child = Node(
                        state=state,
                        parent=node,
                        action=action,
                        g_cost=node.g_cost + step_cost,
                        h_cost=h
                    )
                    # For Greedy: f(n) = h(n) only
                    child.f_cost = h
                    frontier.add(child)

    def solve_astar(self, heuristic=manhattan_distance):
        """
        Solve using A* Search.

        A* combines the path cost and heuristic:
        f(n) = g(n) + h(n)

        Where:
        - g(n) = actual cost from start to n
        - h(n) = estimated cost from n to goal (heuristic)

        Properties:
        - OPTIMAL: Finds shortest path (if h is admissible)
        - COMPLETE: Will find a solution if one exists
        - Efficient: Explores fewer nodes than BFS in most cases

        Admissible heuristic: Never overestimates the true cost to goal.
        Manhattan distance is admissible for 4-directional grid movement.

        Parameters:
            heuristic: Function(state, goal) -> estimated cost (default: manhattan_distance)
        """
        self.num_explored = 0

        # Initialize with start node
        h = heuristic(self.start, self.goal)
        start_node = Node(
            state=self.start,
            parent=None,
            action=None,
            g_cost=0,
            h_cost=h
        )
        # For A*: f(n) = g(n) + h(n) - already set in Node.__init__

        frontier = PriorityQueueFrontier()
        frontier.add(start_node)

        self.explored = set()

        while True:
            if frontier.empty():
                raise Exception("no solution")

            # Get node with lowest f(n) = g(n) + h(n)
            node = frontier.remove()
            self.num_explored += 1

            # Goal check
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            self.explored.add(node.state)

            # Expand neighbors
            for action, state, step_cost in self.neighbors(node.state):
                new_g_cost = node.g_cost + step_cost
                h = heuristic(state, self.goal)

                if state not in self.explored:
                    if not frontier.contains_state(state):
                        child = Node(
                            state=state,
                            parent=node,
                            action=action,
                            g_cost=new_g_cost,
                            h_cost=h
                        )
                        frontier.add(child)
                    else:
                        # Check if this is a better path
                        existing = frontier.get_node(state)
                        if existing and new_g_cost < existing.g_cost:
                            child = Node(
                                state=state,
                                parent=node,
                                action=action,
                                g_cost=new_g_cost,
                                h_cost=h
                            )
                            frontier.update_if_better(child)

    def output_image(self, filename, show_solution=True, show_explored=False):
        """Create a colorful image of the maze and solution."""
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        # Try to load a bold font for A and B labels
        try:
            # Try common bold fonts
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        except (IOError, OSError):
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 32)
            except (IOError, OSError):
                try:
                    font = ImageFont.truetype("arial.ttf", 32)
                except (IOError, OSError):
                    # Fall back to default font
                    font = ImageFont.load_default()

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # Walls - Dark Gray
                if col:
                    fill = (40, 40, 40)

                # Start - Red
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Goal - Green
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution path - Yellow
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explored states - Orange
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty cell - Light Gray
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        # Draw "A" label on start cell (white bold text)
        start_i, start_j = self.start
        start_x = start_j * cell_size + cell_size // 2
        start_y = start_i * cell_size + cell_size // 2
        draw.text((start_x, start_y), "A", fill="white", font=font, anchor="mm")

        # Draw "B" label on goal cell (white bold text)
        goal_i, goal_j = self.goal
        goal_x = goal_j * cell_size + cell_size // 2
        goal_y = goal_i * cell_size + cell_size // 2
        draw.text((goal_x, goal_y), "B", fill="white", font=font, anchor="mm")

        img.save(filename)


# Command-line interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python maze_greedy_best_A_star.py maze.txt [algorithm]")

    maze_file = sys.argv[1]
    algorithm = sys.argv[2] if len(sys.argv) > 2 else "astar"

    m = Maze(maze_file)
    print("Maze:")
    m.print()

    print(f"Solving with {algorithm.upper()}...")

    if algorithm.lower() == "greedy":
        m.solve_greedy()
        output_name = maze_file.replace(".txt", "_greedy.png")
    else:
        m.solve_astar()
        output_name = maze_file.replace(".txt", "_astar.png")

    print("States Explored:", m.num_explored)
    print("Solution length:", len(m.solution[0]), "steps")
    print("Solution:")
    m.print()
    m.output_image(output_name, show_explored=True)
    print(f"Image saved to: {output_name}")
