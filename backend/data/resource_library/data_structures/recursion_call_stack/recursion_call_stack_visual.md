# 递归调用栈图解讲解

## 核心概念

### 什么是递归调用栈

递归函数在调用自身时，每次调用都会在系统栈（调用栈）上分配一个**栈帧**（stack frame），存储局部变量、返回地址和参数。

### 栈帧的组成

| 组成部分 | 说明 |
|----------|------|
| 函数参数 | 传递给函数的参数值 |
| 返回地址 | 调用者继续执行的位置 |
| 局部变量 | 函数内部定义的变量 |
| 保存的寄存器状态 | 调用前的寄存器值，用于恢复 |

### 递归调用流程

```
函数调用 → 压栈 → 执行子调用 → 继续压栈 → 命中终止条件 → 开始回溯 → 逐层返回并出栈
```

### 递归的两个要素

1. **终止条件（base case）**：停止递归的条件，直接返回结果
2. **递归步（recursive step）**：将问题分解为更小的子问题，向终止条件逼近

## 过程拆解

以阶乘函数 `factorial(n)` 为例，计算 `factorial(4)`：

```cpp
int factorial(int n) {
    if (n == 0) return 1;  // 终止条件
    return n * factorial(n-1);  // 递归步
}
```

### 步骤一到步骤五：压栈阶段

- **步骤1**：调用 `factorial(4)`，将帧压入栈，继续调用 `factorial(3)`
- **步骤2**：调用 `factorial(3)`，压栈，继续调用 `factorial(2)`
- **步骤3**：调用 `factorial(2)`，压栈，继续调用 `factorial(1)`
- **步骤4**：调用 `factorial(1)`，压栈，继续调用 `factorial(0)`
- **步骤5**：调用 `factorial(0)`，命中终止条件（n==0），返回 1

### 步骤六到步骤十：回溯阶段

- **步骤6**：`factorial(0)` 出栈，将结果返回给 `factorial(1)`
- **步骤7**：`factorial(1)` 计算 1*1=1，返回给 `factorial(2)`，出栈
- **步骤8**：`factorial(2)` 计算 2*1=2，返回给 `factorial(3)`，出栈
- **步骤9**：`factorial(3)` 计算 3*2=6，返回给 `factorial(4)`，出栈
- **步骤10**：`factorial(4)` 计算 4*6=24，返回最终结果，出栈

## 文字版图示与状态变化表

### factorial(4) 的调用栈变化

| 步骤 | 操作 | 当前栈帧 | 栈状态（从栈底到栈顶） | 返回值待定 |
|------|------|----------|------------------------|------------|
| 0 | 初始状态 | - | [] | - |
| 1 | 调用 factorial(4) | factorial(4): n=4 | [factorial(4)] | 4 * ? |
| 2 | 调用 factorial(3) | factorial(3): n=3 | [factorial(4), factorial(3)] | 3 * ? |
| 3 | 调用 factorial(2) | factorial(2): n=2 | [factorial(4), factorial(3), factorial(2)] | 2 * ? |
| 4 | 调用 factorial(1) | factorial(1): n=1 | [factorial(4), factorial(3), factorial(2), factorial(1)] | 1 * ? |
| 5 | 调用 factorial(0) | factorial(0): n=0 | [factorial(4), factorial(3), factorial(2), factorial(1), factorial(0)] | 命中终止条件！ |
| 6 | 返回 1 | factorial(0) 返回 | [factorial(4), factorial(3), factorial(2), factorial(1)] | 1 * 1 = 1 |
| 7 | 返回 1 | factorial(1) 返回 | [factorial(4), factorial(3), factorial(2)] | 2 * 1 = 2 |
| 8 | 返回 2 | factorial(2) 返回 | [factorial(4), factorial(3)] | 3 * 2 = 6 |
| 9 | 返回 6 | factorial(3) 返回 | [factorial(4)] | 4 * 6 = 24 |
| 10 | 返回 24 | factorial(4) 返回 | [] | 最终结果：24 |

### 栈状态变化示意图

```
步骤1-5（压栈阶段）:

栈底 ──────────────
      factorial(4)  ← 步骤1
      factorial(3)  ← 步骤2
      factorial(2)  ← 步骤3
      factorial(1)  ← 步骤4
栈顶   factorial(0)  ← 步骤5（命中终止条件）

步骤6-10（回溯阶段）:

栈底 ──────────────
      factorial(4)
      factorial(3)
      factorial(2)
栈顶   factorial(1)  ← 步骤6：等待 factorial(0) 返回

栈底 ──────────────
      factorial(4)
      factorial(3)
栈顶   factorial(2)  ← 步骤7：等待 factorial(1) 返回

栈底 ──────────────
      factorial(4)
栈顶   factorial(3)  ← 步骤8：等待 factorial(2) 返回

栈底 ──────────────
栈顶   factorial(4)  ← 步骤9：等待 factorial(3) 返回

栈底 ──────────────
栈顶 （空）          ← 步骤10：返回最终结果 24
```

## 小规模具体例子

### factorial(3) 的计算过程

```
factorial(3) = 3 * factorial(2)
factorial(2) = 2 * factorial(1)
factorial(1) = 1 * factorial(0)
factorial(0) = 1  （终止条件）
```

### 逐层回溯计算

```
factorial(0) = 1
factorial(1) = 1 * factorial(0) = 1 * 1 = 1
factorial(2) = 2 * factorial(1) = 2 * 1 = 2
factorial(3) = 3 * factorial(2) = 3 * 2 = 6
```

### 每一层的局部变量

| 层级 | 函数调用 | 局部变量 n 的值 | 计算过程 | 返回值 |
|------|----------|----------------|----------|--------|
| 第4层 | factorial(0) | n = 0 | 直接返回 | 1 |
| 第3层 | factorial(1) | n = 1 | 1 * 1 | 1 |
| 第2层 | factorial(2) | n = 2 | 2 * 1 | 2 |
| 第1层 | factorial(3) | n = 3 | 3 * 2 | 6 |

## 易错提醒

### 错误一：缺少终止条件

**错误代码**：

```cpp
int factorial(int n) {
    return n * factorial(n-1);  // 没有终止条件！
}
```

**错误后果**：无限递归，栈溢出（Stack Overflow）。

### 错误二：递归步没有向终止条件逼近

**错误代码**：

```cpp
int factorial(int n) {
    if (n == 0) return 1;
    return n * factorial(n+1);  // n 增加而不是减少！
}
```

**错误后果**：n 越来越大，永远不会命中终止条件，栈溢出。

### 错误三：递归深度过大

**错误场景**：计算 `factorial(10000)`，递归深度为 10000。

**错误后果**：系统栈空间有限（通常只有几 MB），递归深度过大导致栈溢出。

### 错误四：误解回溯过程

**错误理解**：返回值是"弹回"到调用者。

**正确理解**：调用者从递归调用中获取返回值，然后继续执行后续代码。

### 错误五：混淆栈帧和栈空间

**错误理解**：所有递归调用共享同一个变量 n。

**正确理解**：每个栈帧都有自己独立的变量，n 在不同帧中可以有不同的值。

## 小练习

### 练习题目

给出斐波那契数列 `fib(n)`（n=4）：

```
fib(0) = 0
fib(1) = 1
fib(n) = fib(n-1) + fib(n-2)
```

### 问题一

画出 `fib(4)` 的递归调用树，标注每个节点的返回值。

### 问题二

回答：当计算 `fib(4)` 时，`fib(2)` 会被重复计算多少次？这说明了什么问题？

### 答案要点

**问题一：递归调用树**

```
          fib(4)
         /      \
    fib(3)      fib(2) ← 第1次计算 fib(2)
    /   \        /   \
 fib(2) fib(1) fib(1) fib(0)
 /  \
fib(1) fib(0)
```

**返回值标注**：

```
          fib(4) = 3
         /         \
    fib(3) = 2    fib(2) = 1
    /   \          /   \
 fib(2)=1 fib(1)=1 fib(1)=1 fib(0)=0
 /  \
fib(1)=1 fib(0)=0
```

**问题二：重复计算次数**

`fib(2)` 被计算了 **2 次**：
1. 从 `fib(4)` 的右子树直接调用
2. 从 `fib(3)` 的左子树调用

**说明的问题**：

纯递归存在**大量重复计算**问题，这正是引入**动态规划**的动机。通过记忆化存储已计算的结果，可以避免重复计算，将时间复杂度从 O(2^n) 降低到 O(n)。

### 验证方法

你可以手动枚举所有调用：

```
fib(4) 调用 fib(3) 和 fib(2)
fib(3) 调用 fib(2) 和 fib(1)
fib(2) 调用 fib(1) 和 fib(0)
fib(1) 返回 1
fib(0) 返回 0
```

统计 `fib(2)` 的调用次数：从 `fib(4)` 和 `fib(3)` 各调用一次，共 2 次。