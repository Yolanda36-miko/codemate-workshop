# 前序中序后序遍历易错点

## 适用对象
已学习二叉树遍历但常在实际编码中出错的学生。

## 学习目标
- 识别遍历顺序混淆的常见场景
- 正确写出递归边界条件
- 习惯性地对空节点做防御性检查
- 理解遍历结果与树结构的对应关系

## 易错点 1：遍历顺序混淆

### 三个遍历的定义

```
前序：根 → 左 → 右  （根在最前）
中序：左 → 根 → 右  （根在中间）
后序：左 → 右 → 根  （根在最后）
```

### 记忆技巧

- **前序** = 先处理自己，再处理孩子（自顶向下）
- **中序** = 先处理左孩子，再处理自己，最后右孩子（对 BST 得到有序序列）
- **后序** = 先处理完所有孩子，再处理自己（自底向上，适合需要子树结果的场景）

### 常见错误：访问和处理的顺序搞反

```python
# 中序遍历
def inorder(node):
    if not node:
        return
    inorder(node.left)
    print(node.val)     # 访问根的正确位置
    inorder(node.right)

# 错误写法：把 print 放在递归调用前面就成了前序
def wrong_inorder(node):
    if not node:
        return
    print(node.val)     # 错！这样变成前序了
    inorder(node.left)
    inorder(node.right)
```

## 易错点 2：空节点处理缺失

### 错误：没有检查空节点

```python
def bad_traversal(root):
    print(root.val)              # root 可能是 None！
    bad_traversal(root.left)     # 没有检查就访问
    bad_traversal(root.right)
```

### 修正

```python
def good_traversal(root):
    if not root:                 # 先检查
        return
    print(root.val)
    good_traversal(root.left)
    good_traversal(root.right)
```

## 易错点 3：非递归遍历的栈操作错误

### 前序遍历：压栈顺序

```python
# 正确：先压右，再压左
stack.append(node.right)
stack.append(node.left)

# 错误：先压左再压右，则右子会先弹出——变成了"根右左"
stack.append(node.left)
stack.append(node.right)
```

### 中序遍历：忘记转向右子树

```python
# 正确
curr = stack.pop()
result.append(curr.val)
curr = curr.right    # 处理完根后转向右子树

# 错误：没有转向——停留在当前节点，死循环
curr = stack.pop()
result.append(curr.val)
# 缺少 curr = curr.right
```

## 易错点 4：已知遍历结果重建二叉树

### 关键认知

- **仅前序 + 中序**可以唯一确定二叉树
- **仅后序 + 中序**可以唯一确定二叉树
- **仅前序 + 后序**不能唯一确定（除非是满二叉树）
- **仅有中序**不能确定（因为不知道根在哪）

### 重建步骤（前序 + 中序）

```
前序: [3, 9, 20, 15, 7]  → 根 = 3（第一个）
中序: [9, 3, 15, 20, 7]  → 3 左边 [9] 是左子树，右边 [15,20,7] 是右子树

      3
     / \
    9   ?
```

继续递归处理左右子数组即可。

## 易错点 5：混淆遍历的应用场景

| 场景 | 推荐遍历 | 原因 |
|------|---------|------|
| 打印目录结构 | 前序 | 先访问父目录再访问子文件 |
| BST 有序输出 | 中序 | BST 中序 = 升序 |
| 删除文件系统（先删子文件） | 后序 | 先处理子节点再处理父节点 |
| 计算目录总大小 | 后序 | 需要子树大小才能计算上级 |
| 查找最短路径 | 层序(BFS) | 逐层扩展，找到即最短 |

## 自查清单

1. 函数入口是否检查了 `root is None`？
2. 递归访问是否在正确的顺序（前/中/后）？
3. 非递归版本中栈的压入/弹出顺序是否正确？
4. 如果使用可变容器收集结果，是否在每次调用前初始化？

## 下一步建议
练习已知前序+中序重建二叉树的代码实现，以及用后序+中序验证。
