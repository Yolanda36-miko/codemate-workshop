# 栈与队列易错点总结

## 常见错误

### 错误一：栈操作时忘记判空

执行 `pop` 或 `top` 前未检查栈是否为空，导致运行时错误（访问非法内存）。

### 错误二：括号匹配中混淆括号类型

用右括号 `)` 去匹配左括号 `[`，导致匹配失败或误判。

### 错误三：队列操作中混淆队首和队尾

错误地从队尾删除元素，或从队首插入元素，破坏了 FIFO 规则。

### 错误四：循环队列实现中指针更新顺序错误

`front` 和 `rear` 的更新顺序导致队列状态错乱或数据覆盖。

### 错误五：数据结构选型错误

将栈用于"先到先服务"场景，或将队列用于"后到先服务"场景。

### 错误六：低效的队列实现

使用数组实现队列并移动所有元素导致 O(n) 复杂度，忽略循环队列或链表实现。

## 错误原因

### 错误一原因

对栈的边界条件考虑不周全，认为"调用时栈一定有元素"，或对 STL `stack` 的行为不熟悉。

### 错误二原因

对括号匹配的逻辑理解不深，只检查是否有左括号，不检查类型是否匹配。

### 错误三原因

对队列的 FIFO 特性理解不清晰，混淆了队首和队尾的操作位置。

### 错误四原因

对循环队列的指针更新逻辑理解混乱，不清楚 `front` 和 `rear` 的先后更新顺序。

### 错误五原因

对栈和队列的适用场景理解不足，不知道何时该用哪种数据结构。

### 错误六原因

对队列的实现方式了解不够，只知道简单的数组模拟，不知道更高效的实现方法。

## 正确理解

### 栈的操作规范

- **判空优先**：执行 `pop` 或 `top` 前必须检查栈是否为空
- **LIFO 原则**：只能从栈顶插入和删除
- **STL stack**：对空栈执行 `pop` 或 `top` 会导致未定义行为

### 括号匹配的核心逻辑

- **类型匹配**：右括号必须与最近的左括号类型相同
- **栈的作用**：保存左括号的顺序，确保嵌套正确
- **三种括号**：`()`、`[]`、`{}` 必须分别匹配

### 队列的操作规范

- **FIFO 原则**：队首删除，队尾插入
- **判空优先**：执行 `dequeue` 或 `front` 前必须检查队列是否为空
- **STL queue**：`push` 在队尾，`pop` 删除队首

### 循环队列的指针更新

- **rear 先更新**：入队时先移动 `rear` 再写入数据
- **front 先更新**：出队时先读取数据再移动 `front`
- **空满判断**：`front == rear` 表示空，`(rear+1)%capacity == front` 表示满

### 数据结构选型指南

| 场景 | 应使用 | 原因 |
|------|--------|------|
| 括号匹配 | 栈 | 需要 LIFO，最近的左括号最先匹配 |
| 撤销操作 | 栈 | 需要 LIFO，最新的操作最先撤销 |
| 函数调用 | 栈 | 需要 LIFO，最后调用的函数最先返回 |
| 排队服务 | 队列 | 需要 FIFO，先到的先服务 |
| 消息队列 | 队列 | 需要 FIFO，先发送的消息先处理 |
| BFS 遍历 | 队列 | 需要 FIFO，按层次顺序处理 |

### 队列的高效实现

- **循环队列**：使用数组 + 双指针，避免元素移动
- **链表队列**：使用链表，动态分配内存
- **STL queue**：底层使用 deque，效率高

## 错误例子

### 错误一：栈操作时忘记判空

**错误代码**：

```cpp
bool isValidParentheses(string expr) {
    stack<char> st;
    
    for (char c : expr) {
        if (c == '(' || c == '[' || c == '{') {
            st.push(c);
        } else if (c == ')' || c == ']' || c == '}') {
            char top = st.top();  // ❌ 栈可能为空!
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

**错误后果**：当输入只有右括号时（如 `")))"`），栈为空，执行 `st.top()` 会导致程序崩溃。

### 错误二：括号匹配中混淆括号类型

**错误代码**：

```cpp
bool isValidParentheses(string expr) {
    stack<char> st;
    
    for (char c : expr) {
        if (c == '(' || c == '[' || c == '{') {
            st.push(c);
        } else if (c == ')' || c == ']' || c == '}') {
            if (st.empty()) return false;
            char top = st.top();
            // ❌ 错误：只检查是否是左括号，不检查类型
            if (top == '(' || top == '[' || top == '{') {
                st.pop();
            } else {
                return false;
            }
        }
    }
    
    return st.empty();
}
```

**错误后果**：表达式 `([)]` 会被错误判断为匹配成功，因为代码只检查栈顶是否是左括号，不检查类型是否匹配。

### 错误三：队列操作中混淆队首和队尾

**错误代码**：

```cpp
void processQueue(vector<int>& q) {
    // ❌ 错误：从队尾删除，破坏 FIFO
    q.pop_back();
    
    // ❌ 错误：从队首插入，破坏 FIFO
    q.insert(q.begin(), 5);
}
```

**错误后果**：
- `pop_back()` 删除的是最后加入的元素，而不是最先加入的
- `insert(q.begin(), 5)` 将新元素插入到队首，违背了"排队"的原则

### 错误四：循环队列实现中指针更新顺序错误

**错误代码**：

```cpp
class CircularQueue {
private:
    int* data;
    int front, rear;
    int capacity;
    
public:
    bool enqueue(int x) {
        if (isFull()) return false;
        
        data[rear] = x;  // ❌ 先写入数据，再更新指针
        rear = (rear + 1) % capacity;
        
        return true;
    }
    
    int dequeue() {
        if (isEmpty()) return -1;
        
        front = (front + 1) % capacity;  // ❌ 先更新指针，再读取数据
        return data[front];
    }
};
```

**错误后果**：
- `enqueue` 中先写入数据会覆盖未读取的数据（当队列满时）
- `dequeue` 中先更新指针会跳过当前元素，读取到错误的数据

### 错误五：数据结构选型错误

**错误场景**：使用栈来模拟银行排队。

```cpp
void bankSimulation(stack<int>& s) {
    // 客户按到达顺序入栈
    s.push(1);  // 第一个到达
    s.push(2);  // 第二个到达
    s.push(3);  // 第三个到达
    
    // ❌ 使用栈，最后到达的客户最先被服务
    while (!s.empty()) {
        cout << "服务客户 " << s.top() << endl;  // 输出: 3, 2, 1
        s.pop();
    }
}
```

**错误后果**：客户 3 最后到达却最先被服务，违背了"先到先服务"的原则。

### 错误六：低效的队列实现

**错误代码**：

```cpp
void inefficientDequeue(vector<int>& q) {
    int front = q[0];
    
    // ❌ 将所有元素向前移动一位，O(n) 复杂度
    for (int i = 0; i < q.size() - 1; i++) {
        q[i] = q[i + 1];
    }
    q.pop_back();
    
    cout << "出队: " << front << endl;
}
```

**错误后果**：每次出队需要移动 n-1 个元素，时间复杂度为 O(n)，当队列很大时效率极低。

## 正确做法

### 正确做法一：栈操作前判空

```cpp
bool isValidParentheses(string expr) {
    stack<char> st;
    
    for (char c : expr) {
        if (c == '(' || c == '[' || c == '{') {
            st.push(c);
        } else if (c == ')' || c == ']' || c == '}') {
            if (st.empty()) return false;  // ✅ 先判空
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

### 正确做法二：括号类型精确匹配

```cpp
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
        } else if (c == ')' || c == ']' || c == '}') {
            if (st.empty()) return false;
            char top = st.top();
            if (isMatching(top, c)) {  // ✅ 精确匹配
                st.pop();
            } else {
                return false;
            }
        }
    }
    
    return st.empty();
}
```

### 正确做法三：队列操作遵循 FIFO

```cpp
void processQueue(queue<int>& q) {
    q.pop();        // ✅ 从队首删除
    q.push(5);      // ✅ 从队尾插入
}
```

### 正确做法四：循环队列指针正确更新

```cpp
class CircularQueue {
private:
    int* data;
    int front, rear;
    int capacity;
    
public:
    bool enqueue(int x) {
        if (isFull()) return false;
        
        rear = (rear + 1) % capacity;  // ✅ 先更新指针
        data[rear] = x;                // ✅ 再写入数据
        
        return true;
    }
    
    int dequeue() {
        if (isEmpty()) return -1;
        
        front = (front + 1) % capacity;  // ✅ 先更新指针
        return data[front];              // ✅ 再读取数据
    }
};
```

### 正确做法五：选择正确的数据结构

```cpp
void bankSimulation(queue<int>& q) {
    // 客户按到达顺序入队
    q.push(1);  // 第一个到达
    q.push(2);  // 第二个到达
    q.push(3);  // 第三个到达
    
    // ✅ 使用队列，先到的客户先被服务
    while (!q.empty()) {
        cout << "服务客户 " << q.front() << endl;  // 输出: 1, 2, 3
        q.pop();
    }
}
```

### 正确做法六：高效的队列实现

```cpp
void efficientDequeue(queue<int>& q) {
    if (q.empty()) return;
    
    int front = q.front();
    q.pop();  // ✅ O(1) 复杂度
    
    cout << "出队: " << front << endl;
}
```

## 自查题

### 题目一

**题目描述**：以下是一个括号匹配的错误实现，请指出错误并修正。

```cpp
bool isValidParentheses(string expr) {
    stack<char> st;
    
    for (char c : expr) {
        if (c == '(' || c == '[' || c == '{') {
            st.push(c);
        } else if (c == ')' || c == ']' || c == '}') {
            char top = st.top();
            if (top == '(' || top == '[' || top == '{') {
                st.pop();
            } else {
                return false;
            }
        }
    }
    
    return true;
}
```

**答案要点**：

**错误一**：第 8 行 `st.top()` 前未判空，如果输入只有右括号会崩溃。

**错误二**：第 9 行只检查栈顶是否是左括号，不检查类型是否匹配，`([)]` 会被误判为正确。

**错误三**：第 18 行返回 `true`，应该返回 `st.empty()`，否则 `"((("` 会被误判为正确。

**修正后的代码**：

```cpp
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
        } else if (c == ')' || c == ']' || c == '}') {
            if (st.empty()) return false;  // ✅ 判空
            char top = st.top();
            if (isMatching(top, c)) {      // ✅ 类型匹配
                st.pop();
            } else {
                return false;
            }
        }
    }
    
    return st.empty();  // ✅ 检查栈是否为空
}
```

### 题目二

**题目描述**：以下是一个队列操作的错误逻辑，请指出问题并修正。

```cpp
void simulateQueue(vector<int>& q) {
    q.push_back(1);  // 入队
    q.push_back(2);  // 入队
    q.push_back(3);  // 入队
    
    q.pop_back();    // 出队（错误！）
    q.push_back(4);  // 入队
    
    // 期望输出：2, 3, 4
    for (int x : q) {
        cout << x << " ";
    }
}
```

**答案要点**：

**错误**：第 8 行 `q.pop_back()` 从队尾删除元素，而不是队首。

**后果**：删除的是 3（最后入队的），而不是 1（最先入队的）。

**输出**：实际输出 `1 2 4`，而非期望的 `2 3 4`。

**修正方案**：

```cpp
void simulateQueue(queue<int>& q) {
    q.push(1);
    q.push(2);
    q.push(3);
    
    q.pop();  // ✅ 从队首删除
    q.push(4);
    
    while (!q.empty()) {
        cout << q.front() << " ";
        q.pop();
    }
    // 输出：2 3 4
}
```

### 题目三

**题目描述**：请为以下场景选择合适的数据结构，并说明理由：

1. **浏览器后退功能**：用户点击"后退"按钮，返回到上一个页面。
2. **打印机任务队列**：多个文档按提交顺序排队等待打印。
3. **表达式求值**：计算中缀表达式的值（如 `3 + 4 * 2`）。

**答案要点**：

**场景一：浏览器后退功能**

**选择**：栈（Stack）

**理由**：需要"后进先出"（LIFO），最新访问的页面最先返回。

```
访问顺序：A → B → C → D
后退顺序：D → C → B → A（最后访问的最先返回）
```

**场景二：打印机任务队列**

**选择**：队列（Queue）

**理由**：需要"先进先出"（FIFO），先提交的文档先打印。

```
提交顺序：文档1 → 文档2 → 文档3
打印顺序：文档1 → 文档2 → 文档3（先提交的先打印）
```

**场景三：表达式求值**

**选择**：栈（Stack）

**理由**：运算符和操作数需要按特定顺序处理，栈可以保存中间结果。

```
表达式：3 + 4 * 2
计算过程：
1. 3 入栈 → [3]
2. + 入栈 → [3, +]
3. 4 入栈 → [3, +, 4]
4. * 入栈 → [3, +, 4, *]
5. 2 入栈 → [3, +, 4, *, 2]
6. 遇到结束符，弹出 2 和 4，计算 4*2=8 → [3, +, 8]
7. 弹出 8 和 3，计算 3+8=11 → [11]
```

**总结**：

| 场景 | 数据结构 | 原则 |
|------|---------|------|
| 浏览器后退 | 栈 | LIFO |
| 打印机任务 | 队列 | FIFO |
| 表达式求值 | 栈 | LIFO |