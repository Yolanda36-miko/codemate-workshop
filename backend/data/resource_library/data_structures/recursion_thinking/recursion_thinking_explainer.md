# 递归思想：分而治之的艺术

## 适用对象
正在学习算法设计，希望深入理解递归思想的学生。

## 学习目标
- 理解递归的核心三要素
- 掌握递归与迭代的区别和适用场景
- 了解递归的典型应用场景
- 识别常见的递归思维误区

## 核心概念：递归三要素

### 1. 递归出口（Base Case）
- **定义**：问题的最小规模，直接返回结果
- **作用**：终止递归，避免无限循环
- **示例**：
```python
def factorial(n):
    if n == 0 or n == 1:  # 出口条件
        return 1
    return n * factorial(n - 1)
```

### 2. 递推关系（Recursive Case）
- **定义**：将原问题分解为更小的子问题
- **作用**：建立问题与子问题的关系
- **示例**：`n! = n * (n-1)!`

### 3. 问题规模缩小
- **定义**：每次递归调用都使问题规模严格减小
- **作用**：确保最终能到达出口条件
- **示例**：`factorial(n)` → `factorial(n-1)`，规模减1

## 递归 vs 迭代

### 对比表

| 维度 | 递归 | 迭代 |
|------|------|------|
| **代码结构** | 简洁，接近数学表达 | 相对繁琐 |
| **内存开销** | 调用栈开销大 | 常量级内存开销 |
| **执行效率** | 函数调用开销 | 效率更高 |
| **可读性** | 逻辑清晰，易理解 | 相对复杂 |
| **适用场景** | 树结构、分治、回溯 | 简单循环、性能敏感场景 |

### 转换示例

**递归版本**：
```python
def sum_recursive(lst):
    if not lst:
        return 0
    return lst[0] + sum_recursive(lst[1:])
```

**迭代版本**：
```python
def sum_iterative(lst):
    total = 0
    for num in lst:
        total += num
    return total
```

## 递归典型应用

### 1. 树遍历

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# 中序遍历
def inorder_traversal(root):
    if not root:
        return []
    return inorder_traversal(root.left) + [root.val] + inorder_traversal(root.right)
```

### 2. 分治算法

**快速排序**：
```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
```

### 3. 回溯算法

**N皇后问题**：
```python
def solve_n_queens(n):
    def backtrack(row, path):
        if row == n:
            result.append(path[:])
            return
        for col in range(n):
            if is_valid(row, col, path):
                path.append(col)
                backtrack(row + 1, path)
                path.pop()
```

### 4. 汉诺塔问题

```python
def hanoi(n, source, target, auxiliary):
    if n == 1:
        print(f"Move disk 1 from {source} to {target}")
        return
    hanoi(n - 1, source, auxiliary, target)
    print(f"Move disk {n} from {source} to {target}")
    hanoi(n - 1, auxiliary, target, source)
```

## 递归思维误区

### 误区 1：缺少出口条件
```python
def infinite_recursion(n):
    return infinite_recursion(n)  # 没有出口，无限递归
```

### 误区 2：问题规模没有缩小
```python
def bad_factorial(n):
    if n == 1:
        return 1
    return n * bad_factorial(n)  # 规模没有缩小
```

### 误区 3：重复计算
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)  # 大量重复计算
```
**优化方案**：使用记忆化搜索

```python
memo = {0: 0, 1: 1}
def fibonacci_memo(n):
    if n not in memo:
        memo[n] = fibonacci_memo(n - 1) + fibonacci_memo(n - 2)
    return memo[n]
```

### 误区 4：忽视栈溢出风险
- Python 默认递归深度限制约为 1000
- 过深递归会引发 `RecursionError`

## 自我检查
1. 递归的三要素是什么？
2. 递归和迭代各有什么优缺点？
3. 哪些问题适合用递归解决？
4. 如何避免递归中的重复计算？

## 下一步建议
学习记忆化搜索、动态规划，以及递归转迭代的技巧。