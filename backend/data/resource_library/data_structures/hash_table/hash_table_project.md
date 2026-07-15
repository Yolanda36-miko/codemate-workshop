# 单词频率统计器

## 项目场景

设计一个"单词频率统计器"——给定一段英文文本（例如文章、书籍章节或用户输入的段落），统计其中每个单词出现的次数，并按出现次数从高到低输出结果。

**示例输入**：

```
To be or not to be, that is the question.
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles,
And by opposing end them?
```

**示例输出**：

```
词频排行（前10）：
1. to: 3
2. or: 2
3. be: 2
4. the: 2
5. that: 1
6. is: 1
7. question: 1
8. whether: 1
9. tis: 1
10. nobler: 1
```

这个场景广泛应用于搜索引擎、文本分析、词云生成等实际应用中，哈希表是解决此类问题最合适的数据结构。

## 任务目标

1. **接收文本输入**：支持从代码中定义或从文件读取英文文本
2. **文本预处理**：将文本拆分为单词，忽略大小写，去除标点符号
3. **词频统计**：使用哈希表存储单词和对应的出现次数
4. **排序输出**：按出现次数降序输出每个单词及其频率
5. **单词查询**：支持查询某个单词的出现次数
6. **统计信息**：输出总单词数（去重前和去重后）
7. **命令行交互**：提供菜单选择界面

## 为什么使用该数据结构

### 问题特征分析

| 特征 | 说明 |
|------|------|
| 键值映射 | 单词到频率的映射天然适合 key-value 结构 |
| O(1) 复杂度 | 插入和查找的平均时间复杂度为 O(1) |
| 冲突处理 | 链地址法适合处理哈希冲突 |
| 动态扩容 | rehash 机制支持处理大量单词 |

### 哈希表的优势

- **高效统计**：插入和查找平均 O(1)，处理大量文本效率极高
- **天然匹配**：word-count 正好对应哈希表的 key-value 结构
- **冲突处理**：链地址法可以优雅处理哈希冲突
- **负载管理**：rehash 机制确保性能稳定

## 实现步骤

### 步骤一：定义哈希表

使用链地址法实现哈希表，支持插入、查找和 rehash。

### 步骤二：文本预处理

实现 `preprocessText()` 函数：
- 将文本转为小写
- 按空格和标点分割为单词列表

### 步骤三：词频统计

遍历单词列表：
- 如果单词已存在，计数 +1
- 如果单词不存在，插入哈希表，计数设为 1

### 步骤四：查询功能

实现 `search()` 函数，返回指定单词的出现次数。

### 步骤五：排序输出

实现 `getAllWords()` 获取所有单词，按出现次数降序排序并输出。

### 步骤六：命令行交互

提供菜单：
1. 统计文本
2. 查询单词
3. 显示排行
4. 退出

### 步骤七（可选）：文件读取

支持从文件读取文本，处理更大规模的输入。

## 核心数据结构设计

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

struct WordNode {
    string word;
    int count;
    WordNode* next;
    WordNode(string w) : word(w), count(1), next(nullptr) {}
};

class HashTable {
private:
    vector<WordNode*> table;
    int tableSize;
    int elementCount;

    int hash(const string& word) {
        int hashValue = 0;
        for (char c : word) {
            hashValue = hashValue * 31 + c;
        }
        return abs(hashValue) % tableSize;
    }

    void rehash() {
        vector<WordNode*> oldTable = table;
        tableSize *= 2;
        table.clear();
        table.resize(tableSize, nullptr);
        elementCount = 0;

        for (auto& bucket : oldTable) {
            WordNode* current = bucket;
            while (current != nullptr) {
                insert(current->word, current->count);
                WordNode* next = current->next;
                delete current;
                current = next;
            }
        }
    }

public:
    HashTable(int initialSize = 101) : tableSize(initialSize), elementCount(0) {
        table.resize(tableSize, nullptr);
    }

    ~HashTable() {
        for (auto& bucket : table) {
            WordNode* current = bucket;
            while (current != nullptr) {
                WordNode* next = current->next;
                delete current;
                current = next;
            }
        }
    }

    void insert(const string& word) {
        if ((double)elementCount / tableSize > 0.75) {
            rehash();
        }

        int index = hash(word);
        WordNode* current = table[index];
        while (current != nullptr) {
            if (current->word == word) {
                current->count++;
                return;
            }
            current = current->next;
        }

        WordNode* newNode = new WordNode(word);
        newNode->next = table[index];
        table[index] = newNode;
        elementCount++;
    }

    void insert(const string& word, int cnt) {
        int index = hash(word);
        WordNode* current = table[index];
        while (current != nullptr) {
            if (current->word == word) {
                current->count = cnt;
                return;
            }
            current = current->next;
        }
        WordNode* newNode = new WordNode(word);
        newNode->count = cnt;
        newNode->next = table[index];
        table[index] = newNode;
        elementCount++;
    }

    int search(const string& word) {
        int index = hash(word);
        WordNode* current = table[index];
        while (current != nullptr) {
            if (current->word == word) {
                return current->count;
            }
            current = current->next;
        }
        return 0;
    }

    vector<pair<string, int>> getAllWords() {
        vector<pair<string, int>> result;
        for (auto& bucket : table) {
            WordNode* current = bucket;
            while (current != nullptr) {
                result.push_back({current->word, current->count});
                current = current->next;
            }
        }
        sort(result.begin(), result.end(), [](const pair<string, int>& a, const pair<string, int>& b) {
            return a.second > b.second;
        });
        return result;
    }

    int getTotalCount() {
        int total = 0;
        for (auto& bucket : table) {
            WordNode* current = bucket;
            while (current != nullptr) {
                total += current->count;
                current = current->next;
            }
        }
        return total;
    }

    int getUniqueCount() {
        return elementCount;
    }
};
```

### 数据结构说明

| 数据结构 | 类型 | 说明 |
|----------|------|------|
| WordNode | struct | 存储单词、计数和链表指针 |
| table | vector\<WordNode*\> | 桶数组，每个桶是一个链表 |
| tableSize | int | 桶的数量 |
| elementCount | int | 不同单词的数量 |

## 核心代码框架或伪代码

### WordNode 结构体

```
struct WordNode:
    word: string
    count: int
    next: WordNode*
```

### HashTable 核心函数

```
function hash(word):
    hashValue = 0
    for each char c in word:
        hashValue = hashValue * 31 + c
    return abs(hashValue) % tableSize

function insert(word):
    if loadFactor > 0.75:
        rehash()
    
    index = hash(word)
    current = table[index]
    
    while current != nullptr:
        if current.word == word:
            current.count++
            return
        current = current.next
    
    newNode = WordNode(word)
    newNode.next = table[index]
    table[index] = newNode
    elementCount++

function search(word):
    index = hash(word)
    current = table[index]
    
    while current != nullptr:
        if current.word == word:
            return current.count
        current = current.next
    
    return 0

function rehash():
    oldTable = table
    tableSize *= 2
    table = new empty table
    
    for each bucket in oldTable:
        while bucket not empty:
            insert(node.word, node.count)
            delete node
```

### 文本预处理函数

```
function preprocessText(text):
    words = empty list
    
    currentWord = ""
    for each char c in text:
        if c is letter:
            currentWord += toLower(c)
        else if currentWord not empty:
            add currentWord to words
            currentWord = ""
    
    if currentWord not empty:
        add currentWord to words
    
    return words
```

### Main 函数交互流程

```
function main():
    ht = HashTable()
    totalWords = 0
    
    while true:
        print menu:
            1. 统计文本
            2. 查询单词
            3. 显示排行
            4. 退出
        
        read choice
        
        if choice == 1:
            print "请输入文本："
            read text
            words = preprocessText(text)
            totalWords += len(words)
            for each word in words:
                ht.insert(word)
            print "统计完成！"
        
        elif choice == 2:
            print "请输入要查询的单词："
            read word
            count = ht.search(word)
            print word + ": " + count
        
        elif choice == 3:
            print "请输入显示数量（0表示全部）："
            read n
            allWords = ht.getAllWords()
            print "总单词数（去重前）：" + totalWords
            print "总单词数（去重后）：" + ht.getUniqueCount()
            print "词频排行："
            for i from 0 to min(n, len(allWords)):
                print (i+1) + ". " + allWords[i].word + ": " + allWords[i].count
        
        elif choice == 4:
            break
```

## 测试用例

### 测试用例一：简单文本

**输入**：`"hello world hello"`

**期望输出**：

```
词频排行：
1. hello: 2
2. world: 1
总单词数（去重前）：3
总单词数（去重后）：2
```

### 测试用例二：完整句子

**输入**：`"The quick brown fox jumps over the lazy dog"`

**期望输出**：

```
词频排行：
1. the: 2
2. quick: 1
3. brown: 1
4. fox: 1
5. jumps: 1
6. over: 1
7. lazy: 1
8. dog: 1
总单词数（去重前）：9
总单词数（去重后）：8
```

### 测试用例三：含标点文本

**输入**：`"To be or not to be, that is the question."`

**期望输出**：

```
词频排行：
1. to: 2
2. be: 2
3. or: 1
4. not: 1
5. that: 1
6. is: 1
7. the: 1
8. question: 1
总单词数（去重前）：9
总单词数（去重后）：8
```

### 测试用例四：查询功能

**输入**：查询 `"be"` 和 `"apple"`

**期望输出**：

```
查询 be: 2
查询 apple: 0
```

### 测试用例五（扩展）：文件读取

**输入**：从文件读取一篇较长的英文文章

**期望输出**：

```
总单词数（去重前）：15000
总单词数（去重后）：3500
词频排行（前10）：
1. the: 850
2. a: 620
3. is: 480
4. of: 450
5. and: 420
6. to: 400
7. in: 380
8. that: 320
9. for: 290
10. on: 260
```

## 扩展方向

### 扩展一：停用词过滤

过滤常见的停用词（如 "the", "a", "an", "is" 等）：

```cpp
vector<string> stopWords = {"the", "a", "an", "is", "are", "was", "were"};

bool isStopWord(const string& word) {
    for (const string& stop : stopWords) {
        if (word == stop) return true;
    }
    return false;
}

void insert(const string& word) {
    if (isStopWord(word)) return;
    // ... 正常插入逻辑
}
```

### 扩展二：n-gram 短语统计

统计连续 n 个单词的组合频率：

```cpp
void insertNgram(const vector<string>& words, int n) {
    for (int i = 0; i <= words.size() - n; i++) {
        string ngram = "";
        for (int j = 0; j < n; j++) {
            if (j > 0) ngram += " ";
            ngram += words[i+j];
        }
        insert(ngram);
    }
}
```

### 扩展三：导出功能

将结果导出为 CSV 或 JSON 格式：

```cpp
void exportToCSV(const string& filename) {
    ofstream file(filename);
    file << "word,count" << endl;
    vector<pair<string, int>> allWords = getAllWords();
    for (auto& pair : allWords) {
        file << pair.first << "," << pair.second << endl;
    }
    file.close();
}
```

### 扩展四：图形化输出

生成简单的文本柱状图或词云：

```
词频分布：
the     ████████████████████████ 850
a       ███████████████████      620
is      ████████████████         480
of      ███████████████          450
and     ██████████████           420
```

### 扩展五：多语言支持

扩展 Unicode 字符处理，支持中文、日文等语言：

```cpp
int hash(const wstring& word) {
    int hashValue = 0;
    for (wchar_t c : word) {
        hashValue = hashValue * 31 + c;
    }
    return abs(hashValue) % tableSize;
}
```