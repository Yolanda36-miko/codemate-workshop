# 递归调用栈代码示例

## 代码目标

本代码通过阶乘函数 `factorial(n)` 演示递归调用过程中栈帧的变化。代码包含一个辅助输出函数，在每次递归调用时打印当前函数名、参数值和当前栈深度（用缩进表示），直观展示压栈和回溯过程。

## 核心代码

```cpp
#include <iostream>
#include <string>
using namespace std;

// 辅助函数：输出缩进，表示递归深度
void printIndent(int depth) {
    for (int i = 0; i < depth; i++) {
        cout << "  ";
    }
}

// 递归阶乘函数，depth 表示当前递归深度
int factorial(int n, int depth) {
    // 打印当前调用信息（压栈阶段）
    printIndent(depth);
    cout << "factorial(" << n << ") called, depth = " << depth << endl;

    // 终止条件
    if (n == 0) {
        // 打印返回值（回溯阶段）
        printIndent(depth);
        cout << "factorial(" << n << ") returns 1" << endl;
        return 1;
    }

    // 递归调用，深度加 1
    int result = n * factorial(n - 1, depth + 1);

    // 打印返回值（回溯阶段）
    printIndent(depth);
    cout << "factorial(" << n << ") returns " << result << endl;

    return result;
}

int main() {
    cout << "=== 递归调用栈演示 ===" << endl;
    cout << "计算 factorial(4) 的过程：" << endl << endl;

    int result = factorial(4, 0);

    cout << endl << "最终结果：factorial(4) = " << result << endl;

    return 0;
}
```

## 关键步骤解释

### 递归调用前打印状态

```cpp
printIndent(depth);
cout << "factorial(" << n << ") called, depth = " << depth << endl;
```

**解释**：在每次递归调用开始时打印，展示"压栈"阶段。`depth` 参数表示当前递归深度，用于输出缩进。

### 递归调用后打印返回值

```cpp
int result = n * factorial(n - 1, depth + 1);
printIndent(depth);
cout << "factorial(" << n << ") returns " << result << endl;
```

**解释**：在递归调用返回后打印，展示"回溯"阶段。只有当子调用完成后才会执行这部分代码。

### 缩进表示递归深度

```cpp
void printIndent(int depth) {
    for (int i = 0; i < depth; i++) {
        cout << "  ";
    }
}
```

**解释**：每增加一层递归，输出两个空格，形成直观的缩进效果，展示调用栈的深度。

### 终止条件的作用

```cpp
if (n == 0) {
    printIndent(depth);
    cout << "factorial(" << n << ") returns 1" << endl;
    return 1;
}
```

**解释**：终止条件是递归的"出口"，当 `n == 0` 时直接返回 1，不再继续递归调用，开始回溯过程。

## 输入输出示例

运行上述代码，输出结果为：

```
=== 递归调用栈演示 ===
计算 factorial(4) 的过程：

factorial(4) called, depth = 0      ← 压栈：第一层
  factorial(3) called, depth = 1    ← 压栈：第二层
    factorial(2) called, depth = 2  ← 压栈：第三层
      factorial(1) called, depth = 3← 压栈：第四层
        factorial(0) called, depth = 4← 压栈：第五层（命中终止条件）
        factorial(0) returns 1      ← 回溯：第五层返回
      factorial(1) returns 1        ← 回溯：第四层返回
    factorial(2) returns 2          ← 回溯：第三层返回
  factorial(3) returns 6            ← 回溯：第二层返回
factorial(4) returns 24             ← 回溯：第一层返回

最终结果：factorial(4) = 24
```

### 输出分析

| 输出行 | 阶段 | 栈状态 |
|--------|------|--------|
| `factorial(4) called` | 压栈 | [factorial(4)] |
| `factorial(3) called` | 压栈 | [factorial(4), factorial(3)] |
| `factorial(2) called` | 压栈 | [factorial(4), factorial(3), factorial(2)] |
| `factorial(1) called` | 压栈 | [factorial(4), factorial(3), factorial(2), factorial(1)] |
| `factorial(0) called` | 压栈（终止） | [factorial(4), factorial(3), factorial(2), factorial(1), factorial(0)] |
| `factorial(0) returns 1` | 回溯 | [factorial(4), factorial(3), factorial(2), factorial(1)] |
| `factorial(1) returns 1` | 回溯 | [factorial(4), factorial(3), factorial(2)] |
| `factorial(2) returns 2` | 回溯 | [factorial(4), factorial(3)] |
| `factorial(3) returns 6` | 回溯 | [factorial(4)] |
| `factorial(4) returns 24` | 回溯 | [] |

## 边界条件

### n == 0

直接返回 1，是递归的终止条件，不再继续递归调用。

### n == 1

只进行一次递归调用（`factorial(1)` → `factorial(0)`），然后回溯。

### n 为负数

当前代码会无限递归导致栈溢出。可以添加负数处理：

```cpp
int factorial(int n, int depth) {
    if (n < 0) {
        printIndent(depth);
        cout << "错误：n 不能为负数！" << endl;
        return -1;
    }
    // ...
}
```

## 时间复杂度和空间复杂度

### 时间复杂度

**O(n)**：递归调用 n+1 次（factorial(n) 到 factorial(0)），每次调用的时间为 O(1)。

### 空间复杂度

**O(n)**：递归调用栈的最大深度为 n+1，每个栈帧占用 O(1) 的空间。

### 为什么空间复杂度不是 O(1)

虽然没有显式使用数组或其他数据结构，但递归调用会在系统栈上创建栈帧，每个栈帧存储参数、返回地址和局部变量，因此空间复杂度为 O(n)。

## 改写练习

### 练习一：记录最大栈深度

```cpp
int maxDepth = 0;

int factorial(int n, int depth) {
    if (depth > maxDepth) maxDepth = depth;
    
    printIndent(depth);
    cout << "factorial(" << n << ") called, depth = " << depth << endl;

    if (n == 0) {
        printIndent(depth);
        cout << "factorial(" << n << ") returns 1" << endl;
        return 1;
    }

    int result = n * factorial(n - 1, depth + 1);

    printIndent(depth);
    cout << "factorial(" << n << ") returns " << result << endl;

    return result;
}

int main() {
    int result = factorial(4, 0);
    cout << "最大栈深度: " << maxDepth << endl;
    return 0;
}
```

### 练习二：迭代版本

```cpp
int factorialIterative(int n) {
    if (n < 0) return -1;
    
    int result = 1;
    cout << "迭代计算过程:" << endl;
    for (int i = 1; i <= n; i++) {
        result *= i;
        cout << "  i=" << i << ", result=" << result << endl;
    }
    return result;
}
```

**对比**：迭代版本的空间复杂度为 O(1)，不需要递归调用栈。

### 练习三：斐波那契数列

```cpp
int fib(int n, int depth) {
    printIndent(depth);
    cout << "fib(" << n << ") called, depth = " << depth << endl;

    if (n == 0) {
        printIndent(depth);
        cout << "fib(" << n << ") returns 0" << endl;
        return 0;
    }
    if (n == 1) {
        printIndent(depth);
        cout << "fib(" << n << ") returns 1" << endl;
        return 1;
    }

    int result = fib(n - 1, depth + 1) + fib(n - 2, depth + 1);

    printIndent(depth);
    cout << "fib(" << n << ") returns " << result << endl;

    return result;
}

int main() {
    fib(4, 0);
    return 0;
}
```

**分析**：斐波那契数列的调用树是指数级的，`fib(2)` 会被重复计算多次，展示纯递归的低效性。