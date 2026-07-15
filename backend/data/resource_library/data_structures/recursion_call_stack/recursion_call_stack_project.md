# 文件夹大小统计工具

## 项目场景

设计一个"文件夹大小统计工具"——给定一个文件夹（目录），它可以包含文件和子文件夹。用户需要统计该文件夹下所有文件的总大小（字节数），并列出每个子文件夹的大小。

**示例目录结构**：

```
root/
├── a.txt (100 KB)
├── b.txt (200 KB)
├── sub1/
│   ├── c.txt (150 KB)
│   └── sub1_1/
│       └── d.txt (50 KB)
└── sub2/
    └── e.txt (300 KB)
```

**期望输出**：

```
root: 800 KB
  sub1: 200 KB
    sub1_1: 50 KB
  sub2: 300 KB
```

这个问题天然适合使用递归来解决：先统计当前文件夹下所有文件的总大小，然后递归统计每个子文件夹的大小，最后累加并返回。

## 任务目标

1. **定义目录树结构**：定义一个树形结构表示文件夹，每个节点包含文件列表和子文件夹列表。
2. **实现递归函数**：实现 `getFolderSize(node)`，返回该文件夹及其子文件夹的总大小。
3. **输出目录树**：以缩进方式展示目录树和对应大小。
4. **处理深度递归**：对于非常大的目录树，能够处理深度递归（考虑递归栈溢出问题）。
5. **提供测试用例**：在内存中构建目录树，验证递归函数的正确性。

## 为什么使用该数据结构

### 问题特征分析

| 特征 | 说明 |
|------|------|
| 树形结构 | 文件夹天然是树形结构（目录树），递归是处理树形结构最自然的方式 |
| 最优子结构 | 每个文件夹的总大小依赖其子文件夹的大小 |
| 递归深度 | 递归调用栈的深度取决于目录树的深度 |

### 递归的优势

- **代码简洁**：递归代码直观表达了"先统计当前文件夹，再递归统计子文件夹"的逻辑。
- **结构清晰**：与目录树结构天然匹配，易于理解。
- **教学价值**：可以直观展示递归调用栈的"压栈"和"回溯"过程。

## 实现步骤

### 步骤一：定义数据结构

定义 `FolderNode` 结构体，包含文件夹名、文件大小列表和子文件夹列表。

### 步骤二：构建示例目录树

在内存中构建一个深度为 3-4 层的示例目录树，包含多个文件和子文件夹。

### 步骤三：实现辅助函数

实现 `printIndent(depth)` 函数，用于打印缩进，展示目录层级。

### 步骤四：实现递归函数

实现 `getFolderSize(node, depth)`：
1. 计算当前文件夹中所有文件的总大小
2. 遍历子文件夹，递归调用 `getFolderSize` 并累加结果
3. 输出当前文件夹的总大小并返回

### 步骤五：主函数调用

在主函数中调用 `getFolderSize(root, 0)`，输出整个目录树的大小统计。

### 步骤六：扩展（迭代栈替代）

增加"最大递归深度"检测，当深度超过阈值时，改用迭代栈（显式栈）的方式。

## 核心数据结构设计

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <stack>
using namespace std;

struct FolderNode {
    string name;
    vector<long long> files;
    vector<FolderNode*> children;
    FolderNode(string n) : name(n) {}
};

void printIndent(int depth) {
    for (int i = 0; i < depth; i++) {
        cout << "  ";
    }
}

long long getFolderSize(FolderNode* node, int depth = 0) {
    long long total = 0;
    for (long long fileSize : node->files) {
        total += fileSize;
    }
    for (FolderNode* child : node->children) {
        total += getFolderSize(child, depth + 1);
    }
    printIndent(depth);
    cout << node->name << ": " << total << " bytes" << endl;
    return total;
}

long long getFolderSizeIterative(FolderNode* root) {
    struct StackFrame {
        FolderNode* node;
        int depth;
        bool visited;
    };
    stack<StackFrame> st;
    st.push({root, 0, false});
    vector<pair<string, long long>> results;

    while (!st.empty()) {
        StackFrame frame = st.top();
        st.pop();

        if (!frame.visited) {
            st.push({frame.node, frame.depth, true});
            for (auto it = frame.node->children.rbegin(); it != frame.node->children.rend(); ++it) {
                st.push({*it, frame.depth + 1, false});
            }
        } else {
            long long total = 0;
            for (long long fileSize : frame.node->files) {
                total += fileSize;
            }
            for (FolderNode* child : frame.node->children) {
                for (auto& r : results) {
                    if (r.first == child->name) {
                        total += r.second;
                        break;
                    }
                }
            }
            results.push_back({frame.node->name, total});
            printIndent(frame.depth);
            cout << frame.node->name << ": " << total << " bytes" << endl;
        }
    }
    return root ? results.back().second : 0;
}
```

### 数据结构说明

| 数据结构 | 类型 | 说明 |
|----------|------|------|
| FolderNode | struct | 文件夹节点，包含名称、文件列表、子文件夹列表 |
| files | vector<long long> | 当前文件夹中的文件大小列表 |
| children | vector<FolderNode*> | 当前文件夹的子文件夹列表 |
| StackFrame | struct | 迭代版本中模拟栈帧的结构体 |

## 核心代码框架或伪代码

### FolderNode 结构体定义

```
struct FolderNode:
    name: string
    files: list of long long
    children: list of FolderNode*
```

### getFolderSize 递归函数

```
function getFolderSize(node, depth):
    total = sum of all files in node.files
    
    for each child in node.children:
        total += getFolderSize(child, depth + 1)
    
    printIndent(depth)
    print(node.name + ": " + total + " bytes")
    
    return total
```

### 构建测试目录树

```
function buildTestTree():
    root = FolderNode("root")
    root.files = [100, 200]
    
    sub1 = FolderNode("sub1")
    sub1.files = [150]
    
    sub1_1 = FolderNode("sub1_1")
    sub1_1.files = [50]
    sub1.children = [sub1_1]
    
    sub2 = FolderNode("sub2")
    sub2.files = [300]
    
    root.children = [sub1, sub2]
    
    return root
```

### Main 函数

```
function main():
    print("=== 递归版本 ===")
    root = buildTestTree()
    total = getFolderSize(root, 0)
    print("总大小:", total, "bytes")
    
    print("\n=== 迭代版本 ===")
    root2 = buildTestTree()
    total2 = getFolderSizeIterative(root2)
    print("总大小:", total2, "bytes")
```

## 测试用例

### 测试用例一：简单目录树

**输入**：

```
root/ (文件: a.txt=10, b.txt=20)
├── sub1/ (文件: c.txt=30)
└── sub2/ (无文件)
```

**期望输出**：

```
sub1: 30 bytes
sub2: 0 bytes
root: 60 bytes
总大小: 60 bytes
```

### 测试用例二：深度目录树

**输入**：

```
root/ (文件: 1)
└── sub1/ (文件: 2)
    └── sub2/ (文件: 3)
        └── sub3/ (文件: 4)
```

**期望输出**：

```
sub3: 4 bytes
sub2: 7 bytes
sub1: 9 bytes
root: 10 bytes
总大小: 10 bytes
```

### 测试用例三：空文件夹

**输入**：

```
empty/ (无文件，无子文件夹)
```

**期望输出**：

```
empty: 0 bytes
总大小: 0 bytes
```

### 测试用例四：大目录树（递归深度问题）

**输入**：深度为 100 层的目录树，每层有一个 1 字节的文件。

**期望输出**：

- 递归版本可能出现栈溢出
- 迭代版本正常输出总大小为 100 字节

## 扩展方向

### 扩展一：最大深度限制

增加"最大深度"参数，限制递归深度，超出则报错或切换到迭代模式：

```cpp
const int MAX_DEPTH = 1000;
long long getFolderSizeLimited(FolderNode* node, int depth = 0) {
    if (depth > MAX_DEPTH) {
        cout << "Error: Recursion depth exceeded!" << endl;
        return 0;
    }
    long long total = 0;
    for (long long fileSize : node->files) {
        total += fileSize;
    }
    for (FolderNode* child : node->children) {
        total += getFolderSizeLimited(child, depth + 1);
    }
    printIndent(depth);
    cout << node->name << ": " << total << " bytes" << endl;
    return total;
}
```

### 扩展二：文件类型过滤

只统计特定后缀的文件：

```cpp
long long getFolderSizeFiltered(FolderNode* node, int depth, const string& extension) {
    long long total = 0;
    for (long long fileSize : node->files) {
        total += fileSize;
    }
    for (FolderNode* child : node->children) {
        total += getFolderSizeFiltered(child, depth + 1, extension);
    }
    printIndent(depth);
    cout << node->name << ": " << total << " bytes" << endl;
    return total;
}
```

### 扩展三：图形化输出

增加树形图输出：

```
root (600 bytes)
├── sub1 (200 bytes)
│   └── sub1_1 (50 bytes)
└── sub2 (300 bytes)
```

### 扩展四：JSON 导出

将目录树大小信息导出为 JSON 格式：

```json
{
    "name": "root",
    "size": 600,
    "children": [
        {
            "name": "sub1",
            "size": 200,
            "children": [...]
        }
    ]
}
```

### 扩展五：真实文件系统读取

使用 `std::filesystem` 库（C++17）从真实文件系统读取目录：

```cpp
#include <filesystem>
namespace fs = std::filesystem;

long long getRealFolderSize(const fs::path& path) {
    long long total = 0;
    for (const auto& entry : fs::directory_iterator(path)) {
        if (entry.is_regular_file()) {
            total += fs::file_size(entry);
        } else if (entry.is_directory()) {
            total += getRealFolderSize(entry.path());
        }
    }
    return total;
}
```