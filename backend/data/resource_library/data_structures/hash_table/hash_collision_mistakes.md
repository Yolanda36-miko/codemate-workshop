# 散列表与哈希冲突易错点总结

## 常见错误

### 错误一：认为哈希查找总是 O(1)

忽略了冲突和负载因子的影响，以为无论什么情况查找都是常数时间。

### 错误二：哈希函数设计不合理

使用对输入不敏感、分布不均匀的哈希函数，导致大量冲突，性能退化。

### 错误三：负载因子过高时不扩容

当负载因子超过阈值（如 0.75）时不进行 rehash，导致链表变长，查找性能急剧下降。

### 错误四：链地址法删除节点时内存泄漏或指针更新错误

删除节点时忘记释放内存，或删除头节点时没有正确更新桶的指针。

### 错误五：开放地址法删除时未正确处理墓碑标记

删除元素后直接标记为空，导致后续查找失败；或使用墓碑但查找逻辑不正确。

### 错误六：错误理解哈希函数的确定性

以为"哈希函数是加密的，不可逆"或"哈希值每次都不同"。

## 错误原因

### 错误一原因

对哈希表的性能分析理解片面，只记住了平均情况，忽略了最坏情况和影响因素。

### 错误二原因

对哈希函数的设计原则理解不足，不知道好的哈希函数需要满足均匀分布、对输入敏感等特性。

### 错误三原因

对负载因子与性能的关系不清晰，不知道随着元素增多，冲突概率会指数级上升。

### 错误四原因

对内存管理不熟悉，或对链表操作的边界情况考虑不周全。

### 错误五原因

对开放地址法的删除机制理解不深，不知道"软删除"（墓碑标记）的必要性和正确实现方式。

### 错误六原因

将哈希函数与加密函数混淆，不理解哈希函数的核心特性是确定性（同一输入总是产生同一输出）。

## 正确理解

### 哈希表的时间复杂度

- **平均情况**：O(1)，当哈希函数均匀分布时
- **最坏情况**：O(n)，当所有元素都映射到同一个桶时
- **影响因素**：负载因子、哈希函数质量、冲突处理方式

### 好的哈希函数特性

- **确定性**：同一输入总是产生同一输出
- **均匀分布**：不同输入尽可能映射到不同位置
- **对输入敏感**：输入微小变化产生显著不同的哈希值

### 负载因子与扩容

- 负载因子 α = n / m，其中 n 是元素个数，m 是桶的大小
- 当 α > 0.75 时，冲突概率显著增加，需要扩容（rehash）
- 扩容通常将桶的大小翻倍，并重新哈希所有元素

### 链地址法删除

- 需要释放被删除节点的内存
- 删除头节点时需要更新桶的指针
- 删除中间或尾部节点时需要更新前一个节点的 next 指针

### 开放地址法删除

- 不能直接标记为空，否则会中断查找链
- 需要使用"墓碑"（tombstone）标记，表示该位置曾经有元素但已被删除
- 查找时需要跳过墓碑继续查找

### 哈希函数的确定性

哈希函数是**确定性映射**，不是加密函数：
- 同一输入总是产生相同的哈希值
- 不同输入可能产生相同的哈希值（冲突）
- 不需要保密，只需要均匀分布

## 错误例子

### 错误一：认为哈希查找总是 O(1)

**错误理解**：以为无论什么情况，哈希查找都是 O(1)。

**错误场景**：当所有元素都映射到同一个桶时：

```cpp
// 极端情况：所有 key 的哈希值都相同
int badHash(int key) {
    return 0;  // 所有元素都映射到 index 0
}
```

**错误后果**：哈希表退化为链表，查找时间从 O(1) 变为 O(n)。

### 错误二：哈希函数设计不合理

**错误代码**：

```cpp
int badHash(int key) {
    return key % 2;  // 只有 0 和 1 两个桶！
}
```

**错误后果**：无论插入多少元素，只有两个桶可用，冲突极其严重。

**另一个错误例子（字符串哈希）**：

```cpp
int badStringHash(const string& s) {
    return s[0];  // 只取第一个字符！
}
```

**错误后果**：所有首字符相同的字符串都会冲突。

### 错误三：负载因子过高时不扩容

**错误代码**：

```cpp
class HashTable {
private:
    vector<list<int>> table;
    int tableSize;
    
public:
    HashTable(int m) : tableSize(m) {
        table.resize(tableSize);
    }
    
    void insert(int key) {
        int index = key % tableSize;
        table[index].push_back(key);
        // 没有检查负载因子！没有 rehash！
    }
};
```

**错误后果**：随着元素增多，链表越来越长，查找性能急剧下降。

### 错误四：链地址法删除节点时内存泄漏

**错误代码**：

```cpp
bool remove(int key) {
    int index = key % tableSize;
    auto it = table[index].begin();
    while (it != table[index].end()) {
        if (*it == key) {
            table[index].erase(it);  // 删除了，但没有释放内存！
            return true;
        }
        ++it;
    }
    return false;
}
```

**错误后果**：使用指针实现的链表会导致内存泄漏。

**另一个错误例子（删除头节点时指针更新错误）**：

```cpp
struct Node {
    int key;
    Node* next;
};

bool remove(int key) {
    int index = key % tableSize;
    Node* current = table[index];
    Node* prev = nullptr;
    
    while (current != nullptr) {
        if (current->key == key) {
            if (prev != nullptr) {
                prev->next = current->next;
            }
            // 忘记处理 prev == nullptr（头节点）的情况！
            delete current;
            return true;
        }
        prev = current;
        current = current->next;
    }
    return false;
}
```

**错误后果**：删除头节点时，桶的指针没有更新，导致头节点仍然指向已删除的节点。

### 错误五：开放地址法删除时未处理墓碑

**错误代码**：

```cpp
class HashTableOpen {
private:
    vector<int> table;
    int tableSize;
    
public:
    HashTableOpen(int m) : tableSize(m) {
        table.resize(m, -1);
    }
    
    bool remove(int key) {
        int index = key % tableSize;
        while (table[index] != -1) {
            if (table[index] == key) {
                table[index] = -1;  // 直接标记为空！
                return true;
            }
            index = (index + 1) % tableSize;
        }
        return false;
    }
    
    bool search(int key) {
        int index = key % tableSize;
        while (table[index] != -1) {
            if (table[index] == key) return true;
            index = (index + 1) % tableSize;
        }
        return false;
    }
};
```

**错误后果**：删除元素后，后续的查找链被中断，导致某些元素无法被找到。

### 错误六：错误理解哈希函数的确定性

**错误理解**：以为哈希函数每次计算结果都不同，或者以为哈希函数是加密的。

**错误代码**：

```cpp
int randomHash(int key) {
    srand(time(nullptr));
    return rand() % tableSize;  // 每次调用结果都不同！
}
```

**错误后果**：同一个 key 每次插入和查找得到不同的索引，导致无法正确查找。

## 正确做法

### 错误一正确做法

理解哈希表的性能取决于负载因子和哈希函数：

```cpp
// 保证哈希函数均匀分布
int goodHash(int key) {
    return key % tableSize;  // tableSize 最好是质数
}

// 定期检查负载因子
double loadFactor() {
    return (double)count / tableSize;
}
```

### 错误二正确做法

设计合理的哈希函数：

```cpp
// 整数哈希
int goodHash(int key) {
    return abs(key) % tableSize;
}

// 字符串哈希
int goodStringHash(const string& s) {
    int hashValue = 0;
    for (char c : s) {
        hashValue = hashValue * 31 + c;
    }
    return abs(hashValue) % tableSize;
}
```

### 错误三正确做法

实现 rehash 功能：

```cpp
void rehash() {
    vector<list<int>> oldTable = table;
    tableSize *= 2;
    table.clear();
    table.resize(tableSize);
    
    for (auto& bucket : oldTable) {
        for (int key : bucket) {
            insert(key);
        }
    }
}

void insert(int key) {
    if ((double)count / tableSize > 0.75) {
        rehash();
    }
    int index = key % tableSize;
    table[index].push_back(key);
    count++;
}
```

### 错误四正确做法

正确删除节点并释放内存：

```cpp
bool remove(int key) {
    int index = key % tableSize;
    Node* current = table[index];
    Node* prev = nullptr;
    
    while (current != nullptr) {
        if (current->key == key) {
            if (prev == nullptr) {
                table[index] = current->next;  // 更新头指针
            } else {
                prev->next = current->next;
            }
            delete current;  // 释放内存
            count--;
            return true;
        }
        prev = current;
        current = current->next;
    }
    return false;
}
```

### 错误五正确做法

使用墓碑标记处理开放地址法的删除：

```cpp
const int EMPTY = -1;
const int TOMBSTONE = -2;

bool remove(int key) {
    int index = key % tableSize;
    while (table[index] != EMPTY) {
        if (table[index] == key) {
            table[index] = TOMBSTONE;  // 使用墓碑标记
            return true;
        }
        index = (index + 1) % tableSize;
    }
    return false;
}

bool search(int key) {
    int index = key % tableSize;
    while (table[index] != EMPTY) {
        if (table[index] == key) return true;
        index = (index + 1) % tableSize;
    }
    return false;  // 跳过墓碑继续查找
}

bool insert(int key) {
    int index = key % tableSize;
    int originalIndex = index;
    int tombstoneIndex = -1;
    
    do {
        if (table[index] == EMPTY) {
            if (tombstoneIndex != -1) {
                table[tombstoneIndex] = key;  // 优先插入墓碑位置
            } else {
                table[index] = key;
            }
            return true;
        }
        if (table[index] == TOMBSTONE && tombstoneIndex == -1) {
            tombstoneIndex = index;
        }
        if (table[index] == key) {
            return true;
        }
        index = (index + 1) % tableSize;
    } while (index != originalIndex);
    
    return false;
}
```

### 错误六正确做法

使用确定性的哈希函数：

```cpp
int goodHash(int key) {
    return key % tableSize;  // 同一输入总是产生相同输出
}
```

### 错误与正确对比

| 错误类型 | 错误做法 | 正确做法 |
|----------|----------|----------|
| 认为总是 O(1) | 忽略负载因子 | 监控负载因子，及时 rehash |
| 哈希函数不合理 | key % 2 或只取首字符 | 使用均匀分布的哈希函数 |
| 不扩容 | 无限插入不 rehash | 负载因子 > 0.75 时扩容 |
| 内存泄漏 | 删除节点不释放内存 | delete current |
| 删除头节点错误 | 不更新桶指针 | table[index] = current->next |
| 开放地址法删除 | 直接置为 EMPTY | 使用 TOMBSTONE 标记 |
| 哈希函数不确定 | 使用 rand() | 使用确定性计算 |

## 自查题

### 题目一

**题目描述**：分析以下哈希函数的问题并提出改进方案。

```cpp
int hashFunction(int key) {
    return 1;  // 所有元素都映射到 index 1
}
```

**答案要点**：

**问题**：
- 所有元素都映射到同一个桶（index 1）
- 哈希表退化为链表，查找时间从 O(1) 变为 O(n)

**改进方案**：

```cpp
int hashFunction(int key) {
    return abs(key) % tableSize;
}
```

**改进理由**：
- 使用取模运算将 key 均匀分布到所有桶
- tableSize 最好选择质数，减少冲突

### 题目二

**题目描述**：指出以下开放地址法（线性探测）删除实现的问题并修正。

```cpp
const int EMPTY = -1;

bool remove(int key) {
    int index = key % 7;
    while (table[index] != EMPTY) {
        if (table[index] == key) {
            table[index] = EMPTY;
            return true;
        }
        index = (index + 1) % 7;
    }
    return false;
}
```

**答案要点**：

**问题**：
- 直接将删除位置标记为 EMPTY（-1）
- 这会中断查找链，导致后续插入的元素无法被找到

**例如**：
1. 插入 10（hash=3）→ index 3
2. 插入 17（hash=3，冲突）→ index 4
3. 删除 10 → index 3 变为 EMPTY
4. 查找 17：从 index 3 开始，遇到 EMPTY 就停止，找不到 17！

**修正代码**：

```cpp
const int EMPTY = -1;
const int TOMBSTONE = -2;

bool remove(int key) {
    int index = key % 7;
    while (table[index] != EMPTY) {
        if (table[index] == key) {
            table[index] = TOMBSTONE;  // 使用墓碑标记
            return true;
        }
        index = (index + 1) % 7;
    }
    return false;
}

bool search(int key) {
    int index = key % 7;
    while (table[index] != EMPTY) {
        if (table[index] == key) return true;
        index = (index + 1) % 7;
    }
    return false;
}
```

### 题目三

**题目描述**：分析以下说法是否正确："负载因子越小，哈希表的性能越好，所以应该把负载因子设为 0.1。"

**答案要点**：

**不完全正确**。

**理由**：

1. **负载因子小的好处**：冲突概率低，每个桶的链表短，查找速度快。

2. **负载因子过小的问题**：
   - **空间浪费**：桶的数量远大于元素数量，大量桶为空
   - **缓存效率低**：哈希表占用更多内存，缓存命中率下降
   - **综合性能不一定更好**：虽然查找快，但内存占用大，可能导致整体性能下降

3. **合理的负载因子**：
   - 通常取 **0.7~0.8**
   - 这个范围在时间效率和空间效率之间取得平衡
   - 当负载因子超过阈值时，进行 rehash（扩容）

**对比**：

| 负载因子 | 优点 | 缺点 |
|----------|------|------|
| 0.1 | 冲突极少，查找极快 | 空间浪费严重，90% 的桶为空 |
| 0.75 | 时间空间平衡 | 需要定期 rehash |
| 0.95 | 空间利用率高 | 冲突严重，链表长，查找慢 |

**结论**：负载因子不是越小越好，需要在时间效率和空间效率之间取得平衡。