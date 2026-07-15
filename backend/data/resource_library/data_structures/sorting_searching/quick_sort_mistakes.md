# 快速排序与稳定性易错点总结

## 常见错误

### 错误一：递归边界条件写错

将 `low >= high` 写成 `low > high`，或漏掉边界判断导致无限递归。

### 错误二：partition 循环条件写错

循环条件使用不当（例如用 `<=` 还是 `<`），或指针初始值、移动顺序不正确。

### 错误三：误以为快速排序是稳定的

对稳定性定义理解不清，认为相等元素顺序无关紧要。

### 错误四：忽略 pivot 选择对性能的影响

在有序数组上使用最左/最右 pivot，导致时间复杂度退化到 O(n²)。

### 错误五：递归深度过大导致栈溢出

没有考虑最坏情况下的递归深度，导致栈溢出。

### 错误六：处理重复元素时逻辑错误

在 partition 中处理等于 pivot 的元素时，指针移动逻辑错误。

## 错误原因

### 错误一原因

对递归终止条件理解不足，没有意识到 `low == high` 时也应该返回（单元素数组不需要排序）。

### 错误二原因

对分区循环中指针移动逻辑理解不清，不知道 `i` 和 `j` 的含义和移动顺序。

### 错误三原因

对稳定性定义不准确，不理解相等元素的相对顺序在实际应用中的重要性。

### 错误四原因

对快速排序的性能分析不够深入，不了解不同 pivot 选择策略对性能的影响。

### 错误五原因

没有考虑递归调用栈的深度限制，尤其是在最坏情况下（数组有序或逆序）。

### 错误六原因

对等于 pivot 的元素处理方式不明确，不知道应该将其分到左边还是右边。

## 正确理解

### 递归边界条件

当 `low >= high` 时，子数组为空或只有一个元素，不需要排序，应直接返回。

### Partition 循环条件

- Lomuto 方案：`j` 从 `low` 到 `high-1`（不包括 pivot）
- Hoare 方案：`i` 和 `j` 从两端向中间移动，直到 `i >= j`

### 稳定性定义

排序后，相等元素的原始相对顺序保持不变。快速排序是不稳定的。

### Pivot 选择策略

- 随机选择：减少最坏情况概率
- 三数取中：避免有序数组的最坏情况
- 中位数：最优但计算成本高

### 递归深度

- 平均情况：O(log n)
- 最坏情况：O(n)（有序数组）

### 重复元素处理

等于 pivot 的元素可以分到左边或右边，但必须保持一致的处理方式。

## 错误例子

### 错误一：递归边界条件写错

**错误代码**：

```cpp
void quickSort(int arr[], int low, int high) {
    if (low > high) return;  // 错误：应该是 >=
    int pivotPos = partition(arr, low, high);
    quickSort(arr, low, pivotPos - 1);
    quickSort(arr, pivotPos + 1, high);
}
```

**错误后果**：当 `low == high` 时，继续递归调用，可能导致无限递归或栈溢出。

### 错误二：partition 循环条件写错

**错误代码**：

```cpp
int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = low;  // 错误：应该是 low - 1

    for (int j = low; j <= high; j++) {  // 错误：应该是 j < high
        if (arr[j] <= pivot) {
            swap(arr[i], arr[j]);
            i++;
        }
    }
    return i;
}
```

**错误后果**：分区失败，可能导致死循环或排序错误。

### 错误三：误以为快速排序是稳定的

**错误理解**："相等元素值一样，顺序无所谓"。

**示例**：

数组 `[2a, 2b, 1]`，排序后可能变成 `[1, 2b, 2a]`，2a 和 2b 的相对顺序改变。

**正确理解**：稳定性有实际意义，例如二次排序场景。

### 错误四：忽略 pivot 选择对性能的影响

**错误代码**：

```cpp
int partition(int arr[], int low, int high) {
    int pivot = arr[high];  // 选择最后一个元素
    // ...
}
```

**错误后果**：对于有序数组 `[0, 1, 2, 3, 4]`，每次 partition 只能减少一个元素，时间复杂度退化为 O(n²)。

### 错误五：递归深度过大导致栈溢出

**错误场景**：对有序数组 `[0, 1, 2, ..., 10000]` 使用快速排序。

**错误后果**：递归深度为 10001，超过系统栈深度限制，导致栈溢出。

### 错误六：处理重复元素时逻辑错误

**错误代码**：

```cpp
int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {  // 错误：应该是 <=
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i + 1], arr[high]);
    return i + 1;
}
```

**错误后果**：等于 pivot 的元素会被分到右边，可能导致分区不均衡。

## 正确做法

### 错误一正确做法

```cpp
void quickSort(int arr[], int low, int high) {
    if (low >= high) return;  // 正确：>= 而不是 >
    int pivotPos = partition(arr, low, high);
    quickSort(arr, low, pivotPos - 1);
    quickSort(arr, pivotPos + 1, high);
}
```

### 错误二正确做法

```cpp
int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = low - 1;  // 正确：low - 1

    for (int j = low; j < high; j++) {  // 正确：j < high
        if (arr[j] <= pivot) {
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i + 1], arr[high]);
    return i + 1;
}
```

### 错误三正确做法

**正确理解**：快速排序是不稳定的，使用稳定排序算法（如归并排序）时需要注意。

### 错误四正确做法

**使用随机选择**：

```cpp
int partition(int arr[], int low, int high) {
    int randomIdx = low + rand() % (high - low + 1);
    swap(arr[randomIdx], arr[high]);
    int pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i + 1], arr[high]);
    return i + 1;
}
```

### 错误五正确做法

**使用迭代版本**：

```cpp
void quickSortIterative(int arr[], int low, int high) {
    vector<pair<int, int>> st;
    st.emplace_back(low, high);

    while (!st.empty()) {
        auto [l, h] = st.back();
        st.pop_back();

        if (l >= h) continue;

        int pivotPos = partition(arr, l, h);
        st.emplace_back(l, pivotPos - 1);
        st.emplace_back(pivotPos + 1, h);
    }
}
```

### 错误六正确做法

```cpp
int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {  // 正确：<= 而不是 <
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i + 1], arr[high]);
    return i + 1;
}
```

### 错误与正确对比

| 错误类型 | 错误代码 | 正确代码 |
|----------|----------|----------|
| 递归边界 | `if (low > high)` | `if (low >= high)` |
| 循环条件 | `j <= high` | `j < high` |
| i 初始值 | `i = low` | `i = low - 1` |
| 重复元素 | `arr[j] < pivot` | `arr[j] <= pivot` |
| pivot 选择 | `pivot = arr[high]` | `随机选择` |
| 递归深度 | 递归调用 | 迭代版本 |

## 自查题

### 题目一

**题目描述**：指出以下快速排序代码的错误并修正。

```cpp
void quickSort(int arr[], int low, int high) {
    int pivotPos = partition(arr, low, high);
    quickSort(arr, low, pivotPos - 1);
    quickSort(arr, pivotPos + 1, high);
}

int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = low;

    for (int j = low; j <= high; j++) {
        if (arr[j] < pivot) {
            swap(arr[i], arr[j]);
            i++;
        }
    }
    swap(arr[i], arr[high]);
    return i;
}
```

**答案要点**：

1. **缺少递归边界条件**：`quickSort` 函数没有检查 `low >= high`，会导致无限递归。

2. **i 初始值错误**：`i` 应该初始化为 `low - 1`，而不是 `low`。

3. **循环条件错误**：`j` 应该从 `low` 到 `high - 1`，而不是 `high`。

4. **重复元素处理错误**：应该使用 `arr[j] <= pivot`，而不是 `<`。

**修正代码**：

```cpp
void quickSort(int arr[], int low, int high) {
    if (low >= high) return;  // 添加边界条件
    int pivotPos = partition(arr, low, high);
    quickSort(arr, low, pivotPos - 1);
    quickSort(arr, pivotPos + 1, high);
}

int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = low - 1;  // 修正初始值

    for (int j = low; j < high; j++) {  // 修正循环条件
        if (arr[j] <= pivot) {  // 修正重复元素处理
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i + 1], arr[high]);
    return i + 1;
}
```

### 题目二

**题目描述**：判断以下排序算法的稳定性，并说明理由。

1. 快速排序
2. 归并排序
3. 插入排序
4. 选择排序

**答案要点**：

1. **快速排序**：不稳定。partition 过程中，相等元素可能被跨位置交换。

2. **归并排序**：稳定。合并过程中，当左右子数组的元素相等时，先取左子数组的元素。

3. **插入排序**：稳定。插入过程中，相等元素不会被交换位置。

4. **选择排序**：不稳定。选择最小元素时，可能与前面的相等元素交换位置。

### 题目三

**题目描述**：对数组 `[3a, 1, 3b, 2]` 执行快速排序（pivot 选择最后一个元素），判断 3a 和 3b 的相对顺序是否可能改变。

**答案要点**：

**Partition 过程**（pivot = 2）：

```
初始：[3a, 1, 3b, 2]
j=0：3a > 2，不交换
j=1：1 <= 2，i++，交换 arr[0] 和 arr[1] → [1, 3a, 3b, 2]
j=2：3b > 2，不交换
最后交换 arr[i+1] 和 pivot → [1, 2, 3b, 3a]
```

**排序结果**：`[1, 2, 3b, 3a]`

**结论**：3a 和 3b 的相对顺序发生改变（3a 在 3b 之前 → 3b 在 3a 之前），证明快速排序是不稳定的。