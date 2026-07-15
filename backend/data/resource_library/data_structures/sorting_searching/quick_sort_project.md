# 学生成绩排名与多字段排序系统

## 项目场景

在学校或培训机构中，学生成绩排名是一项常见需求。本项目设计一个"学生成绩排名与多字段排序系统"，支持以下功能：

- **输入学生数据**：包含姓名、学号、总成绩
- **排序需求**：先按总成绩从高到低排序，总成绩相同的学生按学号从小到大排序
- **稳定性展示**：对比稳定版和不稳定版快速排序的输出差异

**实际应用场景**：
- 班级成绩排名
- 奖学金评选（同分按学号或其他条件）
- 考试成绩统计分析

## 任务目标

1. **定义数据结构**：定义 Student 结构体，包含姓名、学号、成绩、原始位置索引
2. **实现稳定版快速排序**：比较时先比较成绩，成绩相同则比较学号（或原始索引）
3. **实现不稳定版快速排序**：只按成绩比较，不考虑学号
4. **对比结果**：分别调用两个版本，输出排序结果，展示稳定性差异
5. **输出统计**：显示排序前后的学生列表

## 为什么使用该数据结构

### 学生记录的存储

学生记录天然适合用结构体数组存储：
- 每个学生包含多个字段（姓名、学号、成绩）
- 需要支持多字段比较
- 需要保持原始顺序的追踪

### 快速排序的选择

快速排序是实际场景中常用的排序算法：
- 平均时间复杂度 O(n log n)，效率高
- 原地排序，空间复杂度低
- 但默认不稳定，需要通过修改比较规则来实现稳定排序

### 稳定性的意义

在成绩排名中，稳定性很重要：
- 同分学生需要按学号排序（学号小的在前）
- 不稳定排序可能打乱这个顺序
- 通过增加原始索引或学号作为比较键，可以实现稳定排序

## 实现步骤

### 步骤一：定义 Student 结构体

```cpp
struct Student {
    string name;
    int id;
    int score;
    int origPos;
};
```

### 步骤二：实现 partition 函数

- **稳定版**：比较时先比较 score，score 相同则比较 id
- **不稳定版**：只比较 score

### 步骤三：实现 quickSort 递归函数

调用 partition，递归排序左右子数组

### 步骤四：编写主程序

1. 构建测试数据（包含同分学生）
2. 分别调用稳定版和不稳定版快速排序
3. 输出排序结果并对比

### 步骤五：分析结果

总结稳定性的影响，说明何时需要稳定性

## 核心数据结构设计

```cpp
#include <iostream>
#include <vector>
#include <string>
using namespace std;

struct Student {
    string name;
    int id;
    int score;
    int origPos;

    Student(string n, int i, int s, int o)
        : name(n), id(i), score(s), origPos(o) {}
};

void swap(Student& a, Student& b) {
    Student temp = a;
    a = b;
    b = temp;
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 学生姓名 |
| id | int | 学号（唯一标识） |
| score | int | 总成绩 |
| origPos | int | 原始位置索引（用于追踪相对顺序） |

### Partition 函数设计

```cpp
int partition(vector<Student>& arr, int low, int high, bool stable) {
    Student pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        bool shouldSwap;
        if (stable) {
            if (arr[j].score != pivot.score) {
                shouldSwap = arr[j].score > pivot.score;
            } else {
                shouldSwap = arr[j].id < pivot.id;
            }
        } else {
            shouldSwap = arr[j].score > pivot.score;
        }

        if (shouldSwap) {
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i + 1], arr[high]);
    return i + 1;
}
```

## 核心代码框架或伪代码

### Student 结构体

```
struct Student {
    string name
    int id
    int score
    int origPos
}
```

### Partition 函数

```
function partition(arr, low, high, stable):
    pivot = arr[high]
    i = low - 1

    for j = low to high - 1:
        if stable:
            if arr[j].score != pivot.score:
                shouldSwap = arr[j].score > pivot.score
            else:
                shouldSwap = arr[j].id < pivot.id
        else:
            shouldSwap = arr[j].score > pivot.score

        if shouldSwap:
            i++
            swap(arr[i], arr[j])

    swap(arr[i+1], arr[high])
    return i+1
```

### QuickSort 递归函数

```
function quickSort(arr, low, high, stable):
    if low >= high:
        return
    pivotPos = partition(arr, low, high, stable)
    quickSort(arr, low, pivotPos-1, stable)
    quickSort(arr, pivotPos+1, high, stable)
```

### Main 函数

```
function main():
    students = [
        ("张三", 1, 85, 0),
        ("李四", 2, 90, 1),
        ("王五", 3, 85, 2),
        ("赵六", 4, 80, 3),
        ("钱七", 5, 85, 4)
    ]

    stableStudents = copy(students)
    unstableStudents = copy(students)

    quickSort(stableStudents, 0, 4, true)
    quickSort(unstableStudents, 0, 4, false)

    print("排序前:")
    print(students)

    print("\n稳定版排序后:")
    print(stableStudents)

    print("\n不稳定版排序后:")
    print(unstableStudents)
```

## 测试用例

### 测试用例一：包含两个同分学生

**输入数据**：

| 姓名 | 学号 | 成绩 | 原始位置 |
|------|------|------|----------|
| 张三 | 1 | 85 | 0 |
| 李四 | 2 | 90 | 1 |
| 王五 | 3 | 85 | 2 |
| 赵六 | 4 | 80 | 3 |
| 钱七 | 5 | 85 | 4 |

**稳定版期望输出**（按成绩降序，同分按学号升序）：

| 姓名 | 学号 | 成绩 |
|------|------|------|
| 李四 | 2 | 90 |
| 张三 | 1 | 85 |
| 王五 | 3 | 85 |
| 钱七 | 5 | 85 |
| 赵六 | 4 | 80 |

**不稳定版可能输出**（同分学生顺序可能改变）：

| 姓名 | 学号 | 成绩 |
|------|------|------|
| 李四 | 2 | 90 |
| 王五 | 3 | 85 |
| 钱七 | 5 | 85 |
| 张三 | 1 | 85 |
| 赵六 | 4 | 80 |

### 测试用例二：多个同分且学号乱序

**输入数据**：

| 姓名 | 学号 | 成绩 |
|------|------|------|
| A | 5 | 90 |
| B | 3 | 90 |
| C | 1 | 90 |
| D | 4 | 90 |
| E | 2 | 90 |

**稳定版期望输出**（按学号升序）：

| 姓名 | 学号 | 成绩 |
|------|------|------|
| C | 1 | 90 |
| E | 2 | 90 |
| B | 3 | 90 |
| D | 4 | 90 |
| A | 5 | 90 |

**不稳定版可能输出**（顺序不确定）：

| 姓名 | 学号 | 成绩 |
|------|------|------|
| A | 5 | 90 |
| B | 3 | 90 |
| C | 1 | 90 |
| D | 4 | 90 |
| E | 2 | 90 |

### 测试用例三：边界情况

**空列表**：无输出，直接返回

**单学生**：输出该学生信息

**所有学生同分**：稳定版按学号升序排列，不稳定版顺序不确定

## 扩展方向

### 扩展一：从 CSV 文件读取数据

```cpp
void readFromCSV(const string& filename, vector<Student>& students) {
    ifstream file(filename);
    string line;
    int pos = 0;

    while (getline(file, line)) {
        string name;
        int id, score;
        // 解析 CSV 格式
        students.emplace_back(name, id, score, pos++);
    }
}
```

### 扩展二：支持选择排序字段

```cpp
enum SortField { SCORE, ID, NAME };

bool compare(const Student& a, const Student& b, SortField field) {
    switch (field) {
        case SCORE: return a.score > b.score;
        case ID: return a.id < b.id;
        case NAME: return a.name < b.name;
    }
}
```

### 扩展三：与归并排序进行性能对比

实现归并排序，比较两者在不同数据规模下的性能差异。

### 扩展四：排序过程可视化

输出每一步的分区状态，展示排序过程：

```
分区前: [张三(85), 李四(90), 王五(85), 赵六(80), 钱七(85)]
分区后: [李四(90), 张三(85), 王五(85), 钱七(85), 赵六(80)]
         ↑ pivotPos=0
```

### 扩展五：多级排序

支持多字段排序，例如：
- 先按成绩降序
- 再按学号升序
- 最后按姓名升序

```cpp
bool compareMulti(const Student& a, const Student& b) {
    if (a.score != b.score) return a.score > b.score;
    if (a.id != b.id) return a.id < b.id;
    return a.name < b.name;
}
```