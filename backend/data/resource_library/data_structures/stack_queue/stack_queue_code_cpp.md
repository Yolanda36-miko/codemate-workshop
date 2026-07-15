# 栈与队列代码示例

## 代码目标

本代码通过两个典型应用演示栈和队列的核心操作：

**栈的应用 — 括号匹配**：检查表达式中的括号是否成对且正确嵌套。

**队列的应用 — 银行排队叫号系统**：按到达顺序依次处理客户，模拟"先到先服务"的场景。

通过这两个应用，直观对比栈（LIFO）和队列（FIFO）的使用场景差异。

## 核心代码

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <string>
using namespace std;

bool isMatching(char open, char close) {
    return (open == '(' && close == ')') ||
           (open == '[' && close == ']') ||
           (open == '{' && close == '}');
}

bool isValidParentheses(string expr) {
    stack<char> st;
    
    for (char c : expr) {
        if (c == '(' || c == '[' || c == '{') {
            st.push(c);
            cout << "  遇到左括号 '" << c << "'，压入栈 → 栈顶: " << c << endl;
        } else if (c == ')' || c == ']' || c == '}') {
            if (st.empty()) {
                cout << "  遇到右括号 '" << c << "'，但栈为空 → 匹配失败" << endl;
                return false;
            }
            char top = st.top();
            if (isMatching(top, c)) {
                st.pop();
                cout << "  遇到右括号 '" << c << "'，与栈顶 '" << top << "' 匹配，弹出栈 → 栈顶: " 
                     << (st.empty() ? "空" : string(1, st.top())) << endl;
            } else {
                cout << "  遇到右括号 '" << c << "'，与栈顶 '" << top << "' 不匹配 → 匹配失败" << endl;
                return false;
            }
        }
    }
    
    if (st.empty()) {
        cout << "  遍历结束，栈为空 → 匹配成功" << endl;
        return true;
    } else {
        cout << "  遍历结束，栈不为空（还剩 " << st.size() << " 个左括号）→ 匹配失败" << endl;
        return false;
    }
}

void simulateBankQueue() {
    queue<int> q;
    int customerId = 1;
    
    cout << "客户 " << customerId << " 到达，正在排队..." << endl;
    q.push(customerId++);
    
    cout << "客户 " << customerId << " 到达，正在排队..." << endl;
    q.push(customerId++);
    
    cout << "客户 " << customerId << " 到达，正在排队..." << endl;
    q.push(customerId++);
    
    cout << "正在服务客户 " << q.front() << " ... 服务完成，已离开。" << endl;
    q.pop();
    
    cout << "正在服务客户 " << q.front() << " ... 服务完成，已离开。" << endl;
    q.pop();
    
    cout << "客户 " << customerId << " 到达，正在排队..." << endl;
    q.push(customerId++);
    
    cout << "正在服务客户 " << q.front() << " ... 服务完成，已离开。" << endl;
    q.pop();
    
    cout << "正在服务客户 " << q.front() << " ... 服务完成，已离开。" << endl;
    q.pop();
    
    if (q.empty()) {
        cout << "所有客户已服务完毕！" << endl;
    }
}

int main() {
    cout << "=== 括号匹配测试 ===" << endl;
    
    string expressions[] = {"()", "([]{})", "([)]", "(()"};
    for (string expr : expressions) {
        cout << "\n表达式: " << expr << endl;
        bool result = isValidParentheses(expr);
        cout << (result ? "✅ 括号匹配正确" : "❌ 括号匹配错误") << endl;
    }
    
    cout << "\n\n=== 银行排队模拟 ===" << endl;
    simulateBankQueue();
    
    return 0;
}
```

## 关键步骤解释

### 括号匹配函数

```cpp
bool isValidParentheses(string expr) {
    stack<char> st;
    
    for (char c : expr) {
        if (c == '(' || c == '[' || c == '{') {
            st.push(c);
        } else if (c == ')' || c == ']' || c == '}') {
            if (st.empty()) return false;
            char top = st.top();
            if (isMatching(top, c)) {
                st.pop();
            } else {
                return false;
            }
        }
    }
    
    return st.empty();
}
```

**解释**：
1. 遍历字符串中的每个字符；
2. 遇到左括号，压入栈；
3. 遇到右括号：
   - 如果栈为空，说明没有对应的左括号，匹配失败；
   - 如果栈顶不是对应的左括号，匹配失败；
   - 如果匹配成功，弹出栈顶；
4. 遍历结束后，如果栈为空，说明所有括号都匹配成功。

### 银行排队模拟

```cpp
void simulateBankQueue() {
    queue<int> q;
    
    q.push(1);  // 客户 1 入队
    q.push(2);  // 客户 2 入队
    q.push(3);  // 客户 3 入队
    
    q.pop();    // 客户 1 出队（先到先服务）
    q.pop();    // 客户 2 出队
    q.push(4);  // 客户 4 入队
    q.pop();    // 客户 3 出队
    q.pop();    // 客户 4 出队
}
```

**解释**：
1. 客户按到达顺序入队；
2. 服务时按到达顺序出队（先进先出）；
3. 新来的客户加入队尾；
4. 体现"先到先服务"的原则。

### 栈与队列的使用场景对比

| 场景 | 使用数据结构 | 原因 |
|------|------------|------|
| 括号匹配 | 栈 | 需要"后进先出"，最后遇到的左括号最先匹配 |
| 函数调用栈 | 栈 | 最后调用的函数最先返回 |
| 撤销/回退操作 | 栈 | 最新的操作最先撤销 |
| 排队服务 | 队列 | 需要"先进先出"，先到的先服务 |
| 消息队列 | 队列 | 先发送的消息先处理 |
| BFS 遍历 | 队列 | 需要按层次顺序处理节点 |

## 输入输出示例

运行上述代码，输出结果为：

```
=== 括号匹配测试 ===

表达式: ()
  遇到左括号 '(', 压入栈 → 栈顶: (
  遇到右括号 ')', 与栈顶 '(' 匹配，弹出栈 → 栈顶: 空
  遍历结束，栈为空 → 匹配成功
✅ 括号匹配正确

表达式: ([]{})
  遇到左括号 '(', 压入栈 → 栈顶: (
  遇到左括号 '[', 压入栈 → 栈顶: [
  遇到右括号 ']', 与栈顶 '[' 匹配，弹出栈 → 栈顶: (
  遇到左括号 '{', 压入栈 → 栈顶: {
  遇到右括号 '}', 与栈顶 '{' 匹配，弹出栈 → 栈顶: (
  遇到右括号 ')', 与栈顶 '(' 匹配，弹出栈 → 栈顶: 空
  遍历结束，栈为空 → 匹配成功
✅ 括号匹配正确

表达式: ([)]
  遇到左括号 '(', 压入栈 → 栈顶: (
  遇到左括号 '[', 压入栈 → 栈顶: [
  遇到右括号 ')', 与栈顶 '[' 不匹配 → 匹配失败
❌ 括号匹配错误

表达式: (()
  遇到左括号 '(', 压入栈 → 栈顶: (
  遇到左括号 '(', 压入栈 → 栈顶: (
  遇到右括号 ')', 与栈顶 '(' 匹配，弹出栈 → 栈顶: (
  遍历结束，栈不为空（还剩 1 个左括号）→ 匹配失败
❌ 括号匹配错误


=== 银行排队模拟 ===
客户 1 到达，正在排队...
客户 2 到达，正在排队...
客户 3 到达，正在排队...
正在服务客户 1 ... 服务完成，已离开。
正在服务客户 2 ... 服务完成，已离开。
客户 4 到达，正在排队...
正在服务客户 3 ... 服务完成，已离开。
正在服务客户 4 ... 服务完成，已离开。
所有客户已服务完毕！
```

## 边界条件

### 括号匹配的边界条件

**空字符串**：

```cpp
// 输入: ""
// 期望输出: true
bool isValidParentheses("") {
    stack<char> st;
    // 循环不执行，直接返回 st.empty() = true
    return true;
}
```

**只有左括号**：

```cpp
// 输入: "((("
// 期望输出: false
// 遍历结束后栈不为空，返回 false
```

**只有右括号**：

```cpp
// 输入: ")))"
// 期望输出: false
// 遇到第一个右括号时栈为空，直接返回 false
```

**不同括号类型混合**：

```cpp
// 输入: "(]"
// 期望输出: false
// 栈顶是 '('，遇到 ']' 不匹配，返回 false
```

### 队列模拟的边界条件

**空队列**：

```cpp
if (!q.empty()) {
    cout << "正在服务客户 " << q.front() << endl;
    q.pop();
} else {
    cout << "队列为空，没有客户需要服务" << endl;
}
```

**大量客户**：

队列可以不断增长，模拟长时间运行的服务场景：

```cpp
for (int i = 1; i <= 1000; i++) {
    q.push(i);
}
while (!q.empty()) {
    q.pop();
}
```

## 时间复杂度和空间复杂度

### 括号匹配

**时间复杂度**：O(n)
- 遍历一次字符串，每个字符处理一次；
- 栈的 push/pop 操作均为 O(1)。

**空间复杂度**：O(n)
- 最坏情况下所有字符都是左括号，栈的大小为 n；
- 最好情况下栈的大小为 0（空字符串或完全匹配）。

### 队列模拟

**时间复杂度**：O(n)
- 每个客户入队/出队一次，总共 O(n) 次操作；
- 每次入队/出队操作都是 O(1)。

**空间复杂度**：O(n)
- 队列中最多同时容纳的客户数；
- 最坏情况下所有客户同时排队。

## 改写练习

### 练习一：扩展括号匹配

支持更多括号类型（如 `<` 和 `>`，以及单引号和双引号）：

```cpp
bool isMatching(char open, char close) {
    return (open == '(' && close == ')') ||
           (open == '[' && close == ']') ||
           (open == '{' && close == '}') ||
           (open == '<' && close == '>') ||
           (open == '\'' && close == '\'') ||
           (open == '"' && close == '"');
}

bool isValidParentheses(string expr) {
    stack<char> st;
    
    for (char c : expr) {
        if (c == '(' || c == '[' || c == '{' || c == '<' || c == '\'' || c == '"') {
            st.push(c);
        } else if (c == ')' || c == ']' || c == '}' || c == '>' || c == '\'' || c == '"') {
            if (st.empty()) return false;
            char top = st.top();
            if (isMatching(top, c)) {
                st.pop();
            } else {
                return false;
            }
        }
    }
    
    return st.empty();
}
```

### 练习二：多窗口银行排队

模拟多个服务窗口并行服务：

```cpp
void simulateMultiWindowBankQueue() {
    const int NUM_WINDOWS = 2;
    queue<int> windows[NUM_WINDOWS];
    int customerId = 1;
    
    for (int i = 0; i < 5; i++) {
        int window = i % NUM_WINDOWS;
        cout << "客户 " << customerId << " 到达，前往窗口 " << window + 1 << " 排队..." << endl;
        windows[window].push(customerId++);
    }
    
    for (int w = 0; w < NUM_WINDOWS; w++) {
        cout << "\n窗口 " << w + 1 << " 开始服务:" << endl;
        while (!windows[w].empty()) {
            cout << "  正在服务客户 " << windows[w].front() << " ... 完成" << endl;
            windows[w].pop();
        }
    }
}
```

### 练习三：浏览器后退功能

使用栈实现浏览器后退功能：

```cpp
class BrowserHistory {
private:
    stack<string> history;
    
public:
    void visit(string url) {
        history.push(url);
        cout << "访问: " << url << endl;
    }
    
    string back() {
        if (history.empty()) {
            cout << "没有历史记录" << endl;
            return "";
        }
        history.pop();
        string current = history.empty() ? "首页" : history.top();
        cout << "后退到: " << current << endl;
        return current;
    }
    
    string current() {
        return history.empty() ? "首页" : history.top();
    }
};

int main() {
    BrowserHistory browser;
    browser.visit("https://www.google.com");
    browser.visit("https://www.github.com");
    browser.visit("https://www.stackoverflow.com");
    browser.back();  // 返回 github
    browser.back();  // 返回 google
    browser.back();  // 返回首页
    return 0;
}
```