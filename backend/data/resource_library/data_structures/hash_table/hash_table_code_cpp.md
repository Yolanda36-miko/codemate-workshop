# 散列表代码示例（链地址法）

## 代码目标

本代码实现一个基于链地址法的散列表，支持插入（insert）、查找（search）和删除（remove）操作。哈希函数采用 `key % tableSize`。通过具体示例演示哈希表的构建、插入冲突时的链表增长，以及查找和删除操作。

## 核心代码

```cpp
#include <iostream>
#include <vector>
using namespace std;

struct HashNode {
    int key;
    HashNode* next;
    HashNode(int k) : key(k), next(nullptr) {}
};

class HashTable {
private:
    vector<HashNode*> table;
    int tableSize;

    int hashFunction(int key) {
        return key % tableSize;
    }

public:
    HashTable(int m) : tableSize(m) {
        table.resize(tableSize, nullptr);
    }

    ~HashTable() {
        for (int i = 0; i < tableSize; i++) {
            HashNode* current = table[i];
            while (current != nullptr) {
                HashNode* next = current->next;
                delete current;
                current = next;
            }
        }
    }

    void insert(int key) {
        int index = hashFunction(key);
        HashNode* newNode = new HashNode(key);

        if (table[index] == nullptr) {
            table[index] = newNode;
        } else {
            HashNode* current = table[index];
            while (current->next != nullptr) {
                if (current->key == key) {
                    cout << "键 " << key << " 已存在，跳过插入" << endl;
                    delete newNode;
                    return;
                }
                current = current->next;
            }
            if (current->key == key) {
                cout << "键 " << key << " 已存在，跳过插入" << endl;
                delete newNode;
                return;
            }
            current->next = newNode;
        }
        cout << "插入 " << key << " → index " << index << endl;
    }

    bool search(int key) {
        int index = hashFunction(key);
        HashNode* current = table[index];
        while (current != nullptr) {
            if (current->key == key) {
                return true;
            }
            current = current->next;
        }
        return false;
    }

    bool remove(int key) {
        int index = hashFunction(key);
        HashNode* current = table[index];
        HashNode* prev = nullptr;

        while (current != nullptr) {
            if (current->key == key) {
                if (prev == nullptr) {
                    table[index] = current->next;
                } else {
                    prev->next = current->next;
                }
                delete current;
                return true;
            }
            prev = current;
            current = current->next;
        }
        return false;
    }

    void printTable() {
        cout << "Hash Table (size=" << tableSize << "):" << endl;
        for (int i = 0; i < tableSize; i++) {
            cout << "[" << i << "]: ";
            HashNode* current = table[i];
            while (current != nullptr) {
                cout << current->key;
                if (current->next != nullptr) {
                    cout << " -> ";
                }
                current = current->next;
            }
            cout << endl;
        }
    }
};

int main() {
    HashTable ht(7);

    int keys[] = {10, 22, 31, 4, 15, 28};
    for (int key : keys) {
        ht.insert(key);
    }

    cout << endl;
    ht.printTable();

    cout << endl << "Search 31: " << (ht.search(31) ? "Found" : "Not Found") << endl;
    cout << "Search 25: " << (ht.search(25) ? "Found" : "Not Found") << endl;

    cout << endl << "After deleting 31:" << endl;
    ht.remove(31);
    ht.printTable();

    return 0;
}
```

## 关键步骤解释

### 哈希函数

```cpp
int hashFunction(int key) {
    return key % tableSize;
}
```

**解释**：使用取模运算作为哈希函数，将任意整数 key 映射到 [0, tableSize) 范围内的数组下标。取模运算简单高效，但要求 tableSize 最好是质数以减少冲突。

### 插入操作（尾插法）

```cpp
void insert(int key) {
    int index = hashFunction(key);
    HashNode* newNode = new HashNode(key);

    if (table[index] == nullptr) {
        table[index] = newNode;
    } else {
        HashNode* current = table[index];
        while (current->next != nullptr) {
            if (current->key == key) {
                delete newNode;
                return;
            }
            current = current->next;
        }
        if (current->key == key) {
            delete newNode;
            return;
        }
        current->next = newNode;
    }
}
```

**解释**：
1. 计算哈希值得到 index
2. 如果桶为空，直接将新节点作为头节点
3. 如果桶不为空，遍历到链表尾部
4. 遍历过程中检查 key 是否已存在（存在则不插入）
5. 将新节点插入到链表尾部

**为什么选择尾插法**：尾插法保持插入顺序，符合直观预期。头插法虽然更快，但会改变元素顺序。

### 查找操作

```cpp
bool search(int key) {
    int index = hashFunction(key);
    HashNode* current = table[index];
    while (current != nullptr) {
        if (current->key == key) {
            return true;
        }
        current = current->next;
    }
    return false;
}
```

**解释**：
1. 计算哈希值得到 index
2. 从该桶的头节点开始遍历链表
3. 逐一比较 key，找到则返回 true
4. 遍历到链表末尾仍未找到，返回 false

### 删除操作

```cpp
bool remove(int key) {
    int index = hashFunction(key);
    HashNode* current = table[index];
    HashNode* prev = nullptr;

    while (current != nullptr) {
        if (current->key == key) {
            if (prev == nullptr) {
                table[index] = current->next;
            } else {
                prev->next = current->next;
            }
            delete current;
            return true;
        }
        prev = current;
        current = current->next;
    }
    return false;
}
```

**解释**：
1. 使用两个指针：`current` 指向当前节点，`prev` 指向前一个节点
2. 如果待删除节点是头节点（`prev == nullptr`），需要更新桶的头指针
3. 如果待删除节点是中间或尾部节点，将前一个节点的 `next` 指向当前节点的 `next`
4. 释放被删除节点的内存

### 析构函数

```cpp
~HashTable() {
    for (int i = 0; i < tableSize; i++) {
        HashNode* current = table[i];
        while (current != nullptr) {
            HashNode* next = current->next;
            delete current;
            current = next;
        }
    }
}
```

**解释**：遍历所有桶和链表，释放每个节点的内存，避免内存泄漏。这是使用手动内存管理时必须注意的问题。

## 输入输出示例

运行上述代码，输出结果为：

```
插入 10 → index 3
插入 22 → index 1
插入 31 → index 3
插入 4 → index 4
插入 15 → index 1
插入 28 → index 0

Hash Table (size=7):
[0]: 28
[1]: 22 -> 15
[2]: 
[3]: 10 -> 31
[4]: 4
[5]: 
[6]: 

Search 31: Found
Search 25: Not Found

After deleting 31:
Hash Table (size=7):
[0]: 28
[1]: 22 -> 15
[2]: 
[3]: 10
[4]: 4
[5]: 
[6]: 
```

### 输出分析

| 步骤 | 操作 | 哈希值 | 冲突 | 桶内容变化 |
|------|------|--------|------|-----------|
| 1 | 插入 10 | 10 % 7 = 3 | 否 | [3]: 10 |
| 2 | 插入 22 | 22 % 7 = 1 | 否 | [1]: 22 |
| 3 | 插入 31 | 31 % 7 = 3 | **是** | [3]: 10 -> 31 |
| 4 | 插入 4 | 4 % 7 = 4 | 否 | [4]: 4 |
| 5 | 插入 15 | 15 % 7 = 1 | **是** | [1]: 22 -> 15 |
| 6 | 插入 28 | 28 % 7 = 0 | 否 | [0]: 28 |

**桶内容与插入过程的对应关系**：
- index 3：先插入 10，再插入 31 时冲突，形成链表 `10 -> 31`
- index 1：先插入 22，再插入 15 时冲突，形成链表 `22 -> 15`
- index 0、4：只有单个元素，无冲突

## 边界条件

### 插入的 key 已存在

```cpp
while (current->next != nullptr) {
    if (current->key == key) {
        delete newNode;
        return;
    }
    current = current->next;
}
if (current->key == key) {
    delete newNode;
    return;
}
```

**处理方式**：遍历链表检查 key 是否已存在，存在则释放新节点并返回，不允许重复键。

### 表满

链地址法没有"满"的概念，理论上可以无限插入。但当负载因子过高（如 > 0.75）时，链表变长，性能下降，需要考虑扩容（rehash）。

### 删除不存在的 key

```cpp
while (current != nullptr) {
    if (current->key == key) {
        // 删除节点
        return true;
    }
    prev = current;
    current = current->next;
}
return false;
```

**处理方式**：遍历链表未找到目标 key，返回 false，不做任何操作。

### 查找空表或空桶

```cpp
HashNode* current = table[index];
while (current != nullptr) {
    // 遍历查找
}
return false;
```

**处理方式**：空桶时 `current` 为 nullptr，直接返回 false，不进入循环。

## 时间复杂度和空间复杂度

### 时间复杂度

| 操作 | 平均情况 | 最坏情况 |
|------|---------|---------|
| 插入 | O(1) | O(n) |
| 查找 | O(1) | O(n) |
| 删除 | O(1) | O(n) |

**解释**：
- 平均情况：哈希函数均匀分布，每个桶的链表长度为 O(1)
- 最坏情况：所有 key 都映射到同一个桶，链表长度为 n

### 空间复杂度

**O(n + m)**：
- n：元素个数，每个元素对应一个 HashNode
- m：桶的大小，vector 数组占用的空间

## 改写练习

### 练习一：支持字符串 key

```cpp
#include <string>

class HashTableString {
private:
    vector<HashNode*> table;
    int tableSize;

    int hashFunction(const string& key) {
        int hashValue = 0;
        for (char c : key) {
            hashValue = hashValue * 31 + c;
        }
        return abs(hashValue) % tableSize;
    }

public:
    HashTableString(int m) : tableSize(m) {
        table.resize(tableSize, nullptr);
    }

    void insert(const string& key) {
        int index = hashFunction(key);
        HashNode* current = table[index];
        while (current != nullptr) {
            if (current->key == stoi(key)) {
                return;
            }
            current = current->next;
        }
        HashNode* newNode = new HashNode(stoi(key));
        newNode->next = table[index];
        table[index] = newNode;
    }
};
```

### 练习二：开放地址法（线性探测）

```cpp
class HashTableOpenAddressing {
private:
    vector<int> table;
    vector<bool> occupied;
    int tableSize;

    int hashFunction(int key) {
        return key % tableSize;
    }

public:
    HashTableOpenAddressing(int m) : tableSize(m) {
        table.resize(m, -1);
        occupied.resize(m, false);
    }

    bool insert(int key) {
        int index = hashFunction(key);
        int originalIndex = index;

        do {
            if (!occupied[index]) {
                table[index] = key;
                occupied[index] = true;
                return true;
            }
            if (table[index] == key) {
                return true;
            }
            index = (index + 1) % tableSize;
        } while (index != originalIndex);

        return false;
    }

    bool search(int key) {
        int index = hashFunction(key);
        int originalIndex = index;

        do {
            if (!occupied[index]) return false;
            if (table[index] == key) return true;
            index = (index + 1) % tableSize;
        } while (index != originalIndex);

        return false;
    }

    bool remove(int key) {
        int index = hashFunction(key);
        int originalIndex = index;

        do {
            if (!occupied[index]) return false;
            if (table[index] == key) {
                occupied[index] = false;
                return true;
            }
            index = (index + 1) % tableSize;
        } while (index != originalIndex);

        return false;
    }
};
```

### 练习三：实现 rehash 功能

```cpp
void rehash() {
    vector<HashNode*> oldTable = table;
    tableSize *= 2;
    table.clear();
    table.resize(tableSize, nullptr);

    for (int i = 0; i < oldTable.size(); i++) {
        HashNode* current = oldTable[i];
        while (current != nullptr) {
            insert(current->key);
            HashNode* next = current->next;
            delete current;
            current = next;
        }
    }
}

void insert(int key) {
    if ((double)count() / tableSize > 0.75) {
        rehash();
    }

    int index = hashFunction(key);
    HashNode* newNode = new HashNode(key);

    if (table[index] == nullptr) {
        table[index] = newNode;
    } else {
        HashNode* current = table[index];
        while (current->next != nullptr) {
            if (current->key == key) {
                delete newNode;
                return;
            }
            current = current->next;
        }
        current->next = newNode;
    }
}

int count() {
    int cnt = 0;
    for (int i = 0; i < tableSize; i++) {
        HashNode* current = table[i];
        while (current != nullptr) {
            cnt++;
            current = current->next;
        }
    }
    return cnt;
}
```