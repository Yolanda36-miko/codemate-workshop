# 排序与查找算法概念讲解

## 适用对象
正在学习排序与查找算法，需要建立完整的算法选择和对比思维的学生。

## 学习目标
- 理解排序稳定性的含义和重要性
- 掌握排序算法的时间复杂度分析方法
- 理解原地排序与非原地排序的差异
- 了解二分查找的前提和边界条件

## 排序核心概念

### 排序稳定性

**稳定排序**：值相等的元素在排序后保持原有相对顺序。

```
原始数据（按姓名排序后按成绩排序）：
[(张三,85), (李四,90), (王五,85)]

稳定排序（按成绩）：  不稳定排序：
[(张三,85),(王五,85),(李四,90)]  or  [(王五,85),(张三,85),(李四,90)]
 ↑保持原有顺序              ↑顺序可能颠倒
```

**为什么稳定性重要？**
- 多关键字排序：先按次要关键字排，再按主要关键字排（要求稳定性）
- 用户期望：同名商品的展示顺序不应该每次排序都变化

### 原地排序

**原地排序（In-place）**：额外空间复杂度为 O(1) 的排序算法。
- 原地：冒泡、选择、插入、快速、堆排序
- 非原地：归并排序（需要 O(n) 额外空间）

### 比较排序的下界

任何基于比较的排序算法在最坏情况下的时间复杂度下界为 **Ω(n log n)**。这意味着：
- O(n^2) 的算法（冒泡、选择、插入）有优化空间
- O(n log n) 的算法（归并、堆、快速）已经最优
- 要突破 O(n log n)，必须使用非比较排序（计数、基数、桶排序）

## 查找核心概念

### 线性查找

```python
def linear_search(arr, target):
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1
```
- 时间复杂度：O(n)
- 适用：无序或有序数组均可
- 无前提条件

### 二分查找

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2  # 防溢出
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```
- 时间复杂度：O(log n)
- **前提**：数组必须有序
- 每次将搜索空间减半

### 二分查找的变体

```python
# 查找第一个等于 target 的位置
def lower_bound(arr, target):
    left, right = 0, len(arr)
    while left < right:
        mid = left + (right - left) // 2
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left

# 查找第一个大于 target 的位置
def upper_bound(arr, target):
    left, right = 0, len(arr)
    while left < right:
        mid = left + (right - left) // 2
        if arr[mid] <= target:
            left = mid + 1
        else:
            right = mid
    return left
```

## 算法选择决策树

```
数据量小（n < 50）？
├── 是 → 插入排序（简单高效）
└── 否 → 需要稳定性？
    ├── 是 → 归并排序 或 TimSort
    └── 否 → 内存受限？
        ├── 是 → 堆排序（O(1)空间，O(n log n)）
        └── 否 → 快速排序（通常最快）
```

## 常见错误

1. 二分查找用在无序数组上
2. 二分查找中 `mid = (left + right) // 2` 在极端情况下溢出
3. 混淆稳定排序与原地排序的概念
4. 忘记二分查找的循环条件是 `left <= right` 而非 `left < right`

## 自我检查
1. 快速排序在什么情况下退化为 O(n^2)？
2. 归并排序为什么是稳定的而快速排序不是？
3. 二分查找的前提条件是什么？
4. 对已基本有序的数组，哪个排序算法最快？

## 下一步建议
学习 TimSort（Python 内置排序算法）的设计思想，以及外部排序的基本概念。
