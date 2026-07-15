# 动态规划入门代码示例

## 代码目标

本代码演示使用动态规划解决"爬楼梯"问题。通过三种实现方式对比，展示动态规划如何避免重复计算：

1. **递归 + 记忆化**：使用 memo 数组存储已计算结果
2. **迭代 DP**：使用 dp 数组自底向上填充
3. **空间优化**：只使用两个变量，O(1) 空间复杂度

## 核心代码

```cpp
#include <iostream>
#include <vector>
using namespace std;

// 递归 + 记忆化
int climbStairsRecursive(int n, vector<int>& memo) {
    if (n <= 1) return 1;
    if (memo[n] != -1) return memo[n];
    memo[n] = climbStairsRecursive(n-1, memo) + climbStairsRecursive(n-2, memo);
    return memo[n];
}

// 迭代 DP 数组
int climbStairsDP(int n) {
    if (n <= 1) return 1;
    vector<int> dp(n+1);
    dp[0] = 1;
    dp[1] = 1;
    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i-1] + dp[i-2];
    }
    return dp[n];
}

// 空间优化（滚动变量）
int climbStairsOptimized(int n) {
    if (n <= 1) return 1;
    int prev2 = 1;
    int prev1 = 1;
    int curr;
    for (int i = 2; i <= n; i++) {
        curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    return curr;
}

int main() {
    cout << "=== 爬楼梯问题 ===" << endl;
    cout << "每次可走 1 阶或 2 阶，求到达第 n 阶的方法数" << endl << endl;

    for (int n = 1; n <= 10; n++) {
        vector<int> memo1(n+1, -1);
        int res1 = climbStairsRecursive(n, memo1);
        int res2 = climbStairsDP(n);
        int res3 = climbStairsOptimized(n);

        cout << "n=" << n << ": ";
        cout << "递归记忆化=" << res1 << ", ";
        cout << "迭代DP=" << res2 << ", ";
        cout << "空间优化=" << res3 << endl;
    }

    return 0;
}
```

## 关键步骤解释

### 递归 + 记忆化

```cpp
int climbStairsRecursive(int n, vector<int>& memo) {
    if (n <= 1) return 1;
    if (memo[n] != -1) return memo[n];  // 已计算，直接返回
    memo[n] = climbStairsRecursive(n-1, memo) + climbStairsRecursive(n-2, memo);
    return memo[n];
}
```

**关键点**：
- `memo[n] != -1` 判断是否已计算过
- 如果已计算，直接返回结果，避免重复计算
- 未计算则递归求解，并保存结果到 memo

### 迭代 DP 数组

```cpp
int climbStairsDP(int n) {
    if (n <= 1) return 1;
    vector<int> dp(n+1);
    dp[0] = 1;
    dp[1] = 1;
    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i-1] + dp[i-2];
    }
    return dp[n];
}
```

**关键点**：
- 自底向上计算，从 i=2 开始
- 每个 dp[i] 依赖 dp[i-1] 和 dp[i-2]
- 时间复杂度 O(n)，空间复杂度 O(n)

### 空间优化

```cpp
int climbStairsOptimized(int n) {
    if (n <= 1) return 1;
    int prev2 = 1;  // dp[i-2]
    int prev1 = 1;  // dp[i-1]
    int curr;       // dp[i]
    for (int i = 2; i <= n; i++) {
        curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    return curr;
}
```

**关键点**：
- 只使用三个变量，空间复杂度 O(1)
- `prev2` 保存 dp[i-2]，`prev1` 保存 dp[i-1]
- 每次循环更新这两个变量，实现滚动计算

### 复杂度对比

| 方法 | 时间复杂度 | 空间复杂度 |
|------|----------|----------|
| 递归（无记忆化） | O(2^n) | O(n) |
| 递归 + 记忆化 | O(n) | O(n) |
| 迭代 DP 数组 | O(n) | O(n) |
| 空间优化 | O(n) | O(1) |

## 输入输出示例

运行上述代码，输出结果为：

```
=== 爬楼梯问题 ===
每次可走 1 阶或 2 阶，求到达第 n 阶的方法数

n=1: 递归记忆化=1, 迭代DP=1, 空间优化=1
n=2: 递归记忆化=2, 迭代DP=2, 空间优化=2
n=3: 递归记忆化=3, 迭代DP=3, 空间优化=3
n=4: 递归记忆化=5, 迭代DP=5, 空间优化=5
n=5: 递归记忆化=8, 迭代DP=8, 空间优化=8
n=6: 递归记忆化=13, 迭代DP=13, 空间优化=13
n=7: 递归记忆化=21, 迭代DP=21, 空间优化=21
n=8: 递归记忆化=34, 迭代DP=34, 空间优化=34
n=9: 递归记忆化=55, 迭代DP=55, 空间优化=55
n=10: 递归记忆化=89, 迭代DP=89, 空间优化=89
```

## 边界条件

### n=0

根据定义 dp[0]=1，表示从地面到第 0 阶有 1 种方式。如果题目要求 n≥1，则可返回 0 或抛出异常。

### n=1

直接返回初始值 1，循环不执行。

### n=2

循环执行一次：`dp[2] = dp[1] + dp[0] = 1 + 1 = 2`。

### 大 n

对于较大的 n（如 n=50），结果会超出 int 的范围，需要使用 `long long`：

```cpp
long long climbStairsLL(int n) {
    if (n <= 1) return 1;
    long long prev2 = 1, prev1 = 1, curr;
    for (int i = 2; i <= n; i++) {
        curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    return curr;
}
```

## 时间复杂度和空间复杂度

### 递归 + 记忆化

- **时间复杂度**：O(n)，每个子问题只计算一次
- **空间复杂度**：O(n)，递归调用栈深度 + memo 数组

### 迭代 DP 数组

- **时间复杂度**：O(n)，循环 n-1 次
- **空间复杂度**：O(n)，dp 数组大小为 n+1

### 空间优化

- **时间复杂度**：O(n)，循环 n-1 次
- **空间复杂度**：O(1)，只使用常数个变量

### DP 比纯递归高效的原因

纯递归（无记忆化）的时间复杂度是 O(2^n)，因为每个子问题会被重复计算多次。动态规划通过存储子问题的解，使得每个子问题只计算一次，时间复杂度降为 O(n)。

## 改写练习

### 练习一：每次可走 1、2、3 阶

修改状态转移方程：`dp[i] = dp[i-1] + dp[i-2] + dp[i-3]`

```cpp
int climbStairs3(int n) {
    if (n <= 1) return 1;
    if (n == 2) return 2;
    int prev3 = 1, prev2 = 1, prev1 = 2, curr;
    for (int i = 3; i <= n; i++) {
        curr = prev1 + prev2 + prev3;
        prev3 = prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    return curr;
}
```

### 练习二：支持更大的 n

使用 `long long` 类型：

```cpp
long long climbStairsLL(int n) {
    if (n <= 1) return 1;
    long long prev2 = 1, prev1 = 1, curr;
    for (int i = 2; i <= n; i++) {
        curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    return curr;
}

// n=50 的结果：20365011074
```

### 练习三：输出到达每一阶的方法数

```cpp
void printAllSteps(int n) {
    vector<int> dp(n+1);
    dp[0] = 1;
    dp[1] = 1;
    cout << "到达第 0 阶的方法数：" << dp[0] << endl;
    cout << "到达第 1 阶的方法数：" << dp[1] << endl;
    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i-1] + dp[i-2];
        cout << "到达第 " << i << " 阶的方法数：" << dp[i] << endl;
    }
}
```