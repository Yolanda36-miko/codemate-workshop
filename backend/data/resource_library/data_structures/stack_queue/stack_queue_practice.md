# 栈与队列分层练习题

## 基础题

### 基础题一

**题目描述**

给定以下栈操作序列，画出每一步栈的状态（从栈底到栈顶）：

`push(1), push(2), push(3), pop(), pop(), push(4), pop()`

写出最终栈中剩余的元素。

### 基础题二

**题目描述**

给定一个队列，初始为空，执行以下操作：

`enqueue(10), enqueue(20), enqueue(30), dequeue(), enqueue(40), dequeue()`

请写出每一步的队列状态（队首→队尾），并说明 `dequeue` 操作返回的值。

## 进阶题

### 进阶题一

**题目描述**

补全以下括号匹配代码中的空缺部分（用 `___` 标记）：

```cpp
bool isValidParentheses(string s) {
    stack<char> st;
    for (char c : s) {
        if (c == '(' || c == '[' || c == '{') {
            st.push(c);
        } else {
            // 补全：检查栈是否为空，以及栈顶是否匹配
            if (___ || !isMatching(st.top(), c)) {
                return false;
            }
            ___;
        }
    }
    return ___;
}
```

### 进阶题二

**题目描述**

使用两个栈实现一个队列（称为"用栈实现队列"）。写出：
- 核心数据结构（两个 stack）。
- enqueue 操作的实现思路。
- dequeue 操作的实现思路。

分析每次 enqueue 和 dequeue 的时间复杂度。

### 进阶题三

**题目描述**

分析以下场景应该使用栈还是队列，并说明理由：
- a) 打印机的任务调度。
- b) 文本编辑器的撤销操作（Undo）。
- c) 浏览器的前进后退功能。
- d) 操作系统的进程调度（FCFS）。

### 进阶题四

**题目描述**

给定一个字符串，只包含 `'('` 和 `')'`，判断最长的有效括号子串长度。例如 `"(()"` 的最长有效子串是 `"()"`，长度为 2；`")()())"` 的最长有效子串是 `"()()"`，长度为 4。写出解题思路（可以用栈）。

## 综合题

### 综合题一

**题目描述**

设计一个"最小栈"（Min Stack），支持 push、pop、top 和 getMin（获取栈中最小值）操作，所有操作的时间复杂度均为 O(1)。要求：
- 描述核心数据结构（使用两个栈或一个栈 + 辅助空间）。
- 写出 push、pop、top、getMin 的伪代码。
- 举例说明：依次执行 `push(3), push(1), push(5), getMin(), pop(), getMin()` 的返回值。

### 综合题二

**题目描述**

给定一个整数数组，用一个栈实现"每日温度"问题的求解。问题描述：给定一个数组 T，表示每日温度，返回一个新数组 answer，其中 answer[i] 表示需要等待多少天才能遇到更高的温度。如果之后没有更高的温度，则 answer[i] = 0。例如 T = [73, 74, 75, 71, 69, 72, 76, 73]，返回 [1, 1, 4, 2, 1, 1, 0, 0]。要求：
- 说明为什么可以用栈来解决。
- 写出核心算法伪代码。
- 分析时间复杂度和空间复杂度。

## 每题提示

### 基础题一提示

按照操作顺序逐步模拟，push 是入栈，pop 是出栈。栈的状态从栈底到栈顶描述。

### 基础题二提示

队列是 FIFO，enqueue 在队尾插入，dequeue 从队首删除并返回。

### 进阶题一提示

遇到右括号时，首先检查栈是否为空（没有对应的左括号），然后检查类型是否匹配。

### 进阶题二提示

一个栈用于入队，一个栈用于出队。当出队栈为空时，将入队栈的所有元素弹出并压入出队栈。

### 进阶题三提示

根据场景的访问顺序来判断：先到先服务用队列，后到先服务用栈。

### 进阶题四提示

用栈存储左括号的索引，遇到右括号时弹出栈顶，计算当前位置与新栈顶的距离。

### 综合题一提示

使用两个栈：一个存储所有元素，另一个存储当前最小值。每次 push 时同时更新最小栈。

### 综合题二提示

用栈存储未找到更高温度的日期索引，遍历数组时比较当前温度与栈顶温度。

## 每题检查标准

### 基础题一检查标准

栈的状态顺序正确，每一步操作后的状态与预期一致，最终剩余元素正确。

### 基础题二检查标准

队列状态正确，dequeue 返回的值正确，体现 FIFO 特性。

### 进阶题一检查标准

代码补全后能正确处理各种边界情况（空字符串、只有左括号、只有右括号、类型不匹配）。

### 进阶题二检查标准

enqueue 和 dequeue 的思路正确，时间复杂度分析准确。

### 进阶题三检查标准

每个场景选择的数据结构正确，理由充分，能解释 LIFO/FIFO 与场景的匹配关系。

### 进阶题四检查标准

解题思路清晰，能正确计算最长有效括号长度，边界情况处理正确。

### 综合题一检查标准

数据结构设计合理，所有操作时间复杂度均为 O(1)，示例运行结果正确。

### 综合题二检查标准

算法思路正确，伪代码能解决问题，复杂度分析准确。

## 可选答案要点

### 基础题一答案

**步骤状态**：

| 步骤 | 操作 | 栈状态（栈底→栈顶） |
|------|------|---------------------|
| 1 | push(1) | [1] |
| 2 | push(2) | [1, 2] |
| 3 | push(3) | [1, 2, 3] |
| 4 | pop() | [1, 2] |
| 5 | pop() | [1] |
| 6 | push(4) | [1, 4] |
| 7 | pop() | [1] |

**最终状态**：栈中剩余元素为 `[1]`。

### 基础题二答案

**步骤状态**：

| 步骤 | 操作 | 队列状态（队首→队尾） | dequeue 返回 |
|------|------|---------------------|--------------|
| 1 | enqueue(10) | [10] | — |
| 2 | enqueue(20) | [10, 20] | — |
| 3 | enqueue(30) | [10, 20, 30] | — |
| 4 | dequeue() | [20, 30] | 10 |
| 5 | enqueue(40) | [20, 30, 40] | — |
| 6 | dequeue() | [30, 40] | 20 |

**最终状态**：队列状态为 `[30, 40]`。

### 进阶题一答案

**补全代码**：

```cpp
bool isValidParentheses(string s) {
    stack<char> st;
    for (char c : s) {
        if (c == '(' || c == '[' || c == '{') {
            st.push(c);
        } else {
            if (st.empty() || !isMatching(st.top(), c)) {
                return false;
            }
            st.pop();
        }
    }
    return st.empty();
}
```

**空缺解析**：
1. `st.empty()`：检查栈是否为空（没有对应的左括号）
2. `st.pop()`：匹配成功后弹出栈顶的左括号
3. `st.empty()`：遍历结束后检查栈是否为空（所有左括号都已匹配）

### 进阶题二答案

**核心数据结构**：

```cpp
stack<int> inStack;   // 入队栈
stack<int> outStack;  // 出队栈
```

**enqueue 操作**：

```cpp
void enqueue(int x) {
    inStack.push(x);  // 直接压入入队栈
}
```

**dequeue 操作**：

```cpp
int dequeue() {
    if (outStack.empty()) {
        // 将入队栈的所有元素弹出并压入出队栈（反转顺序）
        while (!inStack.empty()) {
            outStack.push(inStack.top());
            inStack.pop();
        }
    }
    int front = outStack.top();
    outStack.pop();
    return front;
}
```

**时间复杂度分析**：
- **enqueue**：O(1)，直接压栈
- **dequeue**：均摊 O(1)，每个元素最多被压入和弹出两次

### 进阶题三答案

| 场景 | 数据结构 | 理由 |
|------|---------|------|
| a) 打印机任务调度 | 队列 | 需要 FIFO，先提交的任务先打印 |
| b) 文本编辑器撤销 | 栈 | 需要 LIFO，最新的操作最先撤销 |
| c) 浏览器前进后退 | 栈（双栈） | 后退需要 LIFO，前进需要另一个栈 |
| d) 进程调度（FCFS） | 队列 | 需要 FIFO，先到达的进程先执行 |

### 进阶题四答案

**解题思路**：

1. 使用栈存储左括号的索引；
2. 遇到 `(` 时，将其索引压入栈；
3. 遇到 `)` 时：
   - 如果栈不为空且栈顶是 `(` 的索引，弹出栈顶；
   - 当前有效长度 = 当前索引 - 新栈顶索引；
   - 更新最大长度；
4. 栈底保存最后一个未匹配的 `)` 的索引（初始为 -1）。

**伪代码**：

```
function longestValidParentheses(s):
    stack = [-1]
    maxLen = 0
    
    for i from 0 to len(s)-1:
        if s[i] == '(':
            push i to stack
        else:
            pop from stack
            if stack is empty:
                push i to stack
            else:
                currentLen = i - stack.top()
                maxLen = max(maxLen, currentLen)
    
    return maxLen
```

### 综合题一答案

**核心数据结构**：

使用两个栈：
- `dataStack`：存储所有元素
- `minStack`：存储当前最小值序列

**伪代码**：

```
function push(x):
    dataStack.push(x)
    if minStack is empty or x <= minStack.top():
        minStack.push(x)

function pop():
    if dataStack.top() == minStack.top():
        minStack.pop()
    dataStack.pop()

function top():
    return dataStack.top()

function getMin():
    return minStack.top()
```

**示例运行**：

| 操作 | dataStack | minStack | 返回值 |
|------|----------|----------|--------|
| push(3) | [3] | [3] | — |
| push(1) | [3, 1] | [3, 1] | — |
| push(5) | [3, 1, 5] | [3, 1] | — |
| getMin() | [3, 1, 5] | [3, 1] | 1 |
| pop() | [3, 1] | [3, 1] | — |
| getMin() | [3, 1] | [3, 1] | 1 |

### 综合题二答案

**为什么用栈**：

栈可以保存"未找到更高温度"的日期索引，当遇到更高温度时，可以一次性计算之前所有日期的等待天数。

**核心算法伪代码**：

```
function dailyTemperatures(T):
    stack = empty stack
    answer = array of zeros with length len(T)
    
    for i from 0 to len(T)-1:
        while stack is not empty and T[i] > T[stack.top()]:
            prevIndex = stack.pop()
            answer[prevIndex] = i - prevIndex
        push i to stack
    
    return answer
```

**复杂度分析**：

- **时间复杂度**：O(n)，每个元素最多入栈和出栈一次
- **空间复杂度**：O(n)，最坏情况下栈存储所有元素（温度递减）

**示例运行**：

```
T = [73, 74, 75, 71, 69, 72, 76, 73]

步骤：
i=0: stack=[0]
i=1: T[1]=74 > T[0]=73 → answer[0]=1, stack=[1]
i=2: T[2]=75 > T[1]=74 → answer[1]=1, stack=[2]
i=3: T[3]=71 < T[2]=75 → stack=[2, 3]
i=4: T[4]=69 < T[3]=71 → stack=[2, 3, 4]
i=5: T[5]=72 > T[4]=69 → answer[4]=1, stack=[2, 3]
     T[5]=72 > T[3]=71 → answer[3]=2, stack=[2]
i=6: T[6]=76 > T[2]=75 → answer[2]=4, stack=[6]
i=7: T[7]=73 < T[6]=76 → stack=[6, 7]

最终 answer = [1, 1, 4, 2, 1, 1, 0, 0]
```