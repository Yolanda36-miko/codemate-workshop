# 递归代码示例

## 阶乘函数

```python
def factorial(n):
    """计算 n 的阶乘，n >= 0"""
    # 出口条件
    if n == 0 or n == 1:
        return 1
    # 递推：n! = n * (n-1)!
    return n * factorial(n - 1)

print(factorial(5))   # 输出: 120
print(factorial(0))   # 输出: 1
```

## 斐波那契数列

```python
def fibonacci(n):
    """计算第 n 个斐波那契数（从 0 开始）"""
    # 出口条件
    if n == 0:
        return 0
    elif n == 1:
        return 1
    # 递推：F(n) = F(n-1) + F(n-2)
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(6))   # 输出: 8 (序列: 0,1,1,2,3,5,8)
```

## 打印递归调用过程

```python
def factorial_with_trace(n, depth=0):
    """带调用追踪的阶乘函数"""
    indent = "  " * depth  # 根据递归深度缩进
    print(f"{indent}调用 factorial({n})")
    
    if n == 0 or n == 1:
        print(f"{indent}到达出口，返回 1")
        return 1
    
    result = n * factorial_with_trace(n - 1, depth + 1)
    print(f"{indent}返回 {result}")
    return result

factorial_with_trace(4)
# 输出：
# 调用 factorial(4)
#   调用 factorial(3)
#     调用 factorial(2)
#       调用 factorial(1)
#       到达出口，返回 1
#     返回 2
#   返回 6
# 返回 24
```

## 求和递归

```python
def sum_list(lst):
    """递归求列表元素之和"""
    # 出口条件：空列表
    if not lst:
        return 0
    # 递推：第一个元素 + 剩余元素之和
    return lst[0] + sum_list(lst[1:])

print(sum_list([1, 2, 3, 4]))  # 输出: 10
```

## 反转字符串

```python
def reverse_string(s):
    """递归反转字符串"""
    # 出口条件：空字符串或单字符
    if len(s) <= 1:
        return s
    # 递推：最后一个字符 + 前面部分的反转
    return s[-1] + reverse_string(s[:-1])

print(reverse_string("hello"))  # 输出: "olleh"
```

## 修改递归深度限制

```python
import sys

# 查看当前递归深度限制
print("默认递归深度:", sys.getrecursionlimit())  # 通常是 1000

# 修改递归深度限制（谨慎使用）
sys.setrecursionlimit(2000)

# 测试深度
def deep_recursion(n):
    if n == 0:
        return 0
    return 1 + deep_recursion(n - 1)

try:
    print(deep_recursion(1500))  # 现在可以正常运行
except RecursionError:
    print("递归深度超出限制")
```

## 递归转迭代示例

```python
# 阶乘的迭代版本
def factorial_iterative(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

print(factorial_iterative(5))  # 输出: 120
```