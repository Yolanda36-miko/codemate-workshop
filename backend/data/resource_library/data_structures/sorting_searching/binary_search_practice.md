# 二分查找边界分层练习题

## 基础题

### 基础题一

**题目描述**

给定有序数组 `arr = [1, 3, 5, 7, 9, 11, 13]`，目标 `target = 7`。手动模拟标准二分查找，写出每一步的 left、right、mid 和 arr[mid] 的值，直到找到目标或确定不存在。

### 基础题二

**题目描述**

给定有序数组 `arr = [2, 4, 6, 8, 10, 12]`，分别计算以下 target 的 lower_bound（第一个 >= target 的位置）：

a) target = 6
b) target = 7
c) target = 1
d) target = 14

要求写出结果并简要说明理由。

## 进阶题

### 进阶题一

**题目描述**

补全以下 lower_bound 代码中的空缺部分（用 `___` 标记）：

```cpp
int lowerBound(vector<int>& arr, int target) {
    int left = 0, right = arr.size();
    while (___ < ___) {
        int mid = left + (right - left) / 2;
        if (arr[mid] ___ target) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }
    return ___;
}
```

并说明如果数组为空，这个函数会返回什么。

### 进阶题二

**题目描述**

给定一个有序数组 `arr = [1, 2, 2, 3, 3, 3, 4, 5]`，请利用 lower_bound 和 upper_bound 计算以下目标值出现的次数：

a) target = 2
b) target = 3
c) target = 6

写出计算过程和结果。

### 进阶题三

**题目描述**

给定一个有序数组 `arr = [1, 3, 5, 7, 9]`，设计一个算法查找目标值的插入位置，使得插入后数组仍然有序。要求：

- 写出核心算法伪代码。
- 说明为什么插入位置可以用 lower_bound 实现。
- 分析时间复杂度。

## 综合题

### 综合题一

**题目描述**

给定一个整数数组 `nums`（可能包含重复元素），要求实现一个函数 `searchRange`，返回目标值在数组中的起始位置和结束位置。如果不存在，返回 `[-1, -1]`。例如 `nums = [5, 7, 7, 8, 8, 10]`，`target = 8`，返回 `[3, 4]`。要求：

- 说明为什么这个问题可以用二分查找的边界变体解决。
- 写出核心算法伪代码（利用 lower_bound 和 upper_bound）。
- 分析时间复杂度。

### 综合题二

**题目描述**

给定一个按升序排序的数组，数组在某个未知位置进行了旋转（例如 `[0,1,2,4,5,6,7]` 可能变为 `[4,5,6,7,0,1,2]`）。要求实现一个函数 `search`，在旋转数组中查找目标值。如果存在返回 true，否则返回 false。要求：

- 说明如何利用二分查找的思想解决这个问题。
- 写出核心算法伪代码。
- 分析时间复杂度为 O(log n) 的关键条件。

## 每题提示

### 基础题一提示

标准二分查找使用 `left <= right` 的循环条件，每次将搜索范围缩小一半。注意 mid 的计算方式和 left/right 的更新规则。

### 基础题二提示

lower_bound 返回第一个 >= target 的位置。当 target 小于所有元素时返回 0，当 target 大于所有元素时返回数组长度。

### 进阶题一提示

左闭右开区间 `[left, right)` 使用 `left < right` 的循环条件。当 `arr[mid] >= target` 时需要保留 mid，所以 `right = mid`。

### 进阶题二提示

出现次数 = upper_bound 返回值 - lower_bound 返回值。注意处理目标值不存在的情况。

### 进阶题三提示

插入位置就是第一个 >= target 的位置，这正是 lower_bound 的定义。

### 综合题一提示

起始位置 = lower_bound 返回的位置，结束位置 = upper_bound 返回的位置 - 1。需要检查目标值是否存在。

### 综合题二提示

旋转数组的特点是：至少有一半是有序的。比较 mid 和 left/right 的值，判断哪一半有序，然后在有序的一半中查找。

## 每题检查标准

### 基础题一检查标准

每一步的 left、right、mid 计算正确，最终找到目标值或确定不存在。

### 基础题二检查标准

四个 lower_bound 的返回值正确，理由清晰合理。

### 进阶题一检查标准

代码补全后能正确运行，空数组情况的返回值正确。

### 进阶题二检查标准

三次出现次数计算正确，计算过程清晰。

### 进阶题三检查标准

伪代码正确，说明清楚，时间复杂度分析准确。

### 综合题一检查标准

算法思路正确，伪代码能解决问题，时间复杂度分析准确。

### 综合题二检查标准

算法思路正确，伪代码能解决问题，复杂度分析准确。

## 可选答案要点

### 基础题一答案

**步骤状态**：

| 步骤 | left | right | mid | arr[mid] | 比较 | 更新 |
|------|------|-------|-----|----------|------|------|
| 初始 | 0 | 6 | — | — | — | — |
| 1 | 0 | 6 | 3 | 7 | == target | 返回 3 |

**最终结果**：在索引 3 处找到目标值 7。

### 基础题二答案

**数组**：`arr = [2, 4, 6, 8, 10, 12]`（长度 6）

| target | lower_bound 返回值 | 理由 |
|--------|-------------------|------|
| a) 6 | 2 | arr[2] = 6，是第一个 >= 6 的位置 |
| b) 7 | 3 | arr[2] = 6 < 7，arr[3] = 8 >= 7，所以返回 3 |
| c) 1 | 0 | 所有元素都 >= 1，返回第一个位置 0 |
| d) 14 | 6 | 所有元素都 < 14，返回数组长度 6 |

### 进阶题一答案

**补全代码**：

```cpp
int lowerBound(vector<int>& arr, int target) {
    int left = 0, right = arr.size();
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] >= target) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }
    return left;
}
```

**空缺解析**：
1. `left < right`：循环条件，左闭右开区间
2. `>=`：当 arr[mid] >= target 时，需要向左寻找更小的满足条件的位置
3. `left`：循环结束时 left == right，返回 left

**空数组情况**：

当数组为空时，`arr.size() = 0`，所以 `left = 0, right = 0`，循环条件 `0 < 0` 不成立，直接返回 0。

### 进阶题二答案

**数组**：`arr = [1, 2, 2, 3, 3, 3, 4, 5]`（长度 8）

**a) target = 2**

```
lower_bound(2)：第一个 >= 2 的位置
left=0, right=8, mid=4, arr[4]=3 >= 2 → right=4
left=0, right=4, mid=2, arr[2]=2 >= 2 → right=2
left=0, right=2, mid=1, arr[1]=2 >= 2 → right=1
left=0, right=1, mid=0, arr[0]=1 < 2 → left=1
返回 1

upper_bound(2)：第一个 > 2 的位置
left=0, right=8, mid=4, arr[4]=3 > 2 → right=4
left=0, right=4, mid=2, arr[2]=2 <= 2 → left=3
left=3, right=4, mid=3, arr[3]=3 > 2 → right=3
返回 3

出现次数 = 3 - 1 = 2
```

**b) target = 3**

```
lower_bound(3)：第一个 >= 3 的位置
left=0, right=8, mid=4, arr[4]=3 >= 3 → right=4
left=0, right=4, mid=2, arr[2]=2 < 3 → left=3
left=3, right=4, mid=3, arr[3]=3 >= 3 → right=3
返回 3

upper_bound(3)：第一个 > 3 的位置
left=0, right=8, mid=4, arr[4]=3 <= 3 → left=5
left=5, right=8, mid=6, arr[6]=4 > 3 → right=6
left=5, right=6, mid=5, arr[5]=3 <= 3 → left=6
返回 6

出现次数 = 6 - 3 = 3
```

**c) target = 6**

```
lower_bound(6)：第一个 >= 6 的位置
left=0, right=8, mid=4, arr[4]=3 < 6 → left=5
left=5, right=8, mid=6, arr[6]=4 < 6 → left=7
left=7, right=8, mid=7, arr[7]=5 < 6 → left=8
返回 8

upper_bound(6)：第一个 > 6 的位置
left=0, right=8, mid=4, arr[4]=3 <= 6 → left=5
left=5, right=8, mid=6, arr[6]=4 <= 6 → left=7
left=7, right=8, mid=7, arr[7]=5 <= 6 → left=8
返回 8

出现次数 = 8 - 8 = 0（目标不存在）
```

**结果汇总**：

| target | lower_bound | upper_bound | 出现次数 |
|--------|------------|------------|----------|
| 2 | 1 | 3 | 2 |
| 3 | 3 | 6 | 3 |
| 6 | 8 | 8 | 0 |

### 进阶题三答案

**核心算法伪代码**：

```
function searchInsert(arr, target):
    left = 0
    right = length(arr)
    while left < right:
        mid = left + (right - left) / 2
        if arr[mid] >= target:
            right = mid
        else:
            left = mid + 1
    return left
```

**为什么可以用 lower_bound 实现**：

插入位置的定义是：找到第一个大于等于 target 的位置，将 target 插入到该位置。这正是 lower_bound 的定义。

- 如果 target 存在于数组中，插入位置就是第一个出现的位置
- 如果 target 不存在，插入位置就是第一个大于 target 的位置
- 如果 target 小于所有元素，插入位置是 0
- 如果 target 大于所有元素，插入位置是数组长度

**时间复杂度**：O(log n)，每次将搜索范围缩小一半。

### 综合题一答案

**为什么可以用二分查找的边界变体解决**：

- 起始位置 = 第一个 >= target 的位置（lower_bound）
- 结束位置 = 最后一个 <= target 的位置 = 第一个 > target 的位置 - 1（upper_bound - 1）
- 通过两次二分查找可以在 O(log n) 时间内找到结果

**核心算法伪代码**：

```
function searchRange(nums, target):
    left = lower_bound(nums, target)
    if left == length(nums) or nums[left] != target:
        return [-1, -1]
    
    right = upper_bound(nums, target) - 1
    return [left, right]

function lower_bound(nums, target):
    left = 0, right = length(nums)
    while left < right:
        mid = left + (right - left) / 2
        if nums[mid] >= target:
            right = mid
        else:
            left = mid + 1
    return left

function upper_bound(nums, target):
    left = 0, right = length(nums)
    while left < right:
        mid = left + (right - left) / 2
        if nums[mid] > target:
            right = mid
        else:
            left = mid + 1
    return left
```

**时间复杂度**：O(log n)，两次二分查找，每次 O(log n)。

**示例验证**：

`nums = [5, 7, 7, 8, 8, 10]`，`target = 8`

```
lower_bound(8)：返回 3（第一个 >= 8 的位置）
upper_bound(8)：返回 5（第一个 > 8 的位置）
结束位置 = 5 - 1 = 4
返回 [3, 4]
```

### 综合题二答案

**如何利用二分查找的思想**：

旋转数组的特点是：至少有一半是有序的。通过比较 `nums[mid]` 和 `nums[left]` 或 `nums[right]`，可以判断哪一半是有序的。如果目标值在有序的范围内，则在该范围内继续二分查找；否则在无序的一半继续查找。

**核心算法伪代码**：

```
function search(nums, target):
    left = 0, right = length(nums) - 1
    
    while left <= right:
        mid = left + (right - left) / 2
        
        if nums[mid] == target:
            return true
        
        if nums[left] == nums[mid] and nums[mid] == nums[right]:
            left += 1
            right -= 1
            continue
        
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    
    return false
```

**时间复杂度分析**：

- **O(log n)**：当数组中没有重复元素时，可以每次将搜索范围缩小一半
- **O(n)**：当数组中有大量重复元素时（如 `nums[left] == nums[mid] == nums[right]`），需要逐个移动指针，退化为线性查找

**O(log n) 的关键条件**：

数组中没有重复元素，或者重复元素的比例很小，可以快速排除。

**示例验证**：

`nums = [4,5,6,7,0,1,2]`，`target = 0`

```
left=0, right=6, mid=3
nums[mid]=7 != 0
nums[left]=4 <= nums[mid]=7（左半部分有序）
nums[left]=4 <= 0 < nums[mid]=7？否
left = mid + 1 = 4

left=4, right=6, mid=5
nums[mid]=1 != 0
nums[left]=0 <= nums[mid]=1（左半部分有序）
nums[left]=0 <= 0 < nums[mid]=1？是
right = mid - 1 = 4

left=4, right=4, mid=4
nums[mid]=0 == target，返回 true
```