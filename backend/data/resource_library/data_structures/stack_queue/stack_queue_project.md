# 浏览器前进后退模拟器

## 项目场景

设计一个"浏览器前进后退模拟器"——模拟浏览器的页面导航功能。用户访问新页面时，当前页面被记录；点击"后退"按钮回到上一页；点击"前进"按钮回到后退之前的页面。

**示例操作序列**：

```
访问 A → 访问 B → 访问 C → 后退 → 后退 → 前进 → 访问 D

页面变化：
A → B → C → B → A → B → D

栈状态变化：
backStack: [] → [A] → [A, B] → [A] → [] → [A] → [A, B]
forwardStack: [] → [] → [] → [C] → [C, B] → [C] → []
```

这个功能是栈的典型应用，使用两个栈（backStack 和 forwardStack）来实现。

## 任务目标

1. **访问新页面**：`visit(url)` —— 将当前页面压入后退栈，设置新页面为当前页面，清空前进栈
2. **后退操作**：`back()` —— 将当前页面压入前进栈，从后退栈弹出上一页作为当前页面
3. **前进操作**：`forward()` —— 将当前页面压入后退栈，从前进栈弹出下一页作为当前页面
4. **状态显示**：`printStatus()` —— 显示当前页面、后退栈和前进栈的内容
5. **命令行交互**：提供菜单选择界面，支持 visit、back、forward、print、exit 命令
6. **边界处理**：后退栈为空时无法后退，前进栈为空时无法前进

## 为什么使用该数据结构

### 问题特征分析

| 特征 | 说明 |
|------|------|
| LIFO 特性 | 后退和前进都是"后到先服务" |
| 双栈协作 | 需要两个栈分别管理后退和前进历史 |
| 状态转换 | 访问新页面会改变两个栈的状态 |
| 边界条件 | 栈为空时需要特殊处理 |

### 栈的优势

- **完美匹配**：浏览器的后退/前进操作完美匹配栈的 LIFO 特性
- **结构清晰**：两个栈分别存储"可以后退的历史"和"可以前进的历史"
- **符合直觉**：访问新页面时清空 forwardStack，符合浏览器的实际行为
- **贴近生活**：比单纯的括号匹配更贴近实际生活，学生更容易理解

### 双栈协作原理

```
                    访问新页面
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   backStack       currentPage       forwardStack
   [A, B]            C                  []
        │                │                │
        │              后退               │
        │                │                │
        │   ┌────────────┴────────────┐   │
        │   ▼                        ▼   │
        │   currentPage → forwardStack  │
        │     B            [C]          │
        │                               │
        ▼   currentPage ← backStack     │
       [A]     B                        │
```

## 实现步骤

### 步骤一：定义 Browser 类

```cpp
class Browser {
private:
    string currentPage;
    stack<string> backStack;
    stack<string> forwardStack;
};
```

### 步骤二：实现 visit() 方法

```cpp
void visit(const string& url) {
    if (!currentPage.empty()) {
        backStack.push(currentPage);
    }
    currentPage = url;
    // 清空前进栈
    while (!forwardStack.empty()) {
        forwardStack.pop();
    }
}
```

### 步骤三：实现 back() 方法

```cpp
bool back() {
    if (backStack.empty()) {
        cout << "无法后退，后退栈为空！" << endl;
        return false;
    }
    forwardStack.push(currentPage);
    currentPage = backStack.top();
    backStack.pop();
    return true;
}
```

### 步骤四：实现 forward() 方法

```cpp
bool forward() {
    if (forwardStack.empty()) {
        cout << "无法前进，前进栈为空！" << endl;
        return false;
    }
    backStack.push(currentPage);
    currentPage = forwardStack.top();
    forwardStack.pop();
    return true;
}
```

### 步骤五：实现 printStatus() 方法

```cpp
void printStatus() const {
    cout << "\n=== 浏览器状态 ===" << endl;
    cout << "当前页面: " << (currentPage.empty() ? "无" : currentPage) << endl;
    cout << "后退栈: " << stackToString(backStack) << endl;
    cout << "前进栈: " << stackToString(forwardStack) << endl;
}
```

### 步骤六：编写 main 函数

```cpp
int main() {
    Browser browser;
    string command, url;
    
    while (true) {
        cout << "\n请输入命令 (visit/back/forward/print/exit): ";
        cin >> command;
        
        if (command == "visit") {
            cin >> url;
            browser.visit(url);
        } else if (command == "back") {
            browser.back();
        } else if (command == "forward") {
            browser.forward();
        } else if (command == "print") {
            browser.printStatus();
        } else if (command == "exit") {
            break;
        } else {
            cout << "未知命令，请重新输入！" << endl;
        }
    }
    
    return 0;
}
```

## 核心数据结构设计

```cpp
#include <iostream>
#include <stack>
#include <string>
#include <algorithm>
using namespace std;

class Browser {
private:
    string currentPage;
    stack<string> backStack;
    stack<string> forwardStack;
    
    string stackToString(const stack<string>& s) const {
        stack<string> temp = s;
        string result = "[";
        while (!temp.empty()) {
            if (result != "[") result += ", ";
            result += temp.top();
            temp.pop();
        }
        result += "]";
        return result;
    }
    
public:
    Browser() : currentPage("") {}
    
    void visit(const string& url) {
        if (!currentPage.empty()) {
            backStack.push(currentPage);
        }
        currentPage = url;
        while (!forwardStack.empty()) {
            forwardStack.pop();
        }
        cout << "访问页面: " << url << endl;
    }
    
    bool back() {
        if (backStack.empty()) {
            cout << "❌ 无法后退，后退栈为空！" << endl;
            return false;
        }
        forwardStack.push(currentPage);
        currentPage = backStack.top();
        backStack.pop();
        cout << "⬅️  后退到: " << currentPage << endl;
        return true;
    }
    
    bool forward() {
        if (forwardStack.empty()) {
            cout << "❌ 无法前进，前进栈为空！" << endl;
            return false;
        }
        backStack.push(currentPage);
        currentPage = forwardStack.top();
        forwardStack.pop();
        cout << "➡️  前进到: " << currentPage << endl;
        return true;
    }
    
    void printStatus() const {
        cout << "\n=== 浏览器状态 ===" << endl;
        cout << "当前页面: " << (currentPage.empty() ? "无" : currentPage) << endl;
        cout << "后退栈: " << stackToString(backStack) << endl;
        cout << "前进栈: " << stackToString(forwardStack) << endl;
    }
    
    string getCurrentPage() const {
        return currentPage;
    }
    
    bool canBack() const {
        return !backStack.empty();
    }
    
    bool canForward() const {
        return !forwardStack.empty();
    }
};
```

### 数据结构说明

| 数据结构 | 类型 | 说明 |
|----------|------|------|
| currentPage | string | 当前页面 URL |
| backStack | stack\<string\> | 后退栈，存储可以后退的页面 |
| forwardStack | stack\<string\> | 前进栈，存储可以前进的页面 |

### 核心方法说明

| 方法 | 返回值 | 说明 |
|------|--------|------|
| visit(url) | void | 访问新页面，更新两个栈的状态 |
| back() | bool | 后退操作，成功返回 true，失败返回 false |
| forward() | bool | 前进操作，成功返回 true，失败返回 false |
| printStatus() | void | 输出当前状态 |
| getCurrentPage() | string | 获取当前页面 |
| canBack() | bool | 判断是否可以后退 |
| canForward() | bool | 判断是否可以前进 |

## 核心代码框架或伪代码

### Browser 类定义

```
class Browser:
    currentPage: string
    backStack: stack<string>
    forwardStack: stack<string>
    
    methods:
        visit(url)
        back() -> bool
        forward() -> bool
        printStatus()
```

### visit 方法伪代码

```
function visit(url):
    if currentPage is not empty:
        push currentPage to backStack
    
    set currentPage = url
    
    while forwardStack is not empty:
        pop from forwardStack
    
    print "访问页面: " + url
```

### back 方法伪代码

```
function back():
    if backStack is empty:
        print "无法后退，后退栈为空！"
        return false
    
    push currentPage to forwardStack
    
    set currentPage = top of backStack
    pop from backStack
    
    print "后退到: " + currentPage
    return true
```

### forward 方法伪代码

```
function forward():
    if forwardStack is empty:
        print "无法前进，前进栈为空！"
        return false
    
    push currentPage to backStack
    
    set currentPage = top of forwardStack
    pop from forwardStack
    
    print "前进到: " + currentPage
    return true
```

### printStatus 方法伪代码

```
function printStatus():
    print "=== 浏览器状态 ==="
    print "当前页面: " + currentPage
    print "后退栈: " + backStack contents (from bottom to top)
    print "前进栈: " + forwardStack contents (from bottom to top)
```

### main 函数交互流程

```
function main():
    browser = Browser()
    
    while true:
        print "\n请输入命令 (visit/back/forward/print/exit): "
        read command
        
        if command == "visit":
            read url
            browser.visit(url)
        elif command == "back":
            browser.back()
        elif command == "forward":
            browser.forward()
        elif command == "print":
            browser.printStatus()
        elif command == "exit":
            break
        else:
            print "未知命令，请重新输入！"
```

## 测试用例

### 测试用例一：初始访问

**操作**：`visit("A")`

**期望输出**：

```
访问页面: A

=== 浏览器状态 ===
当前页面: A
后退栈: []
前进栈: []
```

### 测试用例二：连续访问

**操作**：`visit("B")`

**期望输出**：

```
访问页面: B

=== 浏览器状态 ===
当前页面: B
后退栈: [A]
前进栈: []
```

### 测试用例三：继续访问

**操作**：`visit("C")`

**期望输出**：

```
访问页面: C

=== 浏览器状态 ===
当前页面: C
后退栈: [A, B]
前进栈: []
```

### 测试用例四：第一次后退

**操作**：`back()`

**期望输出**：

```
⬅️  后退到: B

=== 浏览器状态 ===
当前页面: B
后退栈: [A]
前进栈: [C]
```

### 测试用例五：第二次后退

**操作**：`back()`

**期望输出**：

```
⬅️  后退到: A

=== 浏览器状态 ===
当前页面: A
后退栈: []
前进栈: [C, B]
```

### 测试用例六：前进

**操作**：`forward()`

**期望输出**：

```
➡️  前进到: B

=== 浏览器状态 ===
当前页面: B
后退栈: [A]
前进栈: [C]
```

### 测试用例七：访问新页面（清空前进栈）

**操作**：`visit("D")`

**期望输出**：

```
访问页面: D

=== 浏览器状态 ===
当前页面: D
后退栈: [A, B]
前进栈: []
```

### 测试用例八：连续后退到边界

**操作序列**：`back()` → `back()` → `back()`

**期望输出**：

```
⬅️  后退到: B
⬅️  后退到: A
❌ 无法后退，后退栈为空！
```

### 测试用例九：刚启动时前进

**操作**：启动浏览器后直接 `forward()`

**期望输出**：

```
❌ 无法前进，前进栈为空！
```

### 测试用例总结表

| 步骤 | 操作 | 当前页面 | 后退栈 | 前进栈 | 说明 |
|------|------|----------|--------|--------|------|
| 1 | visit("A") | A | [] | [] | 初始访问 |
| 2 | visit("B") | B | [A] | [] | 访问新页面 |
| 3 | visit("C") | C | [A, B] | [] | 访问新页面 |
| 4 | back() | B | [A] | [C] | 后退一次 |
| 5 | back() | A | [] | [C, B] | 后退两次 |
| 6 | forward() | B | [A] | [C] | 前进一次 |
| 7 | visit("D") | D | [A, B] | [] | 访问新页面，清空前进栈 |
| 8 | back() | B | [A] | [D] | 后退 |
| 9 | back() | A | [] | [D, B] | 后退到边界 |
| 10 | back() | A | [] | [D, B] | 无法后退 |

## 扩展方向

### 扩展一：历史记录功能

显示所有访问过的页面列表（按时间顺序）：

```cpp
vector<string> history;

void visit(const string& url) {
    if (!currentPage.empty()) {
        backStack.push(currentPage);
    }
    currentPage = url;
    history.push_back(url);  // 记录到历史
    while (!forwardStack.empty()) {
        forwardStack.pop();
    }
}

void printHistory() const {
    cout << "\n=== 历史记录 ===" << endl;
    for (int i = 0; i < history.size(); i++) {
        cout << i + 1 << ". " << history[i] << endl;
    }
}
```

### 扩展二：书签功能

记录特定页面，支持快速访问：

```cpp
vector<string> bookmarks;

void addBookmark(const string& url) {
    bookmarks.push_back(url);
    cout << "已添加书签: " << url << endl;
}

void printBookmarks() const {
    cout << "\n=== 书签 ===" << endl;
    for (int i = 0; i < bookmarks.size(); i++) {
        cout << i + 1 << ". " << bookmarks[i] << endl;
    }
}

void goToBookmark(int index) {
    if (index >= 1 && index <= bookmarks.size()) {
        visit(bookmarks[index - 1]);
    } else {
        cout << "书签索引无效！" << endl;
    }
}
```

### 扩展三：数据持久化

将浏览历史保存到文件：

```cpp
void saveToFile(const string& filename) const {
    ofstream file(filename);
    
    // 保存历史记录
    file << "history:" << endl;
    for (const string& url : history) {
        file << url << endl;
    }
    
    // 保存书签
    file << "bookmarks:" << endl;
    for (const string& url : bookmarks) {
        file << url << endl;
    }
    
    file.close();
    cout << "数据已保存到: " << filename << endl;
}
```

### 扩展四：多标签页

支持多个标签页，每个标签页有自己的浏览历史：

```cpp
class Tab {
public:
    Browser browser;
    string name;
    Tab(string n) : name(n) {}
};

class MultiTabBrowser {
private:
    vector<Tab> tabs;
    int currentTab;
    
public:
    void newTab(const string& name) {
        tabs.push_back(Tab(name));
        currentTab = tabs.size() - 1;
    }
    
    void switchTab(int index) {
        if (index >= 0 && index < tabs.size()) {
            currentTab = index;
        }
    }
    
    Browser& getCurrentBrowser() {
        return tabs[currentTab].browser;
    }
};
```

### 扩展五：双向链表实现

使用双向链表实现更复杂的导航功能：

```cpp
struct HistoryNode {
    string url;
    HistoryNode* prev;
    HistoryNode* next;
    HistoryNode(string u) : url(u), prev(nullptr), next(nullptr) {}
};

class Browser {
private:
    HistoryNode* current;
    
public:
    void visit(const string& url) {
        // 删除当前节点之后的所有节点（清空前进历史）
        while (current->next != nullptr) {
            HistoryNode* temp = current->next;
            current->next = temp->next;
            delete temp;
        }
        
        // 创建新节点
        HistoryNode* newNode = new HistoryNode(url);
        current->next = newNode;
        newNode->prev = current;
        current = newNode;
    }
    
    bool back() {
        if (current->prev == nullptr) return false;
        current = current->prev;
        return true;
    }
    
    bool forward() {
        if (current->next == nullptr) return false;
        current = current->next;
        return true;
    }
    
    void jumpTo(int index) {
        // 跳转到历史中的特定页面
    }
};
```