# BFS 和 DFS 分层练习题

## 基础题

### 基础题一

**题目描述**

给定无向图的邻接表表示：

```
0: [1, 2]
1: [0, 3, 4]
2: [0]
3: [1]
4: [1]
```

**图结构**：
```
    0
   / \
  1   2
 / \
3   4
```

请从节点 0 出发，写出：
1. BFS 的访问序列
2. DFS 的访问序列（假设邻接表按升序排列）

### 基础题二

**题目描述**

判断题：BFS 一定比 DFS 先找到所有节点？（ ）

A. 正确  
B. 错误

## 进阶题

### 进阶题一

**题目描述**

补全以下 BFS 函数中缺失的部分：

```cpp
void BFS(int start) {
    vector<bool> visited(numVertices, ____);  // 空缺1
    queue<int> q;

    visited[start] = true;
    q.push(start);

    while (!q.____()) {  // 空缺2
        int current = q.____();  // 空缺3
        q.pop();
        cout << current << " ";

        for (int neighbor : adj[current]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true;
                q.____(neighbor);  // 空缺4
            }
        }
    }
}
```

### 进阶题二

**题目描述**

对于以下非连通图：

```
0--1    2--3
```

**邻接表**：
```
0: [1]
1: [0]
2: [3]
3: [2]
```

1. 说明为什么只从节点 0 出发进行 BFS/DFS 会漏掉部分节点。
2. 给出改进方法的伪代码或关键步骤。

### 进阶题三

**题目描述**

分析以下两种特殊图下 BFS 和 DFS 递归的空间复杂度：

1. **链状图**：0-1-2-3-4（每个节点只有一个邻居）
2. **星形图**：0 连接 1、2、3、4（中心节点连接所有其他节点）

## 综合题

### 综合题一

**题目描述**

给定一个无向图和两个节点 s 和 t，设计算法判断是否存在从 s 到 t 的路径。

**要求**：
1. 说明用 BFS 还是 DFS 更合适，并解释原因。
2. 给出实现思路和关键代码逻辑。

### 综合题二

**题目描述**

给定一个无向图，判断它是否是二分图。二分图是指可以用两种颜色对图中的节点进行着色，使得相邻节点颜色不同。

**要求**：
1. 写出使用 BFS 着色法的核心逻辑或伪代码。
2. 说明算法的时间复杂度。

## 每题提示

### 基础题一提示

BFS 按层访问，使用队列；DFS 沿路径深入，使用栈或递归。邻接表按升序排列意味着邻居按数字大小顺序访问。

### 基础题二提示

BFS 和 DFS 都会访问所有可达节点，只是访问顺序不同。

### 进阶题一提示

BFS 的核心操作：初始化 visited、队列操作（front、pop、push）、循环条件。

### 进阶题二提示

非连通图由多个连通分量组成，需要遍历每个连通分量。

### 进阶题三提示

空间复杂度取决于队列或递归栈的最大深度/大小。链状图深度大，星形图宽度大。

### 综合题一提示

路径存在性问题，BFS 和 DFS 都可以解决。考虑哪一种更适合找最短路径。

### 综合题二提示

二分图的性质：不存在奇数长度的环。BFS 逐层着色，检查相邻节点颜色是否冲突。

## 每题检查标准

### 基础题一检查标准

BFS 和 DFS 序列顺序完全正确即可。

### 基础题二检查标准

选择正确答案并说明理由。

### 进阶题一检查标准

代码补全后，能够正确输出 BFS 遍历序列。

### 进阶题二检查标准

正确说明原因，并给出可行的改进方法。

### 进阶题三检查标准

正确分析两种图的空间复杂度，并说明理由。

### 综合题一检查标准

算法逻辑正确，能够正确判断路径是否存在。

### 综合题二检查标准

算法逻辑正确，能够正确判断图是否为二分图。

## 可选答案要点

### 基础题一答案

**BFS 序列**：0 → 1 → 2 → 3 → 4

**DFS 序列**：0 → 1 → 3 → 4 → 2

### 基础题二答案

**B. 错误**

**理由**：BFS 和 DFS 都会访问所有可达节点，只是访问顺序不同。不存在谁"先找到"所有节点的说法。

### 进阶题一答案

```cpp
void BFS(int start) {
    vector<bool> visited(numVertices, false);  // 空缺1：false
    queue<int> q;

    visited[start] = true;
    q.push(start);

    while (!q.empty()) {  // 空缺2：empty
        int current = q.front();  // 空缺3：front
        q.pop();
        cout << current << " ";

        for (int neighbor : adj[current]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true;
                q.push(neighbor);  // 空缺4：push
            }
        }
    }
}
```

### 进阶题二答案

**原因**：从节点 0 出发只能访问连通分量 {0, 1}，无法访问另一个连通分量 {2, 3}。

**改进方法**：

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

### 进阶题三答案

**链状图**（0-1-2-3-4）：
- BFS 空间复杂度：O(1)，队列中最多只有一个节点
- DFS 空间复杂度：O(n)，递归栈深度为 n

**星形图**（0 连接 1、2、3、4）：
- BFS 空间复杂度：O(n)，队列中最多有 n-1 个节点（第一层）
- DFS 空间复杂度：O(1)，递归栈深度为 2

### 综合题一答案

**选择 BFS 的原因**：
- BFS 可以同时找到最短路径，而 DFS 不能保证找到最短路径。

**实现思路**：

```cpp
bool hasPath(int s, int t) {
    if (s == t) return true;

    vector<bool> visited(numVertices, false);
    queue<int> q;
    q.push(s);
    visited[s] = true;

    while (!q.empty()) {
        int current = q.front();
        q.pop();

        for (int neighbor : adj[current]) {
            if (neighbor == t) return true;
            if (!visited[neighbor]) {
                visited[neighbor] = true;
                q.push(neighbor);
            }
        }
    }
    return false;
}
```

### 综合题二答案

**核心逻辑**：

```cpp
bool isBipartite() {
    vector<int> color(numVertices, -1);

    for (int i = 0; i < numVertices; i++) {
        if (color[i] == -1) {
            queue<int> q;
            q.push(i);
            color[i] = 0;

            while (!q.empty()) {
                int current = q.front();
                q.pop();

                for (int neighbor : adj[current]) {
                    if (color[neighbor] == -1) {
                        color[neighbor] = color[current] ^ 1;
                        q.push(neighbor);
                    } else if (color[neighbor] == color[current]) {
                        return false;
                    }
                }
            }
        }
    }
    return true;
}
```

**时间复杂度**：O(V + E)

**算法说明**：
1. 使用颜色数组，-1 表示未着色，0 和 1 表示两种颜色。
2. 对于每个未着色的节点，使用 BFS 逐层着色。
3. 如果发现相邻节点颜色相同，则不是二分图。