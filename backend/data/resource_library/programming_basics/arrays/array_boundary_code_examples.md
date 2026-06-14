# 数组边界代码示例

## 正确访问示例
```python
nums = [5, 10, 15, 20]
# 正向遍历
for i in range(len(nums)):
    print(f"索引{i}: {nums[i]}")

# 反向遍历
for i in range(len(nums)-1, -1, -1):
    print(f"索引{i}: {nums[i]}")
```

## 边界检查函数
```python
def safe_get(arr, index):
    if 0 <= index < len(arr):
        return arr[index]
    else:
        return None

print(safe_get(nums, 2))  # 15
print(safe_get(nums, 10)) # None
```

## 循环边界错误示例
```python
# 错误：i <= len(nums) 会越界
for i in range(len(nums) + 1):
    print(nums[i])  # 最后一次 IndexError
```

## 空数组处理
```python
empty = []
if empty:
    print(empty[0])  # 不会执行
else:
    print("数组为空")
```