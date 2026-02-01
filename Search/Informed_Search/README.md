[Reference Lecture CS50](https://cs50.harvard.edu/ai/weeks/0/)

# Informed Search:

Search strategy that uses problem-specific knowledge to find solutions more efficiently.


## 1. Greedy Best-First Search
Breadth-first and depth-first are both uninformed search algorithms. That is, these algorithms do not utilize any knowledge about the problem that they did not acquire through their own exploration. However, most often is the case that some knowledge about the problem is, in fact, available. For example, when a human maze-solver enters a junction, the human can see which way goes in the general direction of the solution and which way does not. AI can do the same. A type of algorithm that considers additional knowledge to try to improve its performance is called an informed search algorithm.

Greedy best-first search expands the node that is the closest to the goal, as determined by a heuristic function h(n). As its name suggests, the function estimates how close to the goal the next node is, but it can be mistaken. The efficiency of the greedy best-first algorithm depends on how good the heuristic function is. For example, in a maze, an algorithm can use a heuristic function that relies on the Manhattan distance between the possible nodes and the end of the maze. The Manhattan distance ignores walls and counts how many steps up, down, or to the sides it would take to get from one location to the goal location. This is an easy estimation that can be derived based on the (x, y) coordinates of the current location and the goal location.

### Maze4

<img src = "Maze4.png">

### Manhattan Distance

<img src ="Greedy-First-Search_manhatan_1.png">
Manhattan Distance
However, it is important to emphasize that, as with any heuristic, it can go wrong and lead the algorithm down a slower path than it would have gone otherwise. It is possible that an uninformed search algorithm will provide a better solution faster, but it is less likely to do so than an informed algorithm.

Search algorithm that expands the node that is closest to the goal, as estimate by a heuristic function $$h(n)$$
### Manhattan Distance : heuristics Maze4
<img src = "Heuristics_maze4.png">

### Maze 5
<img src = "Maze5.png">

## 2. A* search

A development of the greedy best-first algorithm, A* search considers not only h(n), the estimated cost from the current location to the goal, but also g(n), the cost that was accrued until the current location. By combining both these values, the algorithm has a more accurate way of determining the cost of the solution and optimizing its choices on the go. The algorithm keeps track of (cost of path until now + estimated cost to the goal), and once it exceeds the estimated cost of some previous option, the algorithm will ditch the current path and go back to the previous option, thus preventing itself from going down a long, inefficient path that h(n) erroneously marked as best.

Yet again, since this algorithm, too, relies on a heuristic, it is as good as the heuristic that it employs. It is possible that in some situations it will be less efficient than greedy best-first search or even the uninformed algorithms. For A* search to be optimal, the heuristic function, h(n), should be:

### 1. Admissible (Never Overestimates)

A heuristic is **admissible** if it **never overestimates** the true cost to reach the goal.

```
h(n) ≤ actual cost from n to goal
```

**Why is this important?** If h(n) overestimates, A* might skip the optimal path thinking it's too expensive!

#### Example from Maze4:

```
 # # ###  #B   ← Goal B at (0, 11)
 # #     ##
   # # # ##
# ## # # ##
#    # #
### ## #####
A   ##         ← Start A at (6, 0)
```

Consider node at position **(4, 4)**:
- Manhattan Distance: h(4,4) = |4-0| + |4-11| = 4 + 7 = **11**
- Actual shortest path to B: Must navigate around walls = **19 steps** (actual)

Since **11 ≤ 19**, Manhattan distance is admissible here! ✓

**Manhattan Distance is ALWAYS admissible for maze** because:
- It calculates the straight-line grid distance (ignoring walls)
- The actual path can only be **equal to or longer** (due to walls)
- It can never be shorter than Manhattan distance

### 2. Consistent (Triangle Inequality)

A heuristic is **consistent** if for every node n and its successor n' with step cost c:

```
h(n) ≤ h(n') + c
```

This means: the estimated cost from n should not be more than (estimated cost from n' + cost to get to n')

**Visual Explanation:**
```
        h(n)
    n ---------> Goal
    |            ↗
  c |      h(n')
    ↓      /
    n' ---/

Triangle Inequality: h(n) ≤ c + h(n')
The direct estimate should not exceed going through n'
```

#### Example from Maze4:

Let's check consistency for a move from **(6, 1)** to **(6, 2)**:

```
Position (6, 1): h = |6-0| + |1-11| = 6 + 10 = 16
Position (6, 2): h = |6-0| + |2-11| = 6 + 9  = 15
Step cost c = 1 (moving one cell)

Check: h(6,1) ≤ h(6,2) + c
       16 ≤ 15 + 1
       16 ≤ 16 ✓ Consistent!
```

Another example - move from **(5, 3)** to **(4, 3)** (moving UP):
```
Position (5, 3): h = |5-0| + |3-11| = 5 + 8 = 13
Position (4, 3): h = |4-0| + |3-11| = 4 + 8 = 12
Step cost c = 1

Check: h(5,3) ≤ h(4,3) + c
       13 ≤ 12 + 1
       13 ≤ 13 ✓ Consistent!
```

**Manhattan Distance is ALWAYS consistent** because:
- Moving one step can change h(n) by at most 1 (either +1, -1, or 0)
- Since step cost c = 1, the inequality h(n) ≤ h(n') + 1 always holds

### Summary Table

| Property | Definition | Manhattan Distance |
|----------|------------|-------------------|
| **Admissible** | h(n) ≤ actual cost | ✓ Always (ignores walls) |
| **Consistent** | h(n) ≤ h(n') + c | ✓ Always (changes by ≤1 per step) |

**Note:** A consistent heuristic is always admissible, but an admissible heuristic is not always consistent.

<img src = "A*_h_g.png">