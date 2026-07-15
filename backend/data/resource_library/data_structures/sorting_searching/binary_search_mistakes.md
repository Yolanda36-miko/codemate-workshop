# 二分查找边界易错点总结

## 常见错误

### 错误一：while 循环条件混淆

将 `left < right` 和 `left <= right` 混用，导致死循环或漏解。

### 错误二：mid 计算溢出

使用 `(left + right) / 2` 计算中间位置，当 left 和 right 都是很大的整数时可能溢出。

### 错误三：left/right 更新错误

在 lower_bound 中应 `right = mid` 却写成 `right = mid - 1`，导致跳过目标位置。

### 错误四：返回值含义混淆

将 lower_bound 返回的位置错误地视为"目标是否存在"，忽略了返回值可能等于数组长度的情况。

### 错误五：数组为空时未处理

直接调用 lower_bound/upper_bound 导致返回 0，但 0 可能被误解为有效位置。

### 错误六：边界条件理解错误

目标值小于所有元素或大于所有元素时，返回值未正确理解和处理。

## 错误原因

### 错误一原因

对二分查找的区间定义理解不足，不清楚 `[left, right]`（左闭右闭）和 `[left, right)`（左闭右开）的区别，以及对应的循环条件和更新规则。

### 错误二原因

对整数溢出问题缺乏认识，不知道两个大整数相加可能超过 int 类型的最大值（约 2×10⁹）。

### 错误三原因

对 lower_bound 的核心逻辑理解不深，不知道 `arr[mid] >= target` 时需要保留 mid 继续向左寻找，而不是跳过。

### 错误四原因

对 lower_bound 和 upper_bound 的返回值语义理解不清晰，不知道它们返回的是位置而非"是否找到"。

### 错误五原因

对边界情况考虑不周全，只测试了正常情况，忽略了空数组这种极端情况。

### 错误六原因

对二分查找的终止条件和返回值范围理解不完整，不知道返回值可以等于数组长度。

## 正确理解

### 区间定义与循环条件

| 区间定义 | 循环条件 | left/right 更新 | 适用场景 |
|----------|----------|----------------|----------|
| `[left, right]`（左闭右闭） | `left <= right` | `left = mid + 1`, `right = mid - 1` | 标准二分查找（找是否存在） |
| `[left, right)`（左闭右开） | `left < right` | `left = mid + 1`, `right = mid` | lower_bound/upper_bound |

### mid 的安全计算方式

```cpp
// 错误方式：可能溢出
int mid = (left + right) / 2;

// 正确方式：不会溢出
int mid = left + (right - left) / 2;
```

**原理**：`right - left` 的最大值是 n，远小于 `left + right` 的最大值 2n。

### lower_bound 和 upper_bound 的返回值语义

| 函数 | 返回值含义 | 返回值范围 |
|------|-----------|-----------|
| lower_bound | 第一个 >= target 的位置 | 0 ~ n |
| upper_bound | 第一个 > target 的位置 | 0 ~ n |
| 最后一个 <= target | upper_bound 返回值 - 1 | -1 ~ n-1 |

### 边界条件处理

| 场景 | lower_bound 返回值 | upper_bound 返回值 |
|------|-------------------|-------------------|
| target < arr[0] | 0 | 0 |
| target > arr.back() | n | n |
| target 在数组范围内但不存在 | 第一个 >= target 的位置 | 第一个 > target 的位置 |
| 数组为空 | 0 | 0 |

## 错误例子

### 错误一：while 循环条件混淆

**错误代码**：

```cpp
int lowerBound(vector<int>& arr, int target) {
    int left = 0, right = arr.size();
    while (left <= right) {  // ❌ 左闭右开应该用 left < right
        int mid = left + (right - left) / 2;
        if (arr[mid] >= target) right = mid;
        else left = mid + 1;
    }
    return left;
}
```

**错误后果**：当 `left == right` 时，循环继续执行，`mid = left = right`，如果 `arr[mid] >= target`，则 `right = mid`，导致死循环。

**正确代码**：

```cpp
int lowerBound(vector<int>& arr, int target) {
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
int binarySearch(vector<int>& arr, int target) {
    int left = 0, right = arr.size() - 1;
    while (left <= right) {
        int mid = (left + right) / 2;  // ❌ 可能溢出
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
```

**错误后果**：当 `left = 10⁹` 且 `right = 10⁹` 时，`left + right = 2×10⁹`，超过 int 的最大值（约 2.1×10⁹），导致溢出。

**正确代码**：

```cpp
int binarySearch(vector<int>& arr, int target) {
    int left = 0, right = arr.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;  // ✅ 不会溢出
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
```

### 错误三：left/right 更新错误

**错误代码**：

```cpp
int lowerBound(vector<int>& arr, int target) {
    int left = 0, right = arr.size();
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] >= target) {
            right = mid - 1;  // ❌ 跳过了可能的目标位置
        } else {
            left = mid + 1;
        }
    }
    return left;
}
```

**错误后果**：假设数组 `[1, 2, 2, 2, 3]`，target = 2。当 mid = 1 时，`arr[1] = 2 >= 2`，执行 `right = 0`，跳过了正确的位置 1，最终返回 0，错误。

**正确代码**：

```cpp
int lowerBound(vector<int>& arr, int target) {
    int left = 0, right = arr.size();
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] >= target) {
            right = mid;  // ✅ 保留当前位置，继续向左寻找
        } else {
            left = mid + 1;
        }
    }
    return left;
}
```

### 错误四：返回值含义混淆

**错误代码**：

```cpp
bool containsTarget(vector<int>& arr, int target) {
    int pos = lowerBound(arr, target);
    return pos != -1;  // ❌ lower_bound 永远不会返回 -1
}
```

**错误后果**：`lower_bound` 返回的是位置（0 ~ n），永远不会返回 -1，所以这个函数总是返回 true。

**正确代码**：

```cpp
bool containsTarget(vector<int>& arr, int target) {
    int pos = lowerBound(arr, target);
    return pos < arr.size() && arr[pos] == target;  // ✅ 检查位置是否有效且元素相等
}
```

### 错误五：数组为空时未处理

**错误代码**：

```cpp
int findInsertPosition(vector<int>& arr, int target) {
    return lowerBound(arr, target);  // ❌ 空数组返回 0，可能引起误解
}
```

**错误后果**：当数组为空时，返回 0，但 0 可能被误解为"插入到位置 0"，而实际上空数组只有一个插入位置。

**正确代码**：

```cpp
int findInsertPosition(vector<int>& arr, int target) {
    if (arr.empty()) return 0;  // ✅ 单独处理空数组，明确表示插入位置
    return lowerBound(arr, target);
}
```

### 错误六：边界条件理解错误

**错误代码**：

```cpp
int getLastIndex(vector<int>& arr, int target) {
    int pos = upperBound(arr, target);
    return pos;  // ❌ 返回的是第一个 > target 的位置，不是最后一个 <= target 的位置
}
```

**错误后果**：假设数组 `[1, 2, 2, 2, 3]`，target = 2。`upperBound` 返回 4（第一个 > 2 的位置），但最后一个 <= 2 的位置是 3。

**正确代码**：

```cpp
int getLastIndex(vector<int>& arr, int target) {
    int pos = upperBound(arr, target);
    return pos - 1;  // ✅ 返回最后一个 <= target 的位置
}
```

## 错误与正确做法对比表

| 错误类型 | 错误做法 | 正确做法 |
|----------|----------|----------|
| 循环条件混淆 | `left <= right`（左闭右开） | `left < right`（左闭右开） |
| mid 计算溢出 | `(left + right) / 2` | `left + (right - left) / 2` |
| left/right 更新错误 | `right = mid - 1`（lower_bound） | `right = mid`（lower_bound） |
| 返回值含义混淆 | `pos != -1` 判断是否存在 | `pos < n && arr[pos] == target` |
| 空数组未处理 | 直接调用 lower_bound | 单独判断 `arr.empty()` |
| 边界条件理解错误 | upper_bound 返回值直接使用 | upper_bound 返回值 - 1 |

## 自查题

### 题目一

**题目描述**：

以下是一个 lower_bound 的错误实现：

```cpp
int lowerBound(vector<int>& arr, int target) {
    int left = 0, right = arr.size();
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] >= target) {
            right = mid - 1;  // 错误！
        } else {
            left = mid + 1;
        }
    }
    return left;
}
```

**问题**：

1. 指出错误所在，并说明为什么是错误的。
2. 给出修正后的代码。
3. 举例说明在什么情况下会出错。

**答案要点**：

1. **错误**：`right = mid - 1` 会跳过可能的目标位置。当 `arr[mid] >= target` 时，mid 可能就是第一个满足条件的位置，跳过它会导致返回错误的结果。

2. **修正代码**：

```cpp
int lowerBound(vector<int>& arr, int target) {
    int left = 0, right = arr.size();
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] >= target) {
            right = mid;  // 保留当前位置
        } else {
            left = mid + 1;
        }
    }
    return left;
}
```

3. **出错情况**：

当数组中有多个重复的 target 时，例如 `arr = [1, 2, 2, 2, 3]`，target = 2。

- 步骤1：left=0, right=5, mid=2, arr[2]=2 >= 2, right = mid-1 = 1
- 步骤2：left=0, right=1, mid=0, arr[0]=1 < 2, left = 1
- 返回 1，看起来正确？让我们再看一个例子：

当 `arr = [2, 2, 2, 2]`，target = 2：

- 步骤1：left=0, right=4, mid=2, arr[2]=2 >= 2, right = mid-1 = 1
- 步骤2：left=0, right=1, mid=0, arr[0]=2 >= 2, right = mid-1 = -1
- 返回 0，看起来正确？

再看一个例子：`arr = [1, 3, 3, 3, 5]`，target = 3：

- 步骤1：left=0, right=5, mid=2, arr[2]=3 >= 3, right = mid-1 = 1
- 步骤2：left=0, right=1, mid=0, arr[0]=1 < 3, left = 1
- 返回 1，但正确答案应该是 1（第一个 >= 3 的位置），看起来正确？

**真正出错的情况**：当 target 恰好在数组的第一个位置时：

`arr = [2, 3, 4, 5]`，target = 2：

- 步骤1：left=0, right=4, mid=2, arr[2]=4 >= 2, right = mid-1 = 1
- 步骤2：left=0, right=1, mid=0, arr[0]=2 >= 2, right = mid-1 = -1
- 返回 0，正确。

**另一个出错情况**：`arr = [1, 2, 4, 5]`，target = 3：

- 步骤1：left=0, right=4, mid=2, arr[2]=4 >= 3, right = mid-1 = 1
- 步骤2：left=0, right=1, mid=0, arr[0]=1 < 3, left = 1
- 返回 1，但正确答案应该是 2（第一个 >= 3 的位置是索引 2 的 4）。

**验证方法**：在数组 `[1, 2, 4, 5]` 中查找第一个 >= 3 的位置，正确答案是 2（元素 4），但错误代码返回 1（元素 2），验证了错误。

### 题目二

**题目描述**：

设计一个函数，返回目标值在有序数组中的插入位置（保持数组有序）。例如：

- `arr = [1, 3, 5]`，target = 4，返回 2
- `arr = [1, 3, 5]`，target = 0，返回 0
- `arr = [1, 3, 5]`，target = 6，返回 3

**问题**：

1. 写出正确的二分查找代码。
2. 说明使用哪种区间定义。
3. 解释为什么这样定义是正确的。

**答案要点**：

1. **正确代码**：

```cpp
int searchInsert(vector<int>& arr, int target) {
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

2. **区间定义**：`[left, right)` 左闭右开区间。

3. **解释**：

- 当 `arr[mid] >= target` 时，说明插入位置在 mid 或其左边，所以 `right = mid`（保留 mid）
- 当 `arr[mid] < target` 时，说明插入位置在 mid 的右边，所以 `left = mid + 1`（跳过 mid）
- 循环结束时 `left == right`，此时 left 就是第一个 >= target 的位置，也就是应该插入的位置

**验证方法**：测试 `arr = [1, 3, 5]`，target = 4：

- left=0, right=3, mid=1, arr[1]=3 < 4, left = 2
- left=2, right=3, mid=2, arr[2]=5 >= 4, right = 2
- 返回 2，正确。

### 题目三

**题目描述**：

分析以下说法是否正确："二分查找的 mid 用 `(left + right) / 2` 计算总是安全的，因为 left 和 right 都是 int 类型。"

**问题**：

1. 判断说法是否正确。
2. 说明理由。
3. 给出安全的计算方式。

**答案要点**：

1. **不正确**。

2. **理由**：

- int 类型的最大值约为 2.1×10⁹
- 当 left 和 right 都接近最大值时（如都为 10⁹），`left + right = 2×10⁹`，超过 int 的最大值
- 整数溢出会导致 mid 值变为负数或其他错误值
- 在 64 位系统中，int 仍然是 32 位，所以同样存在溢出问题

3. **安全的计算方式**：

```cpp
int mid = left + (right - left) / 2;
```

**原理**：

- `right - left` 的最大值是 n（数组长度），通常远小于 2×10⁹
- 即使 n = 10⁹，`left + (right - left) / 2` 也不会超过 10⁹ + 5×10⁸ = 1.5×10⁹，小于 int 的最大值

**验证方法**：

```cpp
int left = 1000000000;
int right = 1000000000;

int mid1 = (left + right) / 2;           // 可能溢出
int mid2 = left + (right - left) / 2;    // 安全

cout << "mid1: " << mid1 << endl;  // 可能输出负数或错误值
cout << "mid2: " << mid2 << endl;  // 输出 1000000000，正确
```