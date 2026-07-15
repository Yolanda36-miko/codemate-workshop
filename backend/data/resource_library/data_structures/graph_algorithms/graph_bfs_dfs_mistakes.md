# BFS 和 DFS 易错点总结

## 常见错误

### 错误一：BFS 的 visited 标记时机错误

在 BFS 中，将 visited 标记放在出队时而非入队时。

### 错误二：DFS 递归缺少终止条件

忘记检查节点是否已访问，导致无限递归或重复访问。

### 错误三：混淆 BFS 和 DFS 的数据结构

BFS 使用栈（应该用队列），或 DFS 使用队列（应该用栈/递归）。

### 错误四：非连通图只从一个节点出发

对于非连通图，只从一个起始节点遍历，导致漏掉部分节点。

### 错误五：图中有环时未处理 visited

在有环的图中没有 visited 标记，导致死循环。

### 错误六：错误认为 DFS 递归的空间复杂度是 O(1)

忽略递归调用栈的空间开销。

## 错误原因

### 错误一原因

对 BFS 的队列操作理解不深，没有意识到同一节点可能被多次入队。

### 错误二原因

对递归的终止条件理解不清，认为递归会自动终止。

### 错误三原因

对队列（FIFO）和栈（LIFO）的特性理解混淆，不知道它们分别对应哪种遍历顺序。

### 错误四原因

没有考虑图的连通性，默认图是连通的。

### 错误五原因

没有认识到图和树的区别：图可能有环，需要 visited 来避免重复访问。

### 错误六原因

只关注算法的时间复杂度，忽略了递归调用栈的空间开销。

## 正确理解

### visited 标记时机

- **BFS**：必须在**入队时**标记 visited，防止同一节点被多次入队。
- **DFS**：必须在**访问节点时**标记 visited，防止重复访问。

### 递归终止条件

DFS 递归函数的终止条件是：所有邻居都已被访问，或当前节点为空。

### 数据结构选择

- **BFS**：使用队列（FIFO），保证按层访问。
- **DFS**：使用栈（LIFO）或递归调用栈，保证沿路径深入。

### 图的连通性

对于非连通图，需要遍历所有节点，如果节点未被访问，则从该节点发起遍历。

### visited 的必要性

图可能有环，visited 标记是防止重复访问和死循环的关键。

### 空间复杂度分析

递归调用会在系统栈上创建栈帧，栈深度等于递归深度，空间复杂度为 O(V)。

## 错误例子

### 错误一：BFS 的 visited 标记时机错误

**示例图**（0-1, 0-2, 1-2）：
```
0
|\
1-2
```

**错误代码**：

```cpp
void BFSWrong(int start) {
    queue<int> q;
    vector<bool> visited(numVertices, false);
    q.push(start);

    while (!q.empty()) {
        int current = q.front();
        q.pop();
        visited[current] = true;  // 出队时才标记 ← 错误！
        cout << current << " ";

        for (int neighbor : adj[current]) {
            if (!visited[neighbor]) {
                q.push(neighbor);
            }
        }
    }
}
```

**错误后果**：

| 步骤 | 操作 | 队列 | 说明 |
|------|------|------|------|
| 1 | 0 入队 | [0] | |
| 2 | 0 出队，标记，访问 | [] | 0 |
| 3 | 1、2 入队 | [1, 2] | |
| 4 | 1 出队，标记，访问 | [2] | 1 |
| 5 | 0（已访问）、2 入队 | [2, 2] | **2 被重复入队！** |
| 6 | 2 出队，标记，访问 | [2] | 2 |
| 7 | 2 出队，访问 | [] | **2 被重复访问！** |

**错误输出**：`0 1 2 2`

### 错误二：DFS 递归缺少终止条件

**错误代码**：

```cpp
void DFSWrong(int vertex) {
    cout << vertex << " ";  // 没有检查 visited ← 错误！

    for (int neighbor : adj[vertex]) {
        DFSWrong(neighbor);
    }
}
```

**错误后果**：对于有环的图（如 0-1, 1-0），会无限递归，导致栈溢出。

### 错误三：混淆 BFS 和 DFS 的数据结构

**错误代码**（BFS 使用栈）：

```cpp
void BFSWithStack(int start) {
    stack<int> st;  // 错误使用栈！
    vector<bool> visited(numVertices, false);
    st.push(start);
    visited[start] = true;

    while (!st.empty()) {
        int current = st.top();
        st.pop();
        cout << current << " ";

        for (int neighbor : adj[current]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true;
                st.push(neighbor);
            }
        }
    }
}
```

**错误后果**：输出顺序变成了类似 DFS 的顺序，而非 BFS 的按层顺序。

### 错误四：非连通图只从一个节点出发

**示例图**（非连通）：
```
0--1    2--3
```

**错误代码**：

```cpp
void TraverseWrong(int start) {
    BFS(start);  // 只从 start 出发 ← 错误！
}
```

**错误后果**：如果从 0 开始，只能访问节点 0 和 1，节点 2 和 3 被漏掉。

### 错误五：图中有环时未处理 visited

**示例图**（有环）：
```
0--1--2
|     |
+-----+
```

**错误代码**：

```cpp
void TraverseNoVisited(int vertex) {
    cout << vertex << " ";

    for (int neighbor : adj[vertex]) {
        TraverseNoVisited(neighbor);  // 没有检查 visited ← 错误！
    }
}
```

**错误后果**：无限递归（0 → 1 → 2 → 0 → 1 → 2 → ...），导致栈溢出。

### 错误六：错误认为 DFS 递归的空间复杂度是 O(1)

**错误理解**："DFS 只访问每个节点一次，所以空间复杂度是 O(1)。"

**实际情况**：递归调用栈的深度等于图的最长路径长度。对于链状图（0-1-2-3-4），递归深度为 5，空间复杂度为 O(n)。

## 正确做法

### 错误一正确做法

```cpp
void BFS(int start) {
    queue<int> q;
    vector<bool> visited(numVertices, false);

    visited[start] = true;  // 入队时标记
    q.push(start);

    while (!q.empty()) {
        int current = q.front();
        q.pop();
        cout << current << " ";

        for (int neighbor : adj[current]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true;  // 入队时标记
                q.push(neighbor);
            }
        }
    }
}
```

**正确输出**：`0 1 2`

### 错误二正确做法

```cpp
void DFS(int vertex, vector<bool>& visited) {
    visited[vertex] = true;  // 访问时标记
    cout << vertex << " ";

    for (int neighbor : adj[vertex]) {
        if (!visited[neighbor]) {  // 检查 visited
            DFS(neighbor, visited);
        }
    }
}
```

### 错误三正确做法

```cpp
void BFS(int start) {
    queue<int> q;  // BFS 使用队列
    // ...
}

void DFS(int start) {
    stack<int> st;  // DFS 使用栈
    // ...
}
```

### 错误四正确做法

```cpp
void TraverseAll() {
    vector<bool> visited(numVertices, false);
    for (int i = 0; i < numVertices; i++) {
        if (!visited[i]) {
            BFS(i, visited);  // 从每个未访问节点出发
        }
    }
}
```

### 错误五正确做法

```cpp
void Traverse(int vertex, vector<bool>& visited) {
    visited[vertex] = true;
    cout << vertex << " ";

    for (int neighbor : adj[vertex]) {
        if (!visited[neighbor]) {
            Traverse(neighbor, visited);
        }
    }
}
```

### 错误六正确做法

**正确认识**：

| 算法 | 空间复杂度 | 说明 |
|------|-----------|------|
| BFS | O(V) | 队列最多存储所有顶点 |
| DFS（递归） | O(V) | 递归栈深度最多为 V |
| DFS（迭代） | O(V) | 栈最多存储所有顶点 |

## 自查题

### 题目一

**题目描述**：以下 BFS 代码的输出是什么？

```cpp
void BFS(int start) {
    queue<int> q;
    vector<bool> visited(5, false);
    q.push(start);

    while (!q.empty()) {
        int current = q.front();
        q.pop();
        visited[current] = true;  // 出队时标记
        cout << current << " ";

        for (int neighbor : adj[current]) {
            if (!visited[neighbor]) {
                q.push(neighbor);
            }
        }
    }
}
```

**图**：0-1, 0-2, 1-3, 1-4

**答案要点**：输出 `0 1 2 3 4`，但队列中可能出现重复节点。虽然最终输出正确，但效率较低。正确做法是入队时标记 visited。

### 题目二

**题目描述**：指出以下 DFS 代码的错误：

```cpp
void DFS(int vertex) {
    cout << vertex << " ";
    for (int neighbor : adj[vertex]) {
        DFS(neighbor);
    }
}
```

**答案要点**：

1. **缺少 visited 检查**：对于有环的图会导致无限递归。
2. **没有终止条件**：当所有邻居都已访问时，需要通过 visited 检查来终止递归。

**修正代码**：

```cpp
void DFS(int vertex, vector<bool>& visited) {
    visited[vertex] = true;
    cout << vertex << " ";
    for (int neighbor : adj[vertex]) {
        if (!visited[neighbor]) {
            DFS(neighbor, visited);
        }
    }
}
```

### 题目三

**题目描述**：对于图 `0-1, 0-2, 1-3, 1-4`，以下访问序列 `0 1 3 4 2` 可能是由 BFS 还是 DFS 产生的？为什么？

**答案要点**：

**是 DFS 的结果**。理由如下：

- BFS 会按层访问，0 的邻居 1 和 2 应该在同一层被访问，所以序列应该是 `0 1 2 3 4`（或 `0 2 1 3 4`）。
- DFS 沿路径深入，0 → 1 → 3 → 4，回溯到 1，回溯到 0，然后访问 2，符合 `0 1 3 4 2` 的顺序。