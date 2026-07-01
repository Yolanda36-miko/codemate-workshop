# 二叉树遍历代码示例：递归与非递归实现

## 适用对象
已理解二叉树遍历概念，需要可运行的代码实现和对比的学生。

## 学习目标
- 掌握前序、中序、后序遍历的递归和非递归实现
- 理解栈在非递归遍历中的作用
- 能够分析递归与非递归版本的时间/空间复杂度

## TreeNode 定义

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

## 前序遍历（根 → 左 → 右）

### 递归版本

```python
def preorder_recursive(root):
    result = []
    def dfs(node):
        if not node:
            return
        result.append(node.val)   # 先访问根
        dfs(node.left)            # 再访问左子树
        dfs(node.right)           # 最后访问右子树
    dfs(root)
    return result
```

### 非递归版本（显式栈）

```python
def preorder_iterative(root):
    if not root:
        return []
    result = []
    stack = [root]
    while stack:
        node = stack.pop()        # 弹出栈顶
        result.append(node.val)   # 访问
        # 先压右再压左（栈是LIFO，左要先出）
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return result
```

## 中序遍历（左 → 根 → 右）

### 递归版本

```python
def inorder_recursive(root):
    result = []
    def dfs(node):
        if not node:
            return
        dfs(node.left)            # 先访问左子树
        result.append(node.val)   # 再访问根
        dfs(node.right)           # 最后访问右子树
    dfs(root)
    return result
```

### 非递归版本（显式栈）

```python
def inorder_iterative(root):
    result = []
    stack = []
    curr = root
    while curr or stack:
        # 一直向左走到底，沿途压栈
        while curr:
            stack.append(curr)
            curr = curr.left
        # 弹出栈顶，访问，然后转向右子树
        curr = stack.pop()
        result.append(curr.val)
        curr = curr.right
    return result
```

## 后序遍历（左 → 右 → 根）

### 递归版本

```python
def postorder_recursive(root):
    result = []
    def dfs(node):
        if not node:
            return
        dfs(node.left)            # 先访问左子树
        dfs(node.right)           # 再访问右子树
        result.append(node.val)   # 最后访问根
    dfs(root)
    return result
```

### 非递归版本（双栈法）

```python
def postorder_iterative(root):
    if not root:
        return []
    result = []
    stack = [root]
    # 按 根-右-左 的顺序处理，然后反转得到 左-右-根
    while stack:
        node = stack.pop()
        result.append(node.val)
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    return result[::-1]  # 反转得到后序
```

## 层序遍历（BFS）

```python
from collections import deque

def level_order(root):
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)  # 每层一个列表
    return result
```

## 复杂度对比

| 方法 | 时间复杂度 | 空间复杂度 | 空间说明 |
|------|-----------|-----------|---------|
| 递归（三种遍历） | O(n) | O(h) | 递归栈深度 = 树高 |
| 非递归前序 | O(n) | O(h) | 显式栈最大深度 = 树高 |
| 非递归中序 | O(n) | O(h) | 同上 |
| 非递归后序 | O(n) | O(h) | 同上 |
| 层序遍历 | O(n) | O(w) | w = 树的最大宽度 |

> n = 节点总数，h = 树高（最坏 O(n)，平衡树 O(log n)）

## 测试

```python
#      1
#     / \
#    2   3
#   / \
#  4   5
root = TreeNode(1,
    TreeNode(2, TreeNode(4), TreeNode(5)),
    TreeNode(3)
)

print(preorder_recursive(root))   # [1, 2, 4, 5, 3]
print(preorder_iterative(root))   # [1, 2, 4, 5, 3]
print(inorder_recursive(root))    # [4, 2, 5, 1, 3]
print(inorder_iterative(root))    # [4, 2, 5, 1, 3]
print(postorder_recursive(root))  # [4, 5, 2, 3, 1]
print(postorder_iterative(root))  # [4, 5, 2, 3, 1]
print(level_order(root))          # [[1], [2, 3], [4, 5]]
```

## 自我检查
1. 中序遍历的非递归实现中，什么时候将 curr 设为 node.right？
2. 后序遍历的双栈法为什么需要反转结果？
3. 递归版本和非递归版本的空间复杂度有什么异同？

## 下一步建议
学习 Morris 遍历（O(1) 空间的遍历算法）和遍历在表达式树中的应用。
