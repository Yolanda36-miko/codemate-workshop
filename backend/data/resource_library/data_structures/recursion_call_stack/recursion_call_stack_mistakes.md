# 递归调用栈易错点总结

## 常见错误

### 错误一：缺少终止条件

缺少终止条件或终止条件永远不会命中，导致无限递归和栈溢出。

### 错误二：递归步没有向终止条件逼近

递归步中的参数没有向终止条件逼近（例如 n 增加而不是减少），导致死循环。

### 错误三：误解回溯过程

在递归调用后没有正确处理返回值，导致结果错误。

### 错误四：忽略递归深度限制

递归深度超过系统栈限制，导致程序崩溃。

### 错误五：混淆栈帧概念

以为所有递归调用共享同一个局部变量。

### 错误六：使用 static 或全局变量导致状态污染

在递归函数中使用 static 局部变量或全局变量，导致多次调用间状态相互影响。

## 错误原因

### 错误一原因

对递归的核心机制理解不足，不知道递归需要"出口"。

### 错误二原因

对递归步的设计原则理解不清，没有认识到每一步都应该向终止条件靠近。

### 错误三原因

对函数调用和返回的机制理解不深，不知道递归调用会返回值。

### 错误四原因

对系统栈的工作原理不了解，不知道栈空间有限。

### 错误五原因

对变量作用域不清晰，不理解每个栈帧都有独立的局部变量。

### 错误六原因

对 static 和全局变量的生命周期理解不清，不知道它们在多次调用间保持状态。

## 正确理解

### 终止条件

递归必须有终止条件，当满足条件时直接返回，不再继续调用。

### 递归步

递归步必须使问题规模缩小，向终止条件逼近。

### 回溯过程

递归调用返回后，调用者获取返回值并继续执行后续代码。

### 栈深度限制

系统栈空间有限（通常几 MB），递归深度不能超过这个限制。

### 栈帧概念

每个递归调用都会创建一个独立的栈帧，包含自己的参数和局部变量。

### 变量作用域

- **局部变量**：每个栈帧独立拥有，互不影响
- **static 变量**：所有调用共享，会保持状态
- **全局变量**：所有调用共享，会保持状态

## 错误例子

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

### 错误三：误解回溯过程

**错误代码**：

```cpp
int factorial(int n) {
    if (n == 0) return 1;
    factorial(n-1);  // 忘记使用返回值！
    return n;
}
```

**错误后果**：无论 n 多大，都返回 n，结果错误。

### 错误四：忽略递归深度限制

**错误场景**：计算 `factorial(100000)`。

**错误后果**：递归深度为 100000，超过系统栈限制，程序崩溃。

### 错误五：混淆栈帧概念

**错误代码**：

```cpp
void printNumbers(int n) {
    if (n == 0) return;
    int x = n;  // 每个调用都有自己的 x
    printNumbers(n-1);
    cout << x << " ";  // 期望输出：1 2 3 4
}
```

**错误理解**：以为所有调用共享同一个 x，认为输出会是 4 4 4 4。

**实际输出**：1 2 3 4（每个栈帧有独立的 x）。

### 错误六：使用 static 变量导致状态污染

**错误代码**：

```cpp
int factorial(int n) {
    static int calls = 0;  // static 变量，所有调用共享
    calls++;
    cout << "调用次数: " << calls << endl;
    if (n == 0) return 1;
    return n * factorial(n-1);
}

int main() {
    cout << factorial(3) << endl;  // calls = 4
    cout << factorial(2) << endl;  // calls = 7（继续累加！）
    return 0;
}
```

**错误后果**：第二次调用时，calls 不会重置，导致结果错误。

## 正确做法

### 错误一正确做法

```cpp
int factorial(int n) {
    if (n == 0) return 1;  // 添加终止条件
    return n * factorial(n-1);
}
```

### 错误二正确做法

```cpp
int factorial(int n) {
    if (n == 0) return 1;
    return n * factorial(n-1);  // n 减少，向终止条件逼近
}
```

### 错误三正确做法

```cpp
int factorial(int n) {
    if (n == 0) return 1;
    int subResult = factorial(n-1);  // 使用返回值
    return n * subResult;
}
```

### 错误四正确做法

```cpp
// 使用迭代版本避免栈溢出
int factorialIterative(int n) {
    int result = 1;
    for (int i = 1; i <= n; i++) {
        result *= i;
    }
    return result;
}
```

### 错误五正确做法

理解每个栈帧有独立的局部变量，这是递归的正常行为。

### 错误六正确做法

```cpp
int factorial(int n, int& calls) {
    calls++;
    if (n == 0) return 1;
    return n * factorial(n-1, calls);
}

int main() {
    int calls1 = 0;
    cout << factorial(3, calls1) << ", 调用次数: " << calls1 << endl;
    
    int calls2 = 0;
    cout << factorial(2, calls2) << ", 调用次数: " << calls2 << endl;
    return 0;
}
```

### 错误与正确对比

| 错误类型 | 错误代码 | 正确代码 |
|----------|----------|----------|
| 缺少终止条件 | 无 if (n == 0) | 添加终止条件 |
| 递归步不逼近 | factorial(n+1) | factorial(n-1) |
| 忘记返回值 | factorial(n-1); return n | 使用返回值计算 |
| 递归深度过大 | 直接递归 | 使用迭代 |
| 混淆栈帧 | 认为共享变量 | 理解独立栈帧 |
| static 变量污染 | static int calls | 使用参数传递 |

## 自查题

### 题目一

**题目描述**：指出以下斐波那契函数的错误并修正。

```cpp
int fib(int n) {
    return fib(n-1) + fib(n-2);
}
```

**答案要点**：

**错误**：缺少终止条件，会无限递归导致栈溢出。

**修正代码**：

```cpp
int fib(int n) {
    if (n == 0) return 0;
    if (n == 1) return 1;
    return fib(n-1) + fib(n-2);
}
```

### 题目二

**题目描述**：指出以下代码的问题并修正。

```cpp
int sum(int n) {
    static int total = 0;
    if (n == 0) return total;
    total += n;
    return sum(n-1);
}

int main() {
    cout << sum(3) << endl;  // 期望输出：6
    cout << sum(2) << endl;  // 期望输出：3，但实际输出？
    return 0;
}
```

**答案要点**：

**问题**：`static int total` 在两次调用间保持状态，第二次调用时 total 不会重置。

**第一次调用 sum(3)**：total = 3+2+1 = 6，返回 6

**第二次调用 sum(2)**：total = 6+2+1 = 9，返回 9（错误）

**修正代码**：

```cpp
int sum(int n) {
    if (n == 0) return 0;
    return n + sum(n-1);
}
```

### 题目三

**题目描述**：分析以下说法是否正确："递归的空间复杂度总是 O(1)，因为只用了一个函数。"

**答案要点**：

**错误**。

**理由**：

1. 虽然代码中只定义了一个函数，但每次递归调用都会在系统栈上创建一个**独立的栈帧**。
2. 每个栈帧包含参数、返回地址和局部变量，占用 O(1) 的空间。
3. 如果递归深度为 n，那么栈空间的总开销为 O(n)。
4. 因此，递归的空间复杂度是 O(n)，不是 O(1)。

**对比**：

| 方法 | 空间复杂度 | 原因 |
|------|----------|------|
| 递归 | O(n) | n 个栈帧 |
| 迭代 | O(1) | 只用常数个变量 |