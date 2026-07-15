# BFS 和 DFS C++ 代码示例

## 代码目标

本代码演示无向图的 BFS（广度优先搜索）和 DFS（深度优先搜索）遍历算法。使用邻接表表示图，展示递归实现的 DFS 和迭代实现的 BFS。

## 核心代码

```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;

class Graph {
private:
    int numVertices;
    vector<vector<int>> adj;

public:
    Graph(int vertices) : numVertices(vertices) {
        adj.resize(numVertices);
    }

    void addEdge(int src, int dest) {
        adj[src].push_back(dest);
        adj[dest].push_back(src);
        sort(adj[src].begin(), adj[src].end());
        sort(adj[dest].begin(), adj[dest].end());
    }

    void BFS(int start) {
        vector<bool> visited(numVertices, false);
        queue<int> q;

        visited[start] = true;
        q.push(start);

        cout << "BFS (starting from " << start << "): ";
        while (!q.empty()) {
            int current = q.front();
            q.pop();
            cout << current << " ";

            for (int neighbor : adj[current]) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    q.push(neighbor);
                }
            }
        }
        cout << endl;
    }

    void DFS(int start) {
        vector<bool> visited(numVertices, false);
        cout << "DFS (starting from " << start << "): ";
        DFSUtil(start, visited);
        cout << endl;
    }

private:
    void DFSUtil(int vertex, vector<bool>& visited) {
        visited[vertex] = true;
        cout << vertex << " ";

        for (int neighbor : adj[vertex]) {
            if (!visited[neighbor]) {
                DFSUtil(neighbor, visited);
            }
        }
    }
};

int main() {
    Graph g(5);
    g.addEdge(0, 1);
    g.addEdge(0, 2);
    g.addEdge(1, 3);
    g.addEdge(1, 4);

    g.BFS(0);
    g.DFS(0);

    return 0;
}
```

## 关键步骤解释

### 1. 图类定义

```cpp
class Graph {
private:
    int numVertices;
    vector<vector<int>> adj;
public:
    Graph(int vertices) : numVertices(vertices) {
        adj.resize(numVertices);
    }
};
```

- `numVertices`：图的顶点数量
- `adj`：邻接表，`adj[i]` 存储顶点 `i` 的所有邻居
- 构造函数初始化邻接表大小

### 2. 添加边

```cpp
void addEdge(int src, int dest) {
    adj[src].push_back(dest);
    adj[dest].push_back(src);
    sort(adj[src].begin(), adj[src].end());
    sort(adj[dest].begin(), adj[dest].end());
}
```

- 对于无向图，需要在两个顶点的邻接表中互相添加
- 排序保证邻居按顺序访问，使输出结果可预测

### 3. BFS 实现

```cpp
void BFS(int start) {
    vector<bool> visited(numVertices, false);
    queue<int> q;

    visited[start] = true;
    q.push(start);

    while (!q.empty()) {
        int current = q.front();
        q.pop();
        cout << current << " ";

        for (int neighbor : adj[current]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true;
                q.push(neighbor);
            }
        }
    }
}
```

- **visited 数组**：记录节点是否已访问
- **队列**：存储待处理的节点
- **入队时标记**：在将邻居入队时标记为已访问，避免重复入队

### 4. DFS 实现

```cpp
void DFS(int start) {
    vector<bool> visited(numVertices, false);
    DFSUtil(start, visited);
}

void DFSUtil(int vertex, vector<bool>& visited) {
    visited[vertex] = true;
    cout << vertex << " ";

    for (int neighbor : adj[vertex]) {
        if (!visited[neighbor]) {
            DFSUtil(neighbor, visited);
        }
    }
}
```

- **递归函数 DFSUtil**：执行实际的深度优先遍历
- **终止条件**：当所有邻居都已访问时，自动回溯
- **递归调用栈**：系统自动维护递归调用栈

### 5. 为什么 BFS 用队列，DFS 用递归

- **BFS**：需要按层访问，队列的"先进先出"特性保证先入队的节点先被处理
- **DFS**：需要沿路径深入，递归调用栈的"后进先出"特性保证最后访问的分支最先被处理

## 输入输出示例

### 输入图结构

```
    0
   / \
  1   2
 / \
3   4
```

### 邻接表

```
0: [1, 2]
1: [0, 3, 4]
2: [0]
3: [1]
4: [1]
```

### 输出

```
BFS (starting from 0): 0 1 2 3 4
DFS (starting from 0): 0 1 3 4 2
```

### 输出解释

- **BFS**：按层访问，先访问距离为1的节点（1, 2），再访问距离为2的节点（3, 4）
- **DFS**：沿路径深入，0 → 1 → 3，回溯到1 → 4，回溯到1，回溯到0 → 2

## 边界条件

### 空图

当 `numVertices = 0` 时，BFS 和 DFS 直接返回，不执行任何操作。

### 单节点图

只有一个顶点，没有边。BFS 和 DFS 都只访问该节点。

### 非连通图

本示例只演示从给定起点出发的遍历。对于非连通图，需要遍历所有顶点，如果顶点未被访问，则从该顶点发起遍历：

```cpp
void BFSAll() {
    vector<bool> visited(numVertices, false);
    for (int i = 0; i < numVertices; i++) {
        if (!visited[i]) {
            BFS(i);
        }
    }
}
```

### 有环图

visited 数组保证不会重复访问节点，避免无限循环。

## 时间复杂度和空间复杂度

### BFS

**时间复杂度**：O(V + E)
- 每个顶点入队和出队各一次：O(V)
- 每条边被处理两次（无向图）：O(E)

**空间复杂度**：O(V)
- visited 数组：O(V)
- 队列最多存储所有顶点：O(V)

### DFS

**时间复杂度**：O(V + E)
- 每个顶点被访问一次：O(V)
- 每条边被处理两次（无向图）：O(E)

**空间复杂度**：O(V)
- visited 数组：O(V)
- 递归调用栈深度最多为 V（链状图）：O(V)

### 对比

| 算法 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| BFS | O(V + E) | O(V) |
| DFS | O(V + E) | O(V) |

## 改写练习

### 练习一：将 DFS 递归版本改写为迭代版本

**提示**：使用显式栈替代递归调用栈。

**参考代码框架**：

```cpp
void DFSIterative(int start) {
    vector<bool> visited(numVertices, false);
    stack<int> st;
    st.push(start);
    visited[start] = true;

    cout << "DFS Iterative: ";
    while (!st.empty()) {
        int current = st.top();
        st.pop();
        cout << current << " ";

        for (auto it = adj[current].rbegin(); it != adj[current].rend(); ++it) {
            int neighbor = *it;
            if (!visited[neighbor]) {
                visited[neighbor] = true;
                st.push(neighbor);
            }
        }
    }
    cout << endl;
}
```

### 练习二：计算从起点到所有节点的最短路径长度

**提示**：BFS 天然适合计算无权图的最短路径。

**参考代码框架**：

```cpp
void BFSShortestPath(int start) {
    vector<int> distance(numVertices, -1);
    queue<int> q;

    distance[start] = 0;
    q.push(start);

    while (!q.empty()) {
        int current = q.front();
        q.pop();

        for (int neighbor : adj[current]) {
            if (distance[neighbor] == -1) {
                distance[neighbor] = distance[current] + 1;
                q.push(neighbor);
            }
        }
    }

    for (int i = 0; i < numVertices; i++) {
        cout << "Distance from " << start << " to " << i << ": " << distance[i] << endl;
    }
}
```

### 练习三：修改代码以支持有向图

**提示**：修改 `addEdge` 函数，只添加单向边。

**参考代码**：

```cpp
void addDirectedEdge(int src, int dest) {
    adj[src].push_back(dest);
    sort(adj[src].begin(), adj[src].end());
}
```