"""
Time to fill up our knowledge base with some solid coding interview notes!
Run this and you'll have a nice collection of study materials to chat with.
"""

from services.ingestion import IngestionService
from core.database import get_db
from core.vector_store import VectorStore
import asyncio

async def create_seed_notes():
    """Load up our brain with some quality coding interview wisdom"""
    
    notes_data = [
        {
            "title": "Two Pointers Technique",
            "content": """# Two Pointers Technique

The two pointers technique is a powerful algorithmic approach used to solve array and string problems efficiently.

## When to Use
- Finding pairs in sorted arrays (classic!)
- Removing duplicates (super useful)
- Reversing arrays (easy peasy)
- Finding subarrays with specific properties

## Basic Pattern
```python
def two_pointers_template(arr):
    left = 0
    right = len(arr) - 1
    
    while left < right:
        # Look at what we've got with these two pointers
        if condition_met(arr[left], arr[right]):
            # Boom! Found what we're looking for
            return result
        elif need_larger_sum:
            left += 1
        else:
            right -= 1
    
    return default_result
```

## Common Problems
1. **Two Sum (Sorted Array)**: Find two numbers that add up to target
2. **Container With Most Water**: Find maximum area between two lines
3. **3Sum**: Find triplets that sum to zero
4. **Remove Duplicates**: Remove duplicates from sorted array

## Time Complexity
- Usually O(n) for single pass
- Space complexity: O(1) - constant extra space

## Tips
- Works best with sorted arrays (obviously!)
- Can be combined with other techniques like sliding window
- Don't forget edge cases: empty arrays, single elements, etc.
""",
            "source": "study_notes"
        },
        {
            "title": "Dynamic Programming Fundamentals",
            "content": """# Dynamic Programming (DP)

Dynamic Programming is an optimization technique that solves complex problems by breaking them down into simpler subproblems.

## Core Principles
1. **Optimal Substructure**: The best solution uses the best solutions to smaller pieces
2. **Overlapping Subproblems**: We keep solving the same little problems over and over

## DP Approaches

### 1. Top-Down (Memoization)
```python
def fibonacci_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]
```

### 2. Bottom-Up (Tabulation)
```python
def fibonacci_tab(n):
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]
```

## Common DP Patterns

### 1. Linear DP
- Climbing Stairs
- House Robber
- Maximum Subarray (Kadane's Algorithm)

### 2. 2D DP
- Unique Paths
- Longest Common Subsequence
- Edit Distance

### 3. Knapsack Problems
- 0/1 Knapsack
- Unbounded Knapsack
- Coin Change

## Problem-Solving Steps
1. Figure out if it's actually a DP problem (check those two principles above)
2. Define the state (what the heck does dp[i] actually mean?)
3. Find the recurrence relation (how do pieces connect?)
4. Nail down the base cases (gotta start somewhere!)
5. Pick your approach: top-down or bottom-up
6. Make it faster/use less memory if you can

## Space Optimization
Lots of DP problems can be made way more memory-efficient by only remembering what you actually need from previous steps.
""",
            "source": "study_notes"
        },
        {
            "title": "Binary Search Mastery",
            "content": """# Binary Search

Binary search is a fundamental algorithm for finding elements in sorted arrays with O(log n) time complexity.

## Basic Template
```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1  # Not found
```

## Variants

### 1. Find First Occurrence
```python
def find_first(arr, target):
    left, right = 0, len(arr) - 1
    result = -1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            result = mid
            right = mid - 1  # Continue searching left
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return result
```

### 2. Find Last Occurrence
```python
def find_last(arr, target):
    left, right = 0, len(arr) - 1
    result = -1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            result = mid
            left = mid + 1  # Continue searching right
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return result
```

## Advanced Applications
1. **Search in Rotated Sorted Array**
2. **Find Peak Element**
3. **Search in 2D Matrix**
4. **Find Minimum in Rotated Sorted Array**

## Binary Search on Answer
Sometimes we binary search on the answer space rather than array indices:
- Koko Eating Bananas
- Minimum Days to Make Bouquets
- Capacity to Ship Packages

## Common Pitfalls
- Integer overflow: Use `mid = left + (right - left) // 2`
- Infinite loops: Be careful with boundary updates
- Off-by-one errors: Pay attention to `<=` vs `<` conditions
""",
            "source": "study_notes"
        },
        {
            "title": "Graph Algorithms Essentials",
            "content": """# Graph Algorithms

Graphs are fundamental data structures representing relationships between entities.

## Graph Representations

### 1. Adjacency List
```python
# Most common representation
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A', 'D'],
    'D': ['B', 'C']
}
```

### 2. Adjacency Matrix
```python
# Good for dense graphs
graph = [
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1],
    [0, 1, 1, 0]
]
```

## Traversal Algorithms

### Depth-First Search (DFS)
```python
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    
    visited.add(start)
    print(start)
    
    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
```

### Breadth-First Search (BFS)
```python
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    while queue:
        node = queue.popleft()
        print(node)
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

## Shortest Path Algorithms

### Dijkstra's Algorithm
```python
import heapq

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        if current_dist > distances[current]:
            continue
        
        for neighbor, weight in graph[current]:
            distance = current_dist + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return distances
```

## Common Graph Problems
1. **Connected Components**: Use DFS/BFS
2. **Cycle Detection**: DFS with recursion stack
3. **Topological Sort**: DFS or Kahn's algorithm
4. **Minimum Spanning Tree**: Kruskal's or Prim's
5. **Shortest Path**: Dijkstra's, Bellman-Ford, Floyd-Warshall

## Union-Find (Disjoint Set)
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        
        # Union by rank
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        
        return True
```

## Time Complexities
- DFS/BFS: O(V + E)
- Dijkstra: O((V + E) log V)
- Union-Find: O(α(n)) amortized per operation
""",
            "source": "study_notes"
        },
        {
            "title": "Tree Algorithms and Patterns",
            "content": """# Tree Algorithms

Trees are hierarchical data structures with many important algorithms and patterns.

## Binary Tree Traversals

### Recursive Traversals
```python
def inorder(root):
    if root:
        inorder(root.left)
        print(root.val)
        inorder(root.right)

def preorder(root):
    if root:
        print(root.val)
        preorder(root.left)
        preorder(root.right)

def postorder(root):
    if root:
        postorder(root.left)
        postorder(root.right)
        print(root.val)
```

### Iterative Traversals
```python
def inorder_iterative(root):
    stack = []
    current = root
    result = []
    
    while stack or current:
        while current:
            stack.append(current)
            current = current.left
        
        current = stack.pop()
        result.append(current.val)
        current = current.right
    
    return result
```

## Common Tree Patterns

### 1. Tree Height/Depth
```python
def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
```

### 2. Path Sum Problems
```python
def has_path_sum(root, target_sum):
    if not root:
        return False
    
    if not root.left and not root.right:
        return root.val == target_sum
    
    return (has_path_sum(root.left, target_sum - root.val) or
            has_path_sum(root.right, target_sum - root.val))
```

### 3. Lowest Common Ancestor
```python
def lca(root, p, q):
    if not root or root == p or root == q:
        return root
    
    left = lca(root.left, p, q)
    right = lca(root.right, p, q)
    
    if left and right:
        return root
    
    return left or right
```

## Binary Search Tree (BST)
```python
def validate_bst(root, min_val=float('-inf'), max_val=float('inf')):
    if not root:
        return True
    
    if root.val <= min_val or root.val >= max_val:
        return False
    
    return (validate_bst(root.left, min_val, root.val) and
            validate_bst(root.right, root.val, max_val))
```

## Tree Construction
```python
def build_tree_from_preorder_inorder(preorder, inorder):
    if not preorder or not inorder:
        return None
    
    root = TreeNode(preorder[0])
    mid = inorder.index(preorder[0])
    
    root.left = build_tree_from_preorder_inorder(
        preorder[1:mid+1], inorder[:mid]
    )
    root.right = build_tree_from_preorder_inorder(
        preorder[mid+1:], inorder[mid+1:]
    )
    
    return root
```

## Advanced Tree Concepts
1. **Trie (Prefix Tree)**: For string problems
2. **Segment Tree**: Range queries and updates
3. **Fenwick Tree**: Efficient prefix sums
4. **AVL Tree**: Self-balancing BST
5. **Red-Black Tree**: Another self-balancing BST

## Common Tree Problems
- Diameter of Binary Tree
- Serialize and Deserialize Binary Tree
- Binary Tree Maximum Path Sum
- Construct Binary Tree from Traversals
- Validate Binary Search Tree
""",
            "source": "study_notes"
        }
    ]
    
    # Initialize services
    db = next(get_db())
    vector_store = VectorStore()
    ingestion_service = IngestionService(db, vector_store)
    
    try:
        for note_data in notes_data:
            print(f"Creating note: {note_data['title']}")
            
            document_id, chunks_created = await ingestion_service.ingest_text(
                content=note_data["content"],
                title=note_data["title"],
                source=note_data["source"]
            )
            
            print(f"✅ Created note: {note_data['title']} ({chunks_created} chunks)")
        
        print(f"\n🎉 Successfully created {len(notes_data)} seed notes!")
        
    except Exception as e:
        print(f"❌ Error creating seed notes: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_seed_notes())
