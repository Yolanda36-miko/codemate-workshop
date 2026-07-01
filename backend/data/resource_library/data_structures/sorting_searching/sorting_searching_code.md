# 快速排序、归并排序与二分查找代码示例

## 适用对象
需要可运行的高效排序与查找算法代码参考的学生。

## 学习目标
- 能够手写快速排序和归并排序
- 理解两种算法的分治思想和实现差异
- 掌握二分查找的标准实现及其变体

## 快速排序

### 基本版本（Lomuto 分区）

```python
def quicksort(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    if low < high:
        pivot_idx = partition(arr, low, high)
        quicksort(arr, low, pivot_idx - 1)
        quicksort(arr, pivot_idx + 1, high)
    return arr

def partition(arr, low, high):
    pivot = arr[high]              # 选最后一个元素为基准
    i = low - 1                    # i 指向小于 pivot 的区域的末尾
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1                   # 返回 pivot 的最终位置
```

**执行过程示例**（[3, 6, 1, 8, 2, 4]，pivot=4）：

```
初始: [3, 6, 1, 8, 2, |4|]
      i=-1, j=0: 3≤4 → i=0, swap(3,3) → [3, 6, 1, 8, 2, 4]
      i=0,  j=1: 6>4 → 跳过
      i=0,  j=2: 1≤4 → i=1, swap(6,1) → [3, 1, 6, 8, 2, 4]
      i=1,  j=3: 8>4 → 跳过
      i=1,  j=4: 2≤4 → i=2, swap(6,2) → [3, 1, 2, 8, 6, 4]
      最后: swap(i+1=3, high=5) → [3, 1, 2, 4, 8, 6]
      pivot 在索引 3，左边 [3,1,2] < 4，右边 [8,6] > 4
```

### 简洁版本（额外空间，适合理解）

```python
def quicksort_simple(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort_simple(left) + middle + quicksort_simple(right)
```

## 归并排序

### 自顶向下版本

```python
def mergesort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:   # 等号保证稳定性
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])       # 追加剩余元素
    result.extend(right[j:])
    return result
```

**执行过程示例**（[38, 27, 43, 3]）：

```
分割阶段:
[38, 27, 43, 3]
  → [38, 27]        [43, 3]
    → [38] [27]       [43] [3]

合并阶段:
[38] + [27] → [27, 38]
[43] + [3]  → [3, 43]
[27, 38] + [3, 43] → [3, 27, 38, 43]
```

### 原地归并排序（O(1) 额外空间思路）

```python
def mergesort_inplace(arr, left=0, right=None):
    if right is None:
        right = len(arr) - 1
    if left >= right:
        return
    mid = left + (right - left) // 2
    mergesort_inplace(arr, left, mid)
    mergesort_inplace(arr, mid + 1, right)
    merge_inplace(arr, left, mid, right)

def merge_inplace(arr, left, mid, right):
    # 当左半部分的最大值 ≤ 右半部分的最小值时，已经有序
    if arr[mid] <= arr[mid + 1]:
        return
    # 否则执行原地合并（通过插入方式）
    i, j = left, mid + 1
    while i <= mid and j <= right:
        if arr[i] <= arr[j]:
            i += 1
        else:
            temp = arr[j]
            # 将 arr[i..j-1] 右移一位
            for k in range(j, i, -1):
                arr[k] = arr[k - 1]
            arr[i] = temp
            i += 1
            mid += 1
            j += 1
```

## 二分查找

### 标准二分查找

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2  # 防溢出写法
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# 测试
arr = [1, 3, 5, 7, 9, 11]
print(binary_search(arr, 7))   # 3
print(binary_search(arr, 4))   # -1
```

### 查找第一个等于 target 的位置

```python
def find_first(arr, target):
    left, right = 0, len(arr) - 1
    result = -1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            result = mid
            right = mid - 1     # 继续往左找
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result

arr = [1, 2, 2, 2, 3, 4]
print(find_first(arr, 2))  # 1
```

### 查找最后一个等于 target 的位置

```python
def find_last(arr, target):
    left, right = 0, len(arr) - 1
    result = -1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            result = mid
            left = mid + 1      # 继续往右找
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result
```

## 复杂度速查

| 算法 | 平均时间 | 最坏时间 | 空间 | 稳定性 |
|------|---------|---------|------|--------|
| 快速排序 | O(n log n) | O(n^2) | O(log n) | 不稳定 |
| 归并排序 | O(n log n) | O(n log n) | O(n) | 稳定 |
| 二分查找 | O(log n) | O(log n) | O(1) | — |

## 自我检查
1. 快速排序 pivot 的选择如何影响性能？
2. `merge()` 中 `<=` 而非 `<` 为什么能保证稳定性？
3. 二分查找在含重复元素的数组中返回的是哪个位置？

## 下一步建议
学习快速排序的三数取中优化、三路快排，以及搜索旋转排序数组等变体问题。
