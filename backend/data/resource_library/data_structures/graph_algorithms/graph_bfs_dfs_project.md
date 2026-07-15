# 迷宫寻径系统

## 项目场景

在游戏开发、机器人导航和路径规划等领域，迷宫寻径是一个经典问题。本项目设计一个"迷宫寻径系统"，给定一个二维网格迷宫（0 表示通路，1 表示墙壁），从起点到终点，使用 BFS 和 DFS 分别寻找路径。

**核心对比**：
- **BFS**：用于求最短路径（按层扩展，保证找到最短路径）
- **DFS**：用于求一条可行路径（沿路径深入，不保证最短）

通过这个项目，可以直观展示两种遍历策略在实际问题中的搜索过程和结果差异。

## 任务目标

1. **迷宫建模**：用二维矩阵表示迷宫，支持自定义大小和障碍物布局
2. **BFS 最短路径**：实现 BFS 算法，输出从起点到终点的最短路径
3. **DFS 可行路径**：实现 DFS 算法，输出一条可行路径
4. **结果对比**：对比两种算法的路径长度和搜索节点数
5. **统计分析**：记录并展示搜索过程中的统计信息

## 为什么使用该数据结构

迷宫可以自然地建模为**网格图**：
- 每个格子是一个节点
- 上下左右四个方向（在边界内且为通路）的相邻格子构成边

BFS 和 DFS 是图遍历的两种基本策略：
- **BFS**：使用队列（FIFO），按层扩展，天然适合求最短路径
- **DFS**：使用栈（LIFO）或递归，沿路径深入，适合探索所有可能路径

这种建模方式直观、简单，能够清晰展示两种算法的核心差异。

## 实现步骤

### 步骤一：定义迷宫类

```cpp
class Maze {
private:
    vector<vector<int>> grid;
    pair<int, int> start;
    pair<int, int> end;
    int rows, cols;
    vector<pair<int, int>> dirs = {{-1,0}, {1,0}, {0,-1}, {0,1}};
};
```

### 步骤二：实现 BFS 路径搜索

1. 初始化队列，将起点入队
2. 标记起点为已访问
3. 使用 parent 数组记录每个节点的前驱
4. 循环：取出队首节点，扩展四个方向的邻居
5. 如果找到终点，回溯 parent 数组重建路径

### 步骤三：实现 DFS 路径搜索

1. 使用递归或栈进行深度优先搜索
2. 标记访问状态，记录当前路径
3. 如果找到终点，返回成功
4. 否则继续探索邻居，回溯时移除当前节点

### 步骤四：编写主程序

1. 构建示例迷宫
2. 分别调用 BFS 和 DFS
3. 输出路径和统计信息

### 步骤五：对比结果

1. 对比路径长度（BFS 最短，DFS 不一定）
2. 对比搜索节点数（BFS 可能更多，DFS 可能更少）
3. 分析搜索方向差异

## 核心数据结构设计

```cpp
#include <vector>
#include <queue>
#include <stack>
#include <utility>
using namespace std;

class Maze {
private:
    vector<vector<int>> grid;
    pair<int, int> start;
    pair<int, int> end;
    int rows, cols;
    vector<pair<int, int>> dirs = {{-1,0}, {1,0}, {0,-1}, {0,1}};

public:
    Maze(vector<vector<int>> g, pair<int,int> s, pair<int,int> e)
        : grid(g), start(s), end(e) {
        rows = grid.size();
        cols = grid[0].size();
    }

    bool isValid(int r, int c) {
        return r >= 0 && r < rows && c >= 0 && c < cols && grid[r][c] == 0;
    }
};
```

### 字段说明

- `grid`：二维网格，0 表示通路，1 表示墙壁
- `start`：起点坐标 (row, col)
- `end`：终点坐标 (row, col)
- `rows`, `cols`：迷宫行数和列数
- `dirs`：方向数组，上下左右四个方向
- `isValid(r, c)`：检查坐标是否在边界内且为通路

### 搜索数据结构

| 算法 | 主要数据结构 | 辅助数据结构 |
|------|------------|-------------|
| BFS | `queue<pair<int,int>>` | `vector<vector<bool>> visited`, `vector<vector<pair<int,int>>> parent` |
| DFS | `stack<pair<int,int>>` 或递归栈 | `vector<vector<bool>> visited`, `vector<pair<int,int>> path` |

## 核心代码框架或伪代码

### BFS 伪代码

```
function BFS(start, end):
    queue = new Queue()
    visited = new 2D array(false)
    parent = new 2D array(null)
    
    queue.enqueue(start)
    visited[start.r][start.c] = true
    
    while queue is not empty:
        current = queue.dequeue()
        
        if current == end:
            return reconstructPath(parent, end)
        
        for each direction in dirs:
            next_r = current.r + direction.r
            next_c = current.c + direction.c
            
            if isValid(next_r, next_c) and not visited[next_r][next_c]:
                visited[next_r][next_c] = true
                parent[next_r][next_c] = current
                queue.enqueue((next_r, next_c))
    
    return null  // 无路径可达

function reconstructPath(parent, end):
    path = []
    current = end
    
    while current is not null:
        path.push(current)
        current = parent[current.r][current.c]
    
    reverse(path)
    return path
```

### DFS 伪代码（递归）

```
function DFS(current, end, visited, path):
    if current == end:
        path.push(current)
        return true
    
    visited[current.r][current.c] = true
    path.push(current)
    
    for each direction in dirs:
        next_r = current.r + direction.r
        next_c = current.c + direction.c
        
        if isValid(next_r, next_c) and not visited[next_r][next_c]:
            if DFS((next_r, next_c), end, visited, path):
                return true
    
    path.pop()  // 回溯
    return false
```

### DFS 伪代码（迭代）

```
function DFSIterative(start, end):
    stack = new Stack()
    visited = new 2D array(false)
    path = []
    
    stack.push(start)
    
    while stack is not empty:
        current = stack.top()
        
        if current == end:
            path.push(current)
            return path
        
        if not visited[current.r][current.c]:
            visited[current.r][current.c] = true
            path.push(current)
            
            for each direction in reversed(dirs):
                next_r = current.r + direction.r
                next_c = current.c + direction.c
                
                if isValid(next_r, next_c) and not visited[next_r][next_c]:
                    stack.push((next_r, next_c))
        else:
            stack.pop()
            path.pop()  // 回溯
    
    return null
```

## 测试用例

### 测试用例一：3×3 迷宫

**迷宫布局**：
```
0 1 0
0 0 0
1 1 0
```

**起点**：(0, 0)  
**终点**：(2, 2)

**BFS 期望结果**：
- 最短路径长度：4（5个格子）
- 路径：(0,0) → (1,0) → (1,1) → (1,2) → (2,2)

**DFS 期望结果**：
- 路径长度：可能为 4 或更长（取决于搜索顺序）
- 路径：例如 (0,0) → (1,0) → (1,1) → (1,2) → (2,2)

### 测试用例二：5×5 迷宫

**迷宫布局**：
```
0 0 1 0 0
0 1 0 1 0
0 0 0 0 0
1 1 0 1 0
0 0 0 0 0
```

**起点**：(0, 0)  
**终点**：(4, 4)

**BFS 期望结果**：
- 最短路径长度：8
- 路径：(0,0) → (0,1) → ... → (4,4)

**DFS 期望结果**：
- 路径长度：可能更长（如 10 或更多）
- 路径：沿某条分支深入后到达终点

### 测试用例三：无解迷宫

**迷宫布局**：
```
0 0 1 0
0 1 1 0
1 0 0 0
0 0 1 0
```

**起点**：(0, 0)  
**终点**：(3, 3)

**期望结果**：
- BFS 和 DFS 都返回"无路径可达"

## 扩展方向

### 扩展一：可视化输出

用字符或图形显示搜索过程：
- 标记 BFS 扩展过的节点（蓝色）
- 标记 DFS 扩展过的节点（红色）
- 标记最终路径（绿色）

```
BFS 搜索过程：
S . X .
. X X .
X . . E

DFS 搜索过程：
S . . .
. X . .
X X . E
```

### 扩展二：带权路径搜索

增加路径长度限制或权重，使用 Dijkstra 算法扩展：
- 不同类型的格子有不同的权重（如草地、水域、山路）
- 寻找总权重最小的路径

### 扩展三：文件读取和随机生成

- 支持从文件读取迷宫布局
- 支持随机生成迷宫（使用深度优先搜索生成算法）

### 扩展四：算法性能对比

比较 BFS、DFS 和 A* 算法在同一迷宫上的性能差异：
- 路径长度
- 搜索节点数
- 时间复杂度
- 空间复杂度

### 扩展五：多起点多终点

支持多个起点和多个终点，寻找最优路径：
- 从最近的起点出发
- 到达最近的终点
- 考虑时间窗口限制