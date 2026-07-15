# 快速排序 C++ 代码示例

## 代码目标

本代码演示快速排序的核心实现，包含 partition 函数和 quickSort 递归函数，并通过一个包含相等元素的数组展示快速排序的不稳定性。

## 核心代码

```cpp
#include <iostream>
#include <vector>
#include <string>
using namespace std;

struct Element {
    int val;
    int origIdx;
    Element(int v, int i) : val(v), origIdx(i) {}
};

void swap(Element& a, Element& b) {
    Element temp = a;
    a = b;
    b = temp;
}

int partition(vector<Element>& arr, int low, int high) {
    Element pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        if (arr[j].val <= pivot.val) {
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i + 1], arr[high]);
    return i + 1;
}

void quickSort(vector<Element>& arr, int low, int high) {
    if (low >= high) return;
    int pivotPos = partition(arr, low, high);
    quickSort(arr, low, pivotPos - 1);
    quickSort(arr, pivotPos + 1, high);
}

void printArray(const vector<Element>& arr, const string& label) {
    cout << label << ": ";
    for (const Element& e : arr) {
        cout << e.val << "(" << e.origIdx << ") ";
    }
    cout << endl;
}

int main() {
    vector<Element> arr;
    arr.emplace_back(3, 0);
    arr.emplace_back(1, 1);
    arr.emplace_back(2, 2);
    arr.emplace_back(3, 3);
    arr.emplace_back(0, 4);

    printArray(arr, "排序前");

    if (arr.size() > 1) {
        quickSort(arr, 0, arr.size() - 1);
    }

    printArray(arr, "排序后");

    cout << endl << "稳定性分析：" << endl;
    cout << "原始顺序中，3(0) 在 3(3) 之前" << endl;
    bool isStable = true;
    for (int i = 0; i < arr.size() - 1; i++) {
        if (arr[i].val == arr[i + 1].val && arr[i].origIdx > arr[i + 1].origIdx) {
            isStable = false;
            break;
        }
    }
    cout << "排序后，相等元素的相对顺序" << (isStable ? "保持不变，稳定" : "发生改变，不稳定") << endl;

    return 0;
}
```

## 关键步骤解释

### 1. 结构体定义

```cpp
struct Element {
    int val;
    int origIdx;
    Element(int v, int i) : val(v), origIdx(i) {}
};
```

- `val`：元素的值
- `origIdx`：元素的原始索引，用于追踪相等元素的相对顺序

### 2. Partition 函数

```cpp
int partition(vector<Element>& arr, int low, int high) {
    Element pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        if (arr[j].val <= pivot.val) {
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i + 1], arr[high]);
    return i + 1;
}
```

- **pivot 选择**：选择最后一个元素作为基准
- **指针 i**：记录小于等于 pivot 的元素的右边界
- **指针 j**：遍历数组，寻找小于等于 pivot 的元素
- **交换逻辑**：当 arr[j] <= pivot 时，将其交换到 i 的右侧
- **pivot 归位**：最后将 pivot 交换到正确位置

### 3. QuickSort 递归函数

```cpp
void quickSort(vector<Element>& arr, int low, int high) {
    if (low >= high) return;
    int pivotPos = partition(arr, low, high);
    quickSort(arr, low, pivotPos - 1);
    quickSort(arr, pivotPos + 1, high);
}
```

- **边界条件**：`low >= high` 时返回，避免无限递归
- **递归调用**：先排序左半部分，再排序右半部分

### 4. 稳定性分析

快速排序不稳定的原因：在 partition 过程中，相等元素可能被跨位置交换，导致相对顺序改变。

## 输入输出示例

### 输入

```
排序前: 3(0) 1(1) 2(2) 3(3) 0(4)
```

### 输出

```
排序前: 3(0) 1(1) 2(2) 3(3) 0(4)
排序后: 0(4) 1(1) 2(2) 3(3) 3(0)

稳定性分析：
原始顺序中，3(0) 在 3(3) 之前
排序后，相等元素的相对顺序发生改变，不稳定
```

### 输出解释

- 排序前：3(0) 在 3(3) 之前（原始顺序）
- 排序后：3(3) 在 3(0) 之前（相对顺序改变）
- 这证明了快速排序是不稳定的

## 边界条件

### 空数组

```cpp
if (arr.size() > 1) {
    quickSort(arr, 0, arr.size() - 1);
}
```

当数组为空时，`arr.size() == 0`，直接跳过排序。

### 单元素数组

当数组只有一个元素时，`arr.size() == 1`，直接跳过排序。

### 所有元素相等

```cpp
// 输入：{2, 2, 2}
// 输出：{2, 2, 2}（顺序可能改变）
```

所有元素相等时，partition 每次将数组分为两部分，时间复杂度为 O(n²)。

### 数组已经有序或逆序

```cpp
// 输入：{0, 1, 2, 3, 4}（有序）
// 输入：{4, 3, 2, 1, 0}（逆序）
```

如果每次选择最后一个元素作为 pivot，有序数组会导致最坏时间复杂度 O(n²)。

## 时间复杂度和空间复杂度

### 平均时间复杂度

**O(n log n)**

每次 partition 将数组分成大致相等的两部分，需要 log n 层递归，每层需要 O(n) 的比较和交换。

### 最坏时间复杂度

**O(n²)**

当 pivot 每次都是最小或最大元素时，递归深度为 n，每层需要 O(n) 的比较和交换。

### 最好时间复杂度

**O(n log n)**

当 pivot 每次将数组均匀划分时，递归深度为 log n，每层需要 O(n) 的比较和交换。

### 空间复杂度

**O(log n)**（平均情况）

递归调用栈的平均深度为 log n。

**O(n)**（最坏情况）

递归调用栈的最坏深度为 n。

## 改写练习

### 练习一：以第一个元素为基准

**提示**：修改 partition 函数，选择第一个元素作为 pivot。

**参考代码**：

```cpp
int partitionFirst(vector<Element>& arr, int low, int high) {
    Element pivot = arr[low];
    int i = low;

    for (int j = low + 1; j <= high; j++) {
        if (arr[j].val <= pivot.val) {
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i], arr[low]);
    return i;
}
```

### 练习二：随机选择基准元素

**提示**：使用 rand() 函数随机选择 pivot。

**参考代码**：

```cpp
int partitionRandom(vector<Element>& arr, int low, int high) {
    int randomIdx = low + rand() % (high - low + 1);
    swap(arr[randomIdx], arr[high]);
    return partition(arr, low, high);
}
```

### 练习三：迭代版本

**提示**：使用显式栈替代递归调用栈。

**参考代码**：

```cpp
void quickSortIterative(vector<Element>& arr, int low, int high) {
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

### 练习四：三数取中选择基准

**提示**：选择首、尾、中间三个元素的中位数作为 pivot。

**参考代码**：

```cpp
int medianOfThree(vector<Element>& arr, int low, int high) {
    int mid = low + (high - low) / 2;
    if (arr[low].val > arr[mid].val) swap(arr[low], arr[mid]);
    if (arr[low].val > arr[high].val) swap(arr[low], arr[high]);
    if (arr[mid].val > arr[high].val) swap(arr[mid], arr[high]);
    swap(arr[mid], arr[high]);
    return arr[high].val;
}
```