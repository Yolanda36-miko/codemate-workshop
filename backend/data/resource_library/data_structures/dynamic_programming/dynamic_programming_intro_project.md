# 健身计划生成器

## 项目场景

在健身训练中，用户希望制定一个跑步训练计划。每天可以选择跑 1 公里或 2 公里（也可以选择休息），目标是累计跑完 n 公里。问：有多少种不同的训练方案（方案顺序不同视为不同方案）？

**示例**：跑完 3 公里可以有：
1. 1 + 1 + 1
2. 1 + 2
3. 2 + 1

这个场景本质上就是爬楼梯问题的现实映射，但更贴近生活，便于理解动态规划的实际应用。

## 任务目标

1. **接收用户输入**：目标公里数 n（正整数）
2. **计算方案总数**：使用动态规划计算所有可能的训练方案数量
3. **输出具体方案**：输出其中一种具体方案用于展示
4. **支持两种模式**：
   - 模式一：只输出方案数量
   - 模式二：输出所有方案（适用于小 n）
5. **命令行交互**：提供简单的命令行界面

## 为什么使用该数据结构

### 问题特征分析

训练方案数问题具有以下特征：

| 特征 | 说明 |
|------|------|
| 最优子结构 | 到达 n 公里的方案数 = 到达 n-1 公里的方案数 + 到达 n-2 公里的方案数 |
| 重叠子问题 | 不同路径会重复计算相同子问题 |

### DP 的优势

- **避免重复计算**：使用 DP 数组记录中间结果，时间复杂度 O(n)
- **结构简单**：一维 DP 数组即可，适合初学者理解
- **扩展性强**：可以轻松扩展到每天跑多种距离的情况

## 实现步骤

### 步骤一：定义问题规模

确定目标公里数 n，目标是计算到达第 n 公里的方案数。

### 步骤二：初始化 DP 数组

```
dp[0] = 1  // 已完成 0 公里，只有 1 种方案：不跑
dp[1] = 1  // 跑 1 公里，只有 1 种方案
```

### 步骤三：填充 DP 数组

从 i = 2 到 n，依次计算：

```
dp[i] = dp[i-1] + dp[i-2]
```

### 步骤四：输出方案总数

返回 dp[n] 作为方案总数。

### 步骤五：生成所有方案（扩展）

使用回溯方法，递归生成所有具体方案：

```
generateWays(remaining, current, result):
    if remaining == 0:
        将 current 添加到 result
        return
    if remaining >= 1:
        generateWays(remaining-1, current+"1+", result)
    if remaining >= 2:
        generateWays(remaining-2, current+"2+", result)
```

### 步骤六：命令行交互

```
1. 提示用户输入目标公里数
2. 提示用户选择模式（只输出数量 / 输出所有方案）
3. 调用相应函数并输出结果
```

## 核心数据结构设计

```cpp
#include <iostream>
#include <vector>
#include <string>
using namespace std;

// 计算方案总数
long long countWays(int n) {
    if (n <= 1) return 1;
    vector<long long> dp(n+1);
    dp[0] = 1;
    dp[1] = 1;
    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i-1] + dp[i-2];
    }
    return dp[n];
}

// 生成所有方案（回溯）
void generateWays(int remaining, string current, vector<string>& result) {
    if (remaining == 0) {
        if (!current.empty()) {
            current.pop_back();  // 去掉末尾的 '+'
        }
        result.push_back(current);
        return;
    }
    if (remaining >= 1) {
        generateWays(remaining-1, current + "1+", result);
    }
    if (remaining >= 2) {
        generateWays(remaining-2, current + "2+", result);
    }
}
```

### 数据结构说明

| 数据结构 | 类型 | 说明 |
|----------|------|------|
| dp | vector<long long> | 存储到达每公里的方案数 |
| result | vector<string> | 存储所有具体方案 |
| current | string | 当前正在构建的方案 |

## 核心代码框架或伪代码

### 计算方案总数

```
function countWays(n):
    if n <= 1:
        return 1
    dp = array of size n+1
    dp[0] = 1
    dp[1] = 1
    for i from 2 to n:
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```

### 生成所有方案

```
function generateWays(remaining, current, result):
    if remaining == 0:
        remove trailing '+' from current
        add current to result
        return
    if remaining >= 1:
        generateWays(remaining-1, current + "1+", result)
    if remaining >= 2:
        generateWays(remaining-2, current + "2+", result)
```

### Main 函数

```
function main():
    print("=== 健身计划生成器 ===")
    print("每天可以跑 1 公里或 2 公里")
    print("请输入目标公里数:")
    read n
    print("请选择模式:")
    print("1. 只输出方案数量")
    print("2. 输出所有方案")
    read mode

    ways = countWays(n)
    print("方案总数:", ways)

    if mode == 2:
        print("所有方案:")
        result = empty vector
        generateWays(n, "", result)
        for each plan in result:
            print(plan)
```

## 测试用例

### 测试用例一：n = 1

**输入**：1

**期望输出**：

```
方案总数: 1
方案: ["1"]
```

### 测试用例二：n = 3

**输入**：3

**期望输出**：

```
方案总数: 3
方案: ["1+1+1", "1+2", "2+1"]
```

### 测试用例三：n = 5

**输入**：5

**期望输出**：

```
方案总数: 8
```

### 测试用例四：n = 0

**输入**：0

**期望输出**：

```
方案总数: 1
（或提示"目标公里数必须为正"）
```

## 扩展方向

### 扩展一：每天可跑多种距离

允许用户设置每天的最大公里数（例如每天可跑 1、2 或 3 公里）：

```cpp
long long countWays(int n, int maxStep) {
    vector<long long> dp(n+1);
    dp[0] = 1;
    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= maxStep && j <= i; j++) {
            dp[i] += dp[i-j];
        }
    }
    return dp[n];
}
```

### 扩展二：最小消耗模式

如果每公里有不同消耗值，求达到目标的最小消耗：

```cpp
int minCost(vector<int>& cost, int n) {
    vector<int> dp(n+1);
    dp[0] = cost[0];
    dp[1] = cost[1];
    for (int i = 2; i <= n; i++) {
        dp[i] = min(dp[i-1], dp[i-2]) + cost[i];
    }
    return min(dp[n-1], dp[n]);
}
```

### 扩展三：方案输出优化

避免 n 过大时内存爆炸，只打印前几种方案：

```cpp
void generateWaysLimit(int remaining, string current, vector<string>& result, int limit) {
    if (result.size() >= limit) return;
    if (remaining == 0) {
        if (!current.empty()) current.pop_back();
        result.push_back(current);
        return;
    }
    if (remaining >= 1) {
        generateWaysLimit(remaining-1, current + "1+", result, limit);
    }
    if (remaining >= 2) {
        generateWaysLimit(remaining-2, current + "2+", result, limit);
    }
}
```

### 扩展四：图形化界面

增加进度条或方案树展示：

```
方案总数: 8
进度: [████████████████████████] 100%

方案树:
1
├── 1
│   ├── 1
│   │   ├── 1
│   │   └── 2
│   └── 2
│       └── 1
└── 2
    ├── 1
    │   └── 1
    └── 2
```

### 扩展五：日历结合

将训练计划与日历结合，输出每周训练安排：

```
第1周训练计划:
周一: 跑 2 公里
周二: 跑 1 公里
周三: 休息
周四: 跑 2 公里
周五: 跑 1 公里
周六: 跑 2 公里
周日: 休息
累计: 8 公里
```