# 二分查找边界图解讲解

## 核心概念

### 二分查找基本思想

二分查找（Binary Search）是一种在**有序数组**中快速定位目标元素的算法。通过反复将查找范围减半，时间复杂度为 **O(log n)**，空间复杂度为 **O(1)**（迭代版）。

**算法流程**：
1. 初始化查找范围 `[left, right]`
2. 计算中间位置 `mid = left + (right - left) / 2`
3. 比较 `arr[mid]` 与 `target`：
   - 如果相等，找到目标
   - 如果 `arr[mid] < target`，在右半部分查找
   - 如果 `arr[mid] > target`，在左半部分查找
4. 重复步骤 2-3，直到找到目标或范围为空

### 标准二分查找

查找数组中是否存在目标值 `target`，存在则返回任意一个匹配的索引，不存在则返回 -1。

```cpp
int binarySearch(vector<int>& arr, int target) {
    int left = 0, right = arr.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
```

### 边界查找的两种变体

**lower_bound（左边界）**：查找第一个大于等于 `target` 的位置。

**upper_bound（右边界）**：查找第一个大于 `target` 的位置（即最后一个小于等于 `target` 的位置 + 1）。

### 循环不变量

循环不变量（Loop Invariant）是二分查找的核心思想：
- **区间定义**：`[left, right)` 表示左闭右开区间
- **不变量**：在循环过程中，`[0, left)` 中的元素都 < target，`[right, len)` 中的元素都 >= target
- **终止条件**：当 `left == right` 时，区间为空，`left` 即为答案

### 为什么需要边界查找

| 场景 | 需要的操作 | 示例 |
|------|-----------|------|
| 数组去重 | 找到第一个和最后一个重复元素 | `[1,2,2,2,3]`，找到第一个和最后一个 2 |
| 插入位置 | 找到应该插入的位置 | 在 `[1,3,5]` 中插入 4，应该插入到位置 2 |
| 区间统计 | 统计某个范围内的元素个数 | 统计 `[2,5]` 之间的元素个数 |
| 有序数组查询 | 查找第一个满足条件的元素 | 找到第一个 >= 100 的温度 |

## 过程拆解

### 标准二分查找

**数组**：`arr = [1, 3, 5, 7, 9, 11, 13, 15]`

**目标**：`target = 7`

**步骤**：

```
初始：left = 0, right = 7

步骤1: mid = (0 + 7) / 2 = 3
       arr[3] = 7 == target
       返回索引 3
```

**mid 的安全计算方式**：

- `(left + right) / 2`：在 left 和 right 很大时可能溢出
- `left + (right - left) / 2`：等价但不会溢出，推荐使用

### 查找第一个 >= target 的位置（lower_bound）

**数组**：`arr = [1, 2, 2, 2, 3, 4]`

**目标**：`target = 2`

**步骤**：

```
初始：left = 0, right = 6（数组长度，左闭右开）

步骤1: mid = (0 + 6) / 2 = 3
       arr[3] = 2 >= target
       right = mid = 3  （向左缩，寻找更小的满足条件的位置）
       当前范围：[0, 3)

步骤2: mid = (0 + 3) / 2 = 1
       arr[1] = 2 >= target
       right = mid = 1
       当前范围：[0, 1)

步骤3: mid = (0 + 1) / 2 = 0
       arr[0] = 1 < target
       left = mid + 1 = 1
       当前范围：[1, 1)

步骤4: left == right，退出循环
       返回 left = 1（第一个 >= 2 的位置）
```

### 查找最后一个 <= target 的位置（upper_bound）

**数组**：`arr = [1, 2, 2, 2, 3, 4]`

**目标**：`target = 2`

**步骤**：

```
初始：left = 0, right = 6

步骤1: mid = (0 + 6) / 2 = 3
       arr[3] = 2 <= target
       left = mid + 1 = 4  （向右缩，寻找更大的满足条件的位置）
       当前范围：[4, 6)

步骤2: mid = (4 + 6) / 2 = 5
       arr[5] = 4 > target
       right = mid = 5
       当前范围：[4, 5)

步骤3: mid = (4 + 5) / 2 = 4
       arr[4] = 3 > target
       right = mid = 4
       当前范围：[4, 4)

步骤4: left == right，退出循环
       返回 left - 1 = 3（最后一个 <= 2 的位置）
```

## 状态变化表

### 标准二分查找（找任意一个 2）

**数组**：`arr = [1, 2, 2, 2, 3, 4]`

**目标**：`target = 2`

| 步骤 | left | right | mid | arr[mid] | 比较 | 下一步 |
|------|------|-------|-----|----------|------|--------|
| 1 | 0 | 5 | 2 | 2 | == target | 返回 2 |

### 查找第一个 >= 2 的位置（lower_bound）

| 步骤 | left | right | mid | arr[mid] | 比较 | 更新 |
|------|------|-------|-----|----------|------|------|
| 初始 | 0 | 6 | — | — | — | — |
| 1 | 0 | 6 | 3 | 2 | >= target | right = 3 |
| 2 | 0 | 3 | 1 | 2 | >= target | right = 1 |
| 3 | 0 | 1 | 0 | 1 | < target | left = 1 |
| 结束 | 1 | 1 | — | — | left == right | 返回 left = 1 |

### 查找最后一个 <= 2 的位置（upper_bound）

| 步骤 | left | right | mid | arr[mid] | 比较 | 更新 |
|------|------|-------|-----|----------|------|------|
| 初始 | 0 | 6 | — | — | — | — |
| 1 | 0 | 6 | 3 | 2 | <= target | left = 4 |
| 2 | 4 | 6 | 5 | 4 | > target | right = 5 |
| 3 | 4 | 5 | 4 | 3 | > target | right = 4 |
| 结束 | 4 | 4 | — | — | left == right | 返回 left - 1 = 3 |

### 三种查找方式对比

| 方式 | 返回值含义 | 示例数组 `[1,2,2,2,3,4]` target=2 |
|------|-----------|----------------------------------|
| 标准查找 | 任意一个匹配位置 | 2 |
| lower_bound | 第一个 >= target 的位置 | 1 |
| upper_bound | 第一个 > target 的位置 | 4 |

## 小规模具体例子

### 例子一：标准查找

**数组**：`arr = [1, 3, 5, 7, 9]`

**目标**：`target = 5`

**过程**：

```
left=0, right=4
mid=2, arr[2]=5 == target
返回 2
```

### 例子二：查找第一个 >= 4

**数组**：`arr = [1, 3, 5, 7, 9]`

**目标**：`target = 4`

**过程**：

```
left=0, right=5
mid=2, arr[2]=5 >= 4 → right=2
mid=1, arr[1]=3 < 4 → left=2
left==right, 返回 2（第一个 >= 4 的位置）
```

### 例子三：查找最后一个 <= 6

**数组**：`arr = [1, 3, 5, 7, 9]`

**目标**：`target = 6`

**过程**：

```
left=0, right=5
mid=2, arr[2]=5 <= 6 → left=3
mid=4, arr[4]=9 > 6 → right=4
mid=3, arr[3]=7 > 6 → right=3
left==right, 返回 left-1=2（最后一个 <= 6 的位置）
```

### 例子四：查找不存在的元素

**数组**：`arr = [1, 3, 5, 7, 9]`

**目标**：`target = 10`

**过程**：

```
left=0, right=5
mid=2, arr[2]=5 < 10 → left=3
mid=4, arr[4]=9 < 10 → left=5
left==right, 返回 5（超出数组范围，表示没有元素 >= 10）
```

### 例子五：目标小于最小值

**数组**：`arr = [1, 3, 5, 7, 9]`

**目标**：`target = 0`

**过程**：

```
left=0, right=5
mid=2, arr[2]=5 >= 0 → right=2
mid=1, arr[1]=3 >= 0 → right=1
mid=0, arr[0]=1 >= 0 → right=0
left==right, 返回 0（第一个 >= 0 的位置）
```

## 易错提醒

### 错误一：while 循环条件错误

**错误代码**：

```cpp
// 错误：混用区间定义
int lower_bound(vector<int>& arr, int target) {
    int left = 0, right = arr.size();
    while (left <= right) {  // ❌ 左闭右开应该用 left < right
        int mid = left + (right - left) / 2;
        if (arr[mid] >= target) right = mid;
        else left = mid + 1;
    }
    return left;
}
```

**错误后果**：当 `left == right` 时，循环继续执行，`mid = left = right`，可能导致死循环或数组越界。

**正确做法**：

```cpp
int lower_bound(vector<int>& arr, int target) {
    int left = 0, right = arr.size();
    while (left < right) {  // ✅ 左闭右开用 left < right
        int mid = left + (right - left) / 2;
        if (arr[mid] >= target) right = mid;
        else left = mid + 1;
    }
    return left;
}
```

### 错误二：mid 计算溢出

**错误代码**：

```cpp
int mid = (left + right) / 2;  // ❌ 可能溢出
```

**错误后果**：当 `left` 和 `right` 都是很大的整数时（如 10^9），`left + right` 可能超过 int 的最大值，导致溢出。

**正确做法**：

```cpp
int mid = left + (right - left) / 2;  // ✅ 不会溢出
```

### 错误三：left/right 更新错误

**错误代码**：

```cpp
// lower_bound 的错误更新
if (arr[mid] >= target) {
    right = mid - 1;  // ❌ 可能漏掉第一个匹配位置
}
```

**错误后果**：当 `arr[mid]` 恰好是第一个匹配位置时，`right = mid - 1` 会跳过这个位置，导致返回错误的结果。

**正确做法**：

```cpp
if (arr[mid] >= target) {
    right = mid;  // ✅ 保留当前位置，继续向左寻找
}
```

### 错误四：返回值含义混淆

**错误理解**：

- `lower_bound` 返回第一个 **等于** target 的位置（实际是第一个 **大于等于**）
- `upper_bound` 返回最后一个 **等于** target 的位置（实际是第一个 **大于** target 的位置）

**正确理解**：

| 函数 | 返回值含义 |
|------|-----------|
| lower_bound | 第一个 >= target 的位置 |
| upper_bound | 第一个 > target 的位置 |
| 最后一个 <= target | upper_bound 返回值 - 1 |
| 第一个 == target | 如果 lower_bound 返回的位置的元素 == target，则是该位置；否则不存在 |

### 错误五：数组为空时的处理

**错误代码**：

```cpp
int lower_bound(vector<int>& arr, int target) {
    int left = 0, right = arr.size();
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] >= target) right = mid;
        else left = mid + 1;
    }
    return left;  // 返回 0，但数组为空，可能引起误解
}
```

**正确做法**：

```cpp
int lower_bound(vector<int>& arr, int target) {
    if (arr.empty()) return 0;  // ✅ 单独处理空数组
    int left = 0, right = arr.size();
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] >= target) right = mid;
        else left = mid + 1;
    }
    return left;
}
```

### 错误六：边界条件测试不足

**常见遗漏的测试用例**：

| 测试用例 | 说明 |
|----------|------|
| target < arr[0] | 目标小于最小值 |
| target > arr.back() | 目标大于最大值 |
| target == arr[0] | 目标等于第一个元素 |
| target == arr.back() | 目标等于最后一个元素 |
| 数组只有一个元素 | 长度为 1 的边界 |
| 数组为空 | 空数组处理 |
| 数组中所有元素都相同 | 全重复元素 |

## 小练习

### 练习一：手动模拟 lower_bound

**数组**：`arr = [1, 2, 4, 4, 4, 6, 8, 10]`

**目标**：`target = 4`

**要求**：查找第一个 >= 4 的位置。

**答案要点**：

| 步骤 | left | right | mid | arr[mid] | 比较 | 更新 |
|------|------|-------|-----|----------|------|------|
| 初始 | 0 | 8 | — | — | — | — |
| 1 | 0 | 8 | 4 | 4 | >= target | right = 4 |
| 2 | 0 | 4 | 2 | 4 | >= target | right = 2 |
| 3 | 0 | 2 | 1 | 2 | < target | left = 2 |
| 结束 | 2 | 2 | — | — | left == right | 返回 2 |

**验证**：`arr[2] = 4`，且 `arr[1] = 2 < 4`，所以位置 2 是第一个 >= 4 的位置。

### 练习二：手动模拟 upper_bound

**数组**：`arr = [1, 2, 4, 4, 4, 6, 8, 10]`

**目标**：`target = 4`

**要求**：查找第一个 > 4 的位置。

**答案要点**：

| 步骤 | left | right | mid | arr[mid] | 比较 | 更新 |
|------|------|-------|-----|----------|------|------|
| 初始 | 0 | 8 | — | — | — | — |
| 1 | 0 | 8 | 4 | 4 | <= target | left = 5 |
| 2 | 5 | 8 | 6 | 8 | > target | right = 6 |
| 3 | 5 | 6 | 5 | 6 | > target | right = 5 |
| 结束 | 5 | 5 | — | — | left == right | 返回 5 |

**验证**：`arr[5] = 6`，且 `arr[4] = 4 <= 4`，所以位置 5 是第一个 > 4 的位置。

**最后一个 <= 4 的位置**：`5 - 1 = 4`，`arr[4] = 4`，正确。

### 练习三：边界情况测试

**数组**：`arr = [1, 2, 4, 4, 4, 6, 8, 10]`

**问题**：

1. 如果 `target = 0`，`lower_bound` 返回什么？
2. 如果 `target = 12`，`lower_bound` 返回什么？

**答案要点**：

**问题1：target = 0**

```
left=0, right=8
mid=4, arr[4]=4 >= 0 → right=4
mid=2, arr[2]=4 >= 0 → right=2
mid=1, arr[1]=2 >= 0 → right=1
mid=0, arr[0]=1 >= 0 → right=0
返回 0（第一个 >= 0 的位置）
```

**问题2：target = 12**

```
left=0, right=8
mid=4, arr[4]=4 < 12 → left=5
mid=6, arr[6]=8 < 12 → left=7
mid=7, arr[7]=10 < 12 → left=8
返回 8（超出数组范围，表示没有元素 >= 12）
```

**验证方法**：

- `target = 0`：所有元素都 >= 0，所以第一个位置是 0
- `target = 12`：所有元素都 < 12，所以返回数组长度 8