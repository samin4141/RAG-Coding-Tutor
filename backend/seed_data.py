"""
Let's throw some practice problems into the database!
Just run this script and you'll get a nice collection of coding challenges to work with.
"""

from sqlalchemy.orm import Session
from core.database import get_db, Problem, Solution, TestCase
import json

def create_seed_problems():
    """Load up the database with some classic coding problems - the good stuff!"""
    
    problems_data = [
        {
            "slug": "two-sum",
            "title": "Two Sum",
            "difficulty": "easy",
            "prompt_md": """# Two Sum

Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.

## Example 1:
```
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
```

## Example 2:
```
Input: nums = [3,2,4], target = 6
Output: [1,2]
```

## Example 3:
```
Input: nums = [3,3], target = 6
Output: [0,1]
```

## Constraints:
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9
- Only one valid answer exists.
""",
            "tags": ["array", "hash-table"],
            "skills": ["hash_map", "two_pointers"],
            "solution": """def twoSum(nums, target):
    # We'll use a hash map to remember what numbers we've seen
    num_map = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    
    return []  # This shouldn't happen if the problem is set up right

# Let's test this bad boy
if __name__ == "__main__":
    import sys
    import json
    
    # Grab the input data
    line = sys.stdin.read().strip()
    data = json.loads(line)
    nums = data["nums"]
    target = data["target"]
    
    result = twoSum(nums, target)
    print(json.dumps(result))""",
            "test_cases": [
                {
                    "input": '{"nums": [2,7,11,15], "target": 9}',
                    "expected_output": '[0, 1]',
                    "visible": True
                },
                {
                    "input": '{"nums": [3,2,4], "target": 6}',
                    "expected_output": '[1, 2]',
                    "visible": True
                },
                {
                    "input": '{"nums": [3,3], "target": 6}',
                    "expected_output": '[0, 1]',
                    "visible": False
                },
                {
                    "input": '{"nums": [1,2,3,4,5], "target": 9}',
                    "expected_output": '[3, 4]',
                    "visible": False
                }
            ]
        },
        {
            "slug": "valid-parentheses",
            "title": "Valid Parentheses",
            "difficulty": "easy",
            "prompt_md": """# Valid Parentheses

Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket of the same type.

## Example 1:
```
Input: s = "()"
Output: true
```

## Example 2:
```
Input: s = "()[]{}"
Output: true
```

## Example 3:
```
Input: s = "(]"
Output: false
```

## Constraints:
- 1 <= s.length <= 10^4
- s consists of parentheses only '()[]{}'.
""",
            "tags": ["string", "stack"],
            "skills": ["stack", "string_processing"],
            "solution": """def isValid(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in mapping:
            # Found a closing bracket
            if not stack or stack.pop() != mapping[char]:
                return False
        else:
            # It's an opening bracket, just add it to the stack
            stack.append(char)
    
    return len(stack) == 0

# Test the function
if __name__ == "__main__":
    import sys
    
    s = sys.stdin.read().strip().strip('"')
    result = isValid(s)
    print(str(result).lower())""",
            "test_cases": [
                {
                    "input": '"()"',
                    "expected_output": 'true',
                    "visible": True
                },
                {
                    "input": '"()[]{}"',
                    "expected_output": 'true',
                    "visible": True
                },
                {
                    "input": '"(]"',
                    "expected_output": 'false',
                    "visible": False
                },
                {
                    "input": '"([)]"',
                    "expected_output": 'false',
                    "visible": False
                },
                {
                    "input": '"{[]}"',
                    "expected_output": 'true',
                    "visible": False
                }
            ]
        },
        {
            "slug": "maximum-subarray",
            "title": "Maximum Subarray",
            "difficulty": "medium",
            "prompt_md": """# Maximum Subarray

Given an integer array `nums`, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.

A subarray is a contiguous part of an array.

## Example 1:
```
Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
Output: 6
Explanation: [4,-1,2,1] has the largest sum = 6.
```

## Example 2:
```
Input: nums = [1]
Output: 1
```

## Example 3:
```
Input: nums = [5,4,-1,7,8]
Output: 23
```

## Constraints:
- 1 <= nums.length <= 10^5
- -10^4 <= nums[i] <= 10^4

## Follow up:
If you have figured out the O(n) solution, try coding another solution using the divide and conquer approach, which is more subtle.
""",
            "tags": ["array", "divide-and-conquer", "dynamic-programming"],
            "skills": ["kadanes_algorithm", "dynamic_programming"],
            "solution": """def maxSubArray(nums):
    # Using Kadane's Algorithm - it's pretty clever!
    max_sum = nums[0]
    current_sum = nums[0]
    
    for i in range(1, len(nums)):
        # Should we keep going with our current sum or start fresh?
        current_sum = max(nums[i], current_sum + nums[i])
        max_sum = max(max_sum, current_sum)
    
    return max_sum

# Test the function
if __name__ == "__main__":
    import sys
    import json
    
    line = sys.stdin.read().strip()
    nums = json.loads(line)
    
    result = maxSubArray(nums)
    print(result)""",
            "test_cases": [
                {
                    "input": '[-2,1,-3,4,-1,2,1,-5,4]',
                    "expected_output": '6',
                    "visible": True
                },
                {
                    "input": '[1]',
                    "expected_output": '1',
                    "visible": True
                },
                {
                    "input": '[5,4,-1,7,8]',
                    "expected_output": '23',
                    "visible": False
                },
                {
                    "input": '[-1]',
                    "expected_output": '-1',
                    "visible": False
                },
                {
                    "input": '[-2,-1]',
                    "expected_output": '-1',
                    "visible": False
                }
            ]
        },
        {
            "slug": "climbing-stairs",
            "title": "Climbing Stairs",
            "difficulty": "easy",
            "prompt_md": """# Climbing Stairs

You are climbing a staircase. It takes `n` steps to reach the top.

Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?

## Example 1:
```
Input: n = 2
Output: 2
Explanation: There are two ways to climb to the top.
1. 1 step + 1 step
2. 2 steps
```

## Example 2:
```
Input: n = 3
Output: 3
Explanation: There are three ways to climb to the top.
1. 1 step + 1 step + 1 step
2. 1 step + 2 steps
3. 2 steps + 1 step
```

## Constraints:
- 1 <= n <= 45
""",
            "tags": ["math", "dynamic-programming", "memoization"],
            "skills": ["dynamic_programming", "fibonacci"],
            "solution": """def climbStairs(n):
    if n <= 2:
        return n
    
    # Think of it like this: dp[i] = how many ways to get to step i
    prev2 = 1  # only one way to reach step 1
    prev1 = 2  # two ways to reach step 2
    
    for i in range(3, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current
    
    return prev1

# Test the function
if __name__ == "__main__":
    import sys
    
    n = int(sys.stdin.read().strip())
    result = climbStairs(n)
    print(result)""",
            "test_cases": [
                {
                    "input": '2',
                    "expected_output": '2',
                    "visible": True
                },
                {
                    "input": '3',
                    "expected_output": '3',
                    "visible": True
                },
                {
                    "input": '4',
                    "expected_output": '5',
                    "visible": False
                },
                {
                    "input": '5',
                    "expected_output": '8',
                    "visible": False
                },
                {
                    "input": '1',
                    "expected_output": '1',
                    "visible": False
                }
            ]
        },
        {
            "slug": "binary-tree-inorder-traversal",
            "title": "Binary Tree Inorder Traversal",
            "difficulty": "easy",
            "prompt_md": """# Binary Tree Inorder Traversal

Given the `root` of a binary tree, return the inorder traversal of its nodes' values.

## Example 1:
```
Input: root = [1,null,2,3]
Output: [1,3,2]
```

## Example 2:
```
Input: root = []
Output: []
```

## Example 3:
```
Input: root = [1]
Output: [1]
```

## Constraints:
- The number of nodes in the tree is in the range [0, 100].
- -100 <= Node.val <= 100

## Follow up:
Recursive solution is trivial, could you do it iteratively?

## Note:
For this problem, assume the input is given as a list representation of the binary tree.
The tree will be constructed from the list for you.
""",
            "tags": ["stack", "tree", "depth-first-search", "binary-tree"],
            "skills": ["tree_traversal", "recursion", "stack"],
            "solution": """# Here's our basic tree node - nothing fancy
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def inorderTraversal(root):
    result = []
    
    def inorder(node):
        if node:
            inorder(node.left)
            result.append(node.val)
            inorder(node.right)
    
    inorder(root)
    return result

def build_tree(arr):
    if not arr:
        return None
    
    root = TreeNode(arr[0])
    queue = [root]
    i = 1
    
    while queue and i < len(arr):
        node = queue.pop(0)
        
        if i < len(arr) and arr[i] is not None:
            node.left = TreeNode(arr[i])
            queue.append(node.left)
        i += 1
        
        if i < len(arr) and arr[i] is not None:
            node.right = TreeNode(arr[i])
            queue.append(node.right)
        i += 1
    
    return root

# Test the function
if __name__ == "__main__":
    import sys
    import json
    
    line = sys.stdin.read().strip()
    arr = json.loads(line)
    
    # JSON doesn't have None, so we use "null" and convert it back
    arr = [None if x == "null" else x for x in arr]
    
    root = build_tree(arr)
    result = inorderTraversal(root)
    print(json.dumps(result))""",
            "test_cases": [
                {
                    "input": '[1, "null", 2, 3]',
                    "expected_output": '[1, 3, 2]',
                    "visible": True
                },
                {
                    "input": '[]',
                    "expected_output": '[]',
                    "visible": True
                },
                {
                    "input": '[1]',
                    "expected_output": '[1]',
                    "visible": False
                },
                {
                    "input": '[1, 2, 3, 4, 5]',
                    "expected_output": '[4, 2, 5, 1, 3]',
                    "visible": False
                }
            ]
        },
        {
            "slug": "longest-common-subsequence",
            "title": "Longest Common Subsequence",
            "difficulty": "medium",
            "prompt_md": """# Longest Common Subsequence

Given two strings `text1` and `text2`, return the length of their longest common subsequence. If there is no common subsequence, return 0.

A subsequence of a string is a new string generated from the original string with some characters (can be none) deleted without changing the relative order of the remaining characters.

For example, "ace" is a subsequence of "abcde".

A common subsequence of two strings is a subsequence that is common to both strings.

## Example 1:
```
Input: text1 = "abcde", text2 = "ace" 
Output: 3  
Explanation: The longest common subsequence is "ace" and its length is 3.
```

## Example 2:
```
Input: text1 = "abc", text2 = "abc"
Output: 3
Explanation: The longest common subsequence is "abc" and its length is 3.
```

## Example 3:
```
Input: text1 = "abc", text2 = "def"
Output: 0
Explanation: There is no such common subsequence, so the result is 0.
```

## Constraints:
- 1 <= text1.length, text2.length <= 1000
- text1 and text2 consist of only lowercase English characters.
""",
            "tags": ["string", "dynamic-programming"],
            "skills": ["dynamic_programming", "lcs", "string_algorithms"],
            "solution": """def longestCommonSubsequence(text1, text2):
    m, n = len(text1), len(text2)
    
    # Set up our dynamic programming table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Now let's fill in all the values
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[m][n]

# Test the function
if __name__ == "__main__":
    import sys
    import json
    
    line = sys.stdin.read().strip()
    data = json.loads(line)
    text1 = data["text1"]
    text2 = data["text2"]
    
    result = longestCommonSubsequence(text1, text2)
    print(result)""",
            "test_cases": [
                {
                    "input": '{"text1": "abcde", "text2": "ace"}',
                    "expected_output": '3',
                    "visible": True
                },
                {
                    "input": '{"text1": "abc", "text2": "abc"}',
                    "expected_output": '3',
                    "visible": True
                },
                {
                    "input": '{"text1": "abc", "text2": "def"}',
                    "expected_output": '0',
                    "visible": False
                },
                {
                    "input": '{"text1": "bl", "text2": "yby"}',
                    "expected_output": '1',
                    "visible": False
                }
            ]
        }
    ]
    
    db = next(get_db())
    
    try:
        for problem_data in problems_data:
            # Don't want duplicates, so let's check first
            existing = db.query(Problem).filter(Problem.slug == problem_data["slug"]).first()
            if existing:
                print(f"Problem {problem_data['slug']} already exists, skipping...")
                continue
            
            # Create problem
            problem = Problem(
                slug=problem_data["slug"],
                title=problem_data["title"],
                difficulty=problem_data["difficulty"],
                prompt_md=problem_data["prompt_md"],
                tags=problem_data["tags"],
                skills=problem_data["skills"]
            )
            db.add(problem)
            db.flush()  # This gets us the auto-generated ID
            
            # Create solution
            solution = Solution(
                problem_id=problem.id,
                lang="python",
                code=problem_data["solution"],
                explanation_md=f"This is the canonical solution for {problem_data['title']}."
            )
            db.add(solution)
            
            # Create test cases
            for test_data in problem_data["test_cases"]:
                test_case = TestCase(
                    problem_id=problem.id,
                    input_data=test_data["input"],
                    expected_output=test_data["expected_output"],
                    visible=test_data["visible"]
                )
                db.add(test_case)
            
            print(f"✅ Created problem: {problem_data['title']}")
        
        db.commit()
        print(f"\n🎉 Successfully created {len(problems_data)} seed problems!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating seed problems: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_problems()
