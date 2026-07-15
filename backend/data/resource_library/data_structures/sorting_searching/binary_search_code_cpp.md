# 二分查找边界代码示例

## 代码目标

本代码演示二分查找的三种常见变体：

**标准二分查找**：查找目标值是否存在，存在返回任意索引，不存在返回 -1。

**lower_bound**：查找第一个大于等于 target 的位置（返回值范围 0 ~ n）。

**upper_bound**：查找第一个大于 target 的位置（返回值范围 0 ~ n）。

通过这三种变体的对比，展示循环条件和左右指针更新规则的不同，帮助理解边界查找的核心逻辑。

## 核心代码

```cpp
#include <iostream>
#include <vector>
using namespace std;

int binarySearch(vector<int>& arr, int target) {
    int left = 0, right = arr.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return -1;
}

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

int upperBound(vector<int>& arr, int target) {
    int left = 0, right = arr.size();
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] > target) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }
    return left;
}

void printArray(const vector<int>& arr) {
    cout << "[";
    for (size_t i = 0; i < arr.size(); i++) {
        if (i > 0) cout << ", ";
        cout << arr[i];
    }
    cout << "]";
}

int main() {
    vector<int> arr = {1, 2, 2, 2, 3, 4};
    
    cout << "数组: ";
    printArray(arr);
    cout << endl << endl;
    
    cout << "=== 标准二分查找 ===" << endl;
    int idx = binarySearch(arr, 2);
    cout << "查找 2: " << (idx != -1 ? "找到索引 " + to_string(idx) : "未找到 (-1)") << endl;
    idx = binarySearch(arr, 5);
    cout << "查找 5: " << (idx != -1 ? "找到索引 " + to_string(idx) : "未找到 (-1)") << endl;
    
    cout << endl << "=== lower_bound (第一个 >= target) ===" << endl;
    cout << "target=2: 位置 " << lowerBound(arr, 2) << endl;
    cout << "target=3: 位置 " << lowerBound(arr, 3) << endl;
    cout << "target=0: 位置 " << lowerBound(arr, 0) << endl;
    cout << "target=5: 位置 " << lowerBound(arr, 5) << endl;
    
    cout << endl << "=== upper_bound (第一个 > target) ===" << endl;
    cout << "target=2: 位置 " << upperBound(arr, 2) << endl;
    cout << "target=3: 位置 " << upperBound(arr, 3) << endl;
    cout << "target=0: 位置 " << upperBound(arr, 0) << endl;
    cout << "target=5: 位置 " << upperBound(arr, 5) << endl;
    
    return 0;
}
```

## 关键步骤解释

### 标准二分查找

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

**解释**：
- **循环条件**：`left <= right`，表示区间 `[left, right]` 是左闭右闭的，当 `left > right` 时区间为空
- **更新规则**：
  - `arr[mid] < target`：目标在右半部分，`left = mid + 1`（跳过 mid）
  - `arr[mid] > target`：目标在左半部分，`right = mid - 1`（跳过 mid）
- **返回值**：找到返回索引，未找到返回 -1

### lower_bound

```cpp
int lowerBound(vector<int>& arr, int target) {
    int left = 0, right = arr.size();
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] >= target) right = mid;
        else left = mid + 1;
    }
    return left;
}
```

**解释**：
- **循环条件**：`left < right`，表示区间 `[left, right)` 是左闭右开的
- **更新规则**：
  - `arr[mid] >= target`：找到满足条件的位置，但可能有更小的满足条件的位置，所以 `right = mid`（保留 mid）
  - `arr[mid] < target`：目标在右半部分，`left = mid + 1`（跳过 mid）
- **返回值**：第一个 >= target 的位置，范围是 0 ~ n

### upper_bound

```cpp
int upperBound(vector<int>& arr, int target) {
    int left = 0, right = arr.size();
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] > target) right = mid;
        else left = mid + 1;
    }
    return left;
}
```

**解释**：
- **循环条件**：`left < right`，表示区间 `[left, right)` 是左闭右开的
- **更新规则**：
  - `arr[mid] > target`：找到满足条件的位置，但可能有更小的满足条件的位置，所以 `right = mid`（保留 mid）
  - `arr[mid] <= target`：目标在右半部分，`left = mid + 1`（跳过 mid）
- **返回值**：第一个 > target 的位置，范围是 0 ~ n

### 三种变体对比表

| 对比项 | 标准二分查找 | lower_bound | upper_bound |
|--------|------------|-------------|-------------|
| 循环条件 | `left <= right` | `left < right` | `left < right` |
| right 初始值 | `n - 1` | `n` | `n` |
| 找到相等时 | 返回 mid | `right = mid` | `left = mid + 1` |
| 目标在左边 | `right = mid - 1` | `right = mid` | `right = mid` |
| 目标在右边 | `left = mid + 1` | `left = mid + 1` | `left = mid + 1` |
| 返回值含义 | 任意匹配索引或 -1 | 第一个 >= target 的位置 | 第一个 > target 的位置 |
| 返回值范围 | -1 ~ n-1 | 0 ~ n | 0 ~ n |

### 为什么使用左闭右开区间

**原因**：

1. **统一处理边界**：当 target 大于所有元素时，返回 n（数组长度），表示应该插入到数组末尾
2. **简化逻辑**：`left == right` 时循环终止，不需要额外判断
3. **语义清晰**：`[left, right)` 表示 left 是当前搜索范围的起点，right 是终点（不包含）

## 输入输出示例

运行上述代码，输出结果为：

```
数组: [1, 2, 2, 2, 3, 4]

=== 标准二分查找 ===
查找 2: 找到索引 2
查找 5: 未找到 (-1)

=== lower_bound (第一个 >= target) ===
target=2: 位置 1
target=3: 位置 4
target=0: 位置 0
target=5: 位置 6

=== upper_bound (第一个 > target) ===
target=2: 位置 4
target=3: 位置 5
target=0: 位置 0
target=5: 位置 6
```

**结果分析**：

| 函数 | target=2 | target=3 | target=0 | target=5 |
|------|----------|----------|----------|----------|
| binarySearch | 返回索引 2（任意一个 2） | 返回索引 4 | 返回 -1（不存在） | 返回 -1（不存在） |
| lower_bound | 返回 1（第一个 >= 2） | 返回 4（第一个 >= 3） | 返回 0（第一个 >= 0） | 返回 6（所有元素 < 5） |
| upper_bound | 返回 4（第一个 > 2） | 返回 5（第一个 > 3） | 返回 0（第一个 > 0） | 返回 6（所有元素 <= 5） |

## 边界条件

### 空数组

```cpp
vector<int> arr;
binarySearch(arr, 5);    // 返回 -1
lowerBound(arr, 5);      // 返回 0
upperBound(arr, 5);      // 返回 0
```

### 数组所有元素都小于 target

```cpp
vector<int> arr = {1, 2, 3};
lowerBound(arr, 4);      // 返回 3（n）
upperBound(arr, 4);      // 返回 3（n）
```

### 数组所有元素都大于 target

```cpp
vector<int> arr = {1, 2, 3};
lowerBound(arr, 0);      // 返回 0
upperBound(arr, 0);      // 返回 0
```

### 数组中全是 target

```cpp
vector<int> arr = {5, 5, 5, 5};
lowerBound(arr, 5);      // 返回 0（第一个 >= 5）
upperBound(arr, 5);      // 返回 4（第一个 > 5）
```

### 目标值不存在但位于数组范围内

```cpp
vector<int> arr = {1, 3, 5};
lowerBound(arr, 4);      // 返回 2（第一个 >= 4 的位置，即 5 的位置）
upperBound(arr, 4);      // 返回 2（第一个 > 4 的位置，即 5 的位置）
```

## 时间复杂度和空间复杂度

### 时间复杂度

**O(log n)**，每次将搜索区间缩小一半，最多需要 log₂(n) 次比较。

```
n = 8: 需要 3 次比较（8 → 4 → 2 → 1）
n = 16: 需要 4 次比较（16 → 8 → 4 → 2 → 1）
n = 1000: 需要约 10 次比较
```

### 空间复杂度

**迭代版本**：O(1)，只使用常数个变量（left, right, mid）。

**递归版本**：O(log n)，递归调用栈的深度为 log₂(n)。

```cpp
// 递归版本的空间复杂度分析
int binarySearchRecursive(vector<int>& arr, int left, int right, int target) {
    if (left > right) return -1;
    int mid = left + (right - left) / 2;
    if (arr[mid] == target) return mid;
    else if (arr[mid] < target) return binarySearchRecursive(arr, mid+1, right, target);
    else return binarySearchRecursive(arr, left, mid-1, target);
}
```

## 改写练习

### 练习一：递归实现标准二分查找

```cpp
int binarySearchRecursive(vector<int>& arr, int left, int right, int target) {
    if (left > right) return -1;
    int mid = left + (right - left) / 2;
    if (arr[mid] == target) return mid;
    else if (arr[mid] < target) return binarySearchRecursive(arr, mid + 1, right, target);
    else return binarySearchRecursive(arr, left, mid - 1, target);
}

int main() {
    vector<int> arr = {1, 2, 3, 4, 5};
    cout << binarySearchRecursive(arr, 0, arr.size() - 1, 3) << endl;  // 输出 2
    return 0;
}
```

**空间复杂度**：O(log n)，递归调用栈深度为 log₂(n)。

### 练习二：统计目标值出现次数

```cpp
int countOccurrences(vector<int>& arr, int target) {
    int first = lowerBound(arr, target);
    int last = upperBound(arr, target);
    return last - first;
}

int main() {
    vector<int> arr = {1, 2, 2, 2, 3, 4};
    cout << countOccurrences(arr, 2) << endl;  // 输出 3
    return 0;
}
```

### 练习三：查找插入位置

```cpp
int findInsertPosition(vector<int>& arr, int target) {
    return lowerBound(arr, target);
}

int main() {
    vector<int> arr = {1, 3, 5};
    cout << findInsertPosition(arr, 4) << endl;  // 输出 2
    return 0;
}
```

### 练习四：支持自定义比较函数

```cpp
template<typename Predicate>
int findFirstTrue(vector<int>& arr, Predicate pred) {
    int left = 0, right = arr.size();
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (pred(arr[mid])) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }
    return left;
}

int main() {
    vector<int> arr = {1, 2, 3, 4, 5};
    // 查找第一个 >= 3 的位置
    int pos = findFirstTrue(arr, [](int x) { return x >= 3; });
    cout << pos << endl;  // 输出 2
    return 0;
}
```