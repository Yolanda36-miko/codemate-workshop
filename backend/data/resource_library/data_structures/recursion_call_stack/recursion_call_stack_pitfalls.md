# 递归终止条件与返回值易错点

## 适用对象
已学习递归基础，在练习中频繁遇到递归 bug 的学生。

## 学习目标
- 识别并修复常见的递归终止条件错误
- 理解递归返回值传递链中的断链问题
- 掌握避免栈溢出的策略

## 易错点 1：终止条件缺失或不正确

### 错误：缺少终止条件

```python
# 永远不会停止！
def bad_countdown(n):
    print(n)
    bad_countdown(n - 1)  # 没有检查 n 是否达到 0
```

### 修正：

```python
def good_countdown(n):
    if n <= 0:            # 终止条件
        return
    print(n)
    good_countdown(n - 1)
```

### 错误：终止条件不可能到达

```python
def unreachable_base(n):
    if n == 0:
        return 0
    return n + unreachable_base(n - 2)  # n 每次减 2

# 如果 n 是奇数：1→-1→-3→-5→... 永远不会碰到 0
```

### 修正：

```python
def fixed_reachable(n):
    if n <= 0:            # 使用不等号而非等号
        return 0
    return n + fixed_reachable(n - 2)
```

## 易错点 2：返回值链断裂

### 错误：忘记 return 递归结果

```python
def bad_factorial(n):
    if n <= 1:
        return 1
    n * factorial(n - 1)  # 没有 return！回溯时返回 None
```

### 修正：

```python
def good_factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)  # 必须 return
```

### 错误：只在递归分支 return，忘记终止分支

```python
def bad_search(root, target):
    if root is None:
        return False
    if root.val == target:
        return True
    bad_search(root.left, target)   # 没有 return
    bad_search(root.right, target)  # 没有 return
    # 函数末尾没有 return，隐式返回 None
```

### 修正：

```python
def good_search(root, target):
    if root is None:
        return False
    if root.val == target:
        return True
    return good_search(root.left, target) or good_search(root.right, target)
```

## 易错点 3：回溯阶段的状态混淆

### 错误：修改可变对象后未恢复

```python
def bad_backtrack(path, choices, result):
    if len(path) == 3:  # 终止条件
        result.append(path)  # 保存的是引用！
        return
    for c in choices:
        path.append(c)
        bad_backtrack(path, choices, result)
        # 忘记回溯恢复——path 一直增长

# 所有 result 中的 path 都指向同一个列表
```

### 修正：

```python
def good_backtrack(path, choices, result):
    if len(path) == 3:
        result.append(path[:])  # 保存副本
        return
    for c in choices:
        path.append(c)
        good_backtrack(path, choices, result)
        path.pop()  # 回溯恢复：移除最后添加的元素
```

## 易错点 4：栈溢出

### 常见原因

1. **递归深度过大**：处理大规模数据时使用递归
2. **终止条件不当**：递归在大量迭代后才到达出口
3. **输入规模估计不足**：二叉树退化为链表时递归深度 = 节点数

### 解决方案

```python
# 方案 1：增加递归深度限制（治标）
import sys
sys.setrecursionlimit(5000)

# 方案 2：转为迭代（治本）
def factorial_iterative(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

# 方案 3：使用显式栈模拟递归
def inorder_iterative(root):
    result = []
    stack = []
    curr = root
    while curr or stack:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        result.append(curr.val)
        curr = curr.right
    return result
```

## 易错点 5：重复计算导致的性能陷阱

```python
# 问题代码：指数级重复计算
def fib_naive(n):
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)

# fib_naive(50) 需要计算约 2^50 次——根本算不完

# 修复：记忆化
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)

# fib_memo(50) 只需 O(n) 次计算
```

## 自查清单

在写完递归函数后，检查：
1. 所有递归分支是否都向终止条件收敛？
2. 终止条件是否使用不等号（<=）而非精确等号（==）？
3. 递归调用的返回值是否被正确传递（return）？
4. 可变对象是否在回溯时恢复到调用前的状态？
5. 对于大规模输入，递归深度是否安全？

## 下一步建议
学习递归转迭代的系统方法，以及尾调用优化的语言支持情况。
