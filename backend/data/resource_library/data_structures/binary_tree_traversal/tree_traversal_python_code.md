# 二叉树遍历 Python 代码示例

## TreeNode 定义
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

## 前序遍历（根-左-右）
```python
def preorder(root):
    if not root:
        return
    print(root.val, end=' ')
    preorder(root.left)
    preorder(root.right)
```

## 中序遍历（左-根-右）
```python
def inorder(root):
    if not root:
        return
    inorder(root.left)
    print(root.val, end=' ')
    inorder(root.right)
```

## 后序遍历（左-右-根）
```python
def postorder(root):
    if not root:
        return
    postorder(root.left)
    postorder(root.right)
    print(root.val, end=' ')
```

## 测试代码
```python
# 构建示例树：
#     1
#    / \
#   2   3
#  / \
# 4   5
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)

print("前序:", end=' ')
preorder(root)  # 输出: 1 2 4 5 3
print("\n中序:", end=' ')
inorder(root)   # 输出: 4 2 5 1 3
print("\n后序:", end=' ')
postorder(root) # 输出: 4 2 5 3 1
```

## 注意事项
- 递归深度限制：Python 默认递归深度约 1000，对于极深树需设置 `sys.setrecursionlimit`
- 空树处理：函数开头检查 `if not root: return`