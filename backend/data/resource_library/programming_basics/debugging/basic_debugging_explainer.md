# 基础调试技巧

## 适用对象
正在学习编程，遇到错误不知道如何定位和解决的初学者。

## 学习目标
- 理解编程中的三种主要错误类型
- 学会阅读和理解错误信息
- 掌握使用 print 语句进行调试
- 培养断点思维和系统性排查能力

## 核心概念

### 错误的三种类型

**1. 语法错误（SyntaxError）**
- 代码不符合编程语言的语法规则
- 在代码执行前就会被发现
- 示例：缺少冒号、引号不匹配、缩进错误

**2. 运行时错误（RuntimeError）**
- 代码语法正确，但运行时出现问题
- 示例：除零错误、索引越界、类型错误

**3. 逻辑错误（Logical Error）**
- 代码能运行，但输出结果不正确
- 最难发现和调试的错误类型

### 阅读错误信息

Python 的错误信息包含三个关键部分：
1. **错误类型**：如 `SyntaxError`、`IndexError`、`ZeroDivisionError`
2. **错误位置**：显示错误发生的文件名和行号
3. **错误描述**：说明错误的具体原因

### Print 调试法

在关键位置添加 print 语句，输出变量的值来追踪程序执行流程：

```python
def calculate_average(numbers):
    print("输入的列表:", numbers)  # 检查输入
    total = 0
    for i, num in enumerate(numbers):
        total += num
        print(f"第 {i} 次循环: num={num}, total={total}")
    average = total / len(numbers)
    print("计算结果:", average)
    return average
```

### 断点思维

断点思维是指在脑海中或实际调试工具中设置检查点，验证程序在特定位置的状态是否符合预期。

## 常见错误

### 语法错误示例
```python
# 错误：缺少冒号
if x > 5
    print("x 大于 5")

# 错误：缩进不一致
def func():
print("hello")  # 没有缩进

# 错误：引号不匹配
print('Hello")  # 单引号和双引号混合
```

### 运行时错误示例
```python
# 除零错误
result = 10 / 0  # ZeroDivisionError

# 索引越界
arr = [1, 2, 3]
print(arr[3])  # IndexError

# 类型错误
print("Hello" + 123)  # TypeError
```

### 逻辑错误示例
```python
# 计算平均数时忘记除以数量
def average(numbers):
    total = sum(numbers)
    return total  # 应该是 total / len(numbers)

# 循环条件错误导致少执行一次
for i in range(1, 10):  # 如果想要 1-10，应该是 range(1, 11)
    print(i)
```

## 自我检查
1. 三种错误类型有什么区别？
2. 如何快速定位错误发生的位置？
3. print 调试法的优缺点是什么？
4. 如何判断错误是语法错误还是逻辑错误？

## 下一步建议
学习使用 IDE 的调试工具（如 PyCharm、VS Code），了解断点设置和变量监视功能。