# 函数调用代码示例与注释

## 基础函数定义与调用
```python
def greet(name):
    """打印问候语"""
    print(f"Hello, {name}!")

greet("Alice")  # 输出: Hello, Alice!
```

## 带返回值的函数
```python
def add(a, b):
    return a + b

result = add(10, 5)
print(result)  # 输出: 15
```

## 参数传递：不可变对象 vs 可变对象
```python
# 不可变对象（int, str）在函数内修改不影响外部
def try_change_num(n):
    n = n + 10
    print("函数内:", n)

x = 5
try_change_num(x)  # 函数内: 15
print("函数外:", x)  # 输出: 5

# 可变对象（list）在函数内修改会影响外部
def add_element(lst):
    lst.append("new")
    print("函数内:", lst)

my_list = [1, 2]
add_element(my_list)  # 函数内: [1, 2, 'new']
print("函数外:", my_list)  # 输出: [1, 2, 'new']
```

## 默认参数与关键字参数
```python
def describe_pet(name, animal_type="dog"):
    print(f"I have a {animal_type} named {name}.")

describe_pet("Buddy")                # 使用默认类型
describe_pet("Whiskers", "cat")      # 位置参数
describe_pet(animal_type="hamster", name="Nibbles")  # 关键字参数
```

## 注意事项
- 函数内部修改全局变量需要使用 `global` 关键字（一般不推荐）
- 默认参数不要使用可变对象（如 `def f(lst=[])` 会导致共享状态）