# 文件系统目录结构遍历工具

## 项目场景

在日常开发和运维工作中，我们经常需要查看文件系统的目录结构。例如：
- 程序员需要快速了解项目的目录组织
- 运维人员需要检查服务器上的文件布局
- 用户需要可视化展示自己的文件夹结构

本项目将开发一个命令行工具，能够：
1. 读取指定目录的结构
2. 用树状结构展示目录内容
3. 支持多种遍历方式（前序遍历、按名称排序输出）
4. 提供文件查找功能

## 任务目标

1. **构建目录树**：根据指定路径，递归扫描所有子目录和文件，构建树状数据结构
2. **前序遍历输出**：按照"根-子-孙"的顺序输出目录结构，显示完整路径层级
3. **按名称排序输出**：对每个目录下的内容按名称排序后输出（模拟中序遍历的有序特性）
4. **文件查找**：根据文件名或关键字查找文件，并显示其完整路径
5. **深度限制**：支持限制遍历的最大深度

## 为什么使用该数据结构

### 为什么选择树结构

文件系统天然就是树形结构：
- 根目录是树的根节点
- 子目录是内部节点
- 文件是叶子节点
- 目录之间的层级关系对应树的父子关系

### 为什么不用数组或链表

- **数组**：无法有效表达层级关系，查找特定路径效率低
- **链表**：只能表达线性关系，无法表示分支结构
- **树**：能够自然、高效地表达一对多的层级关系，遍历操作非常直观

### 与二叉树的联系

虽然文件系统是 N 叉树（一个目录可以有多个子目录），但遍历思想与二叉树一致：
- 前序遍历：先访问当前节点，再递归遍历所有子节点
- 中序遍历：可以理解为按特定顺序（如名称排序）遍历子节点

## 实现步骤

### 步骤一：定义树节点结构

定义一个 DirectoryNode 结构体，包含目录/文件名称、类型（目录或文件）、子节点列表等字段。

### 步骤二：构建目录树

实现一个递归函数，扫描指定目录：
1. 获取目录下所有条目
2. 对每个条目判断是文件还是目录
3. 创建对应的节点
4. 如果是目录，递归调用构建其子树

### 步骤三：实现前序遍历输出

实现前序遍历函数：
1. 访问当前节点（输出名称和层级缩进）
2. 递归遍历所有子节点

### 步骤四：实现按名称排序输出

在遍历前，对每个节点的子节点列表按名称排序，然后再进行遍历。

### 步骤五：实现文件查找功能

实现递归查找函数：
1. 检查当前节点是否匹配查找条件
2. 如果匹配，记录路径
3. 递归查找所有子节点

### 步骤六：编写主程序

提供命令行接口，支持：
- 指定扫描目录
- 选择遍历方式（前序/排序）
- 设置最大深度
- 执行文件查找

## 核心数据结构设计

```cpp
#include <string>
#include <vector>
#include <algorithm>
using namespace std;

enum NodeType { DIRECTORY, FILE };

struct DirectoryNode {
    string name;
    string path;
    NodeType type;
    vector<DirectoryNode*> children;
    DirectoryNode* parent;

    DirectoryNode(string n, string p, NodeType t)
        : name(n), path(p), type(t), parent(nullptr) {}

    ~DirectoryNode() {
        for (auto child : children) {
            delete child;
        }
    }

    void sortChildren() {
        sort(children.begin(), children.end(), [](DirectoryNode* a, DirectoryNode* b) {
            if (a->type != b->type) {
                return a->type == DIRECTORY;
            }
            return a->name < b->name;
        });
    }
};
```

### 字段说明

- `name`：节点名称（文件名或目录名）
- `path`：节点的完整路径
- `type`：节点类型（DIRECTORY 表示目录，FILE 表示文件）
- `children`：子节点列表（目录的子目录和文件）
- `parent`：父节点指针（便于回溯路径）
- `sortChildren()`：按类型和名称排序子节点（目录优先，然后按名称排序）

## 核心代码框架或伪代码

### 构建目录树

```cpp
DirectoryNode* buildTree(const string& dirPath, DirectoryNode* parent = nullptr) {
    DirectoryNode* node = new DirectoryNode(
        getBasename(dirPath), dirPath, DIRECTORY);
    node->parent = parent;

    vector<string> entries = listDirectory(dirPath);
    for (const string& entry : entries) {
        string fullPath = dirPath + "/" + entry;
        if (isDirectory(fullPath)) {
            node->children.push_back(buildTree(fullPath, node));
        } else {
            node->children.push_back(
                new DirectoryNode(entry, fullPath, FILE));
        }
    }
    return node;
}
```

### 前序遍历输出

```cpp
void preorderPrint(DirectoryNode* node, int depth = 0) {
    if (!node) return;

    for (int i = 0; i < depth; i++) {
        cout << "  ";
    }

    if (node->type == DIRECTORY) {
        cout << "+ " << node->name << "/" << endl;
    } else {
        cout << "- " << node->name << endl;
    }

    for (auto child : node->children) {
        preorderPrint(child, depth + 1);
    }
}
```

### 按名称排序遍历输出

```cpp
void sortedPrint(DirectoryNode* node, int depth = 0) {
    if (!node) return;

    node->sortChildren();

    for (int i = 0; i < depth; i++) {
        cout << "  ";
    }

    if (node->type == DIRECTORY) {
        cout << "+ " << node->name << "/" << endl;
    } else {
        cout << "- " << node->name << endl;
    }

    for (auto child : node->children) {
        sortedPrint(child, depth + 1);
    }
}
```

### 文件查找

```cpp
void findFile(DirectoryNode* node, const string& keyword, vector<string>& results) {
    if (!node) return;

    if (node->name.find(keyword) != string::npos) {
        results.push_back(node->path);
    }

    for (auto child : node->children) {
        findFile(child, keyword, results);
    }
}
```

## 测试用例

### 测试场景一：小型目录树

**输入目录结构**：

```
my_project/
├── src/
│   ├── main.cpp
│   └── utils/
│       └── helper.cpp
├── include/
│   └── common.h
└── README.md
```

**前序遍历输出**：

```
+ my_project/
  + src/
    - main.cpp
    + utils/
      - helper.cpp
  + include/
    - common.h
  - README.md
```

**按名称排序输出**：

```
+ my_project/
  + include/
    - common.h
  - README.md
  + src/
    - main.cpp
    + utils/
      - helper.cpp
```

### 测试场景二：空目录树

**输入**：一个空目录 `empty_dir/`

**期望输出**：

```
+ empty_dir/
```

### 测试场景三：文件查找

**输入**：查找关键字 "cpp"

**期望输出**：

```
my_project/src/main.cpp
my_project/src/utils/helper.cpp
```

## 扩展方向

### 扩展一：文件大小统计

在节点结构中增加 `size` 字段，记录文件大小或目录总大小。遍历过程中计算每个目录的总大小，并在输出时显示。

### 扩展二：深度限制遍历

在遍历函数中增加 `maxDepth` 参数，当当前深度超过限制时停止递归。适用于大型目录结构的概览。

### 扩展三：导出为 JSON 格式

实现一个函数，将目录树导出为 JSON 格式，便于与其他工具集成或进行数据交换。

### 扩展四：正则表达式查找

将简单的关键字查找扩展为支持正则表达式匹配，提高查找的灵活性。

### 扩展五：图形化输出

使用 ASCII 字符绘制更美观的树形图，例如：

```
my_project/
├── src/
│   ├── main.cpp
│   └── utils/
│       └── helper.cpp
├── include/
│   └── common.h
└── README.md
```