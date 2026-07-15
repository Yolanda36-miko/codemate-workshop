# 词典查询与单词补全系统

## 项目场景

设计一个"词典查询与单词补全系统"——给定一个按字母顺序排列的英文词典（单词列表），用户输入一个单词前缀，系统需要快速找到所有以该前缀开头的单词，并统计数量。同时支持插入新单词并保持词典有序。

**示例操作**：

```
词典: ["apple", "banana", "grape", "orange", "peach"]

查询前缀 "ap" → 返回 ["apple"], count=1
查询前缀 "a"   → 返回 ["apple"], count=1
插入 "avocado"
查询前缀 "a"   → 返回 ["apple", "avocado"], count=2
```

这个场景广泛应用于搜索引擎的自动补全、拼写检查、词典应用等。

## 任务目标

1. **加载词典**：`load(dictionary)` —— 从文件或内存加载初始词典
2. **插入单词**：`insert(word)` —— 插入新单词，保持有序
3. **精确查找**：`search(word)` —— 查找单词是否存在
4. **前缀查询**：`startsWith(prefix)` —— 返回所有以给定前缀开头的单词列表
5. **前缀计数**：`countPrefix(prefix)` —— 返回以给定前缀开头的单词数量
6. **命令行交互**：提供菜单选择界面，测试上述功能
7. **边界处理**：处理空字符串、不存在的前缀、重复插入等情况

## 为什么使用该数据结构

### 问题特征分析

| 特征 | 说明 |
|------|------|
| 有序性 | 词典是按字母顺序排列的 |
| 前缀范围 | 需要查找前缀的起始和结束位置 |
| O(log n) 复杂度 | 二分查找可以快速定位边界 |
| 动态插入 | 需要保持有序插入 |

### 二分查找边界的优势

- **高效定位**：使用 lower_bound 和 upper_bound 在 O(log n) 时间内定位前缀范围
- **巧妙的边界技巧**：利用 `prefix + '{'` 找到前缀范围的结束位置（'{' 是 'z' 的下一个 ASCII 字符）
- **有序插入**：插入位置可以用 lower_bound 快速找到，O(log n) + O(n)（数组移动）
- **实际应用价值**：这个项目展示了二分查找边界在实际产品中的核心价值

### 前缀范围原理

```
词典: ["apple", "avocado", "banana", "grape", "orange", "peach"]

查找前缀 "a"：
lower_bound("a") → 返回第一个 >= "a" 的位置（索引 0，"apple"）
lower_bound("a{") → 返回第一个 >= "a{" 的位置（索引 2，"banana"）
前缀范围: [0, 2) → ["apple", "avocado"]

查找前缀 "ap"：
lower_bound("ap") → 返回第一个 >= "ap" 的位置（索引 0，"apple"）
lower_bound("ap{") → 返回第一个 >= "ap{" 的位置（索引 1，"avocado"）
前缀范围: [0, 1) → ["apple"]
```

## 实现步骤

### 步骤一：初始化词典

```cpp
vector<string> dictionary;

void loadDictionary(const vector<string>& words) {
    dictionary = words;
    sort(dictionary.begin(), dictionary.end());
}
```

### 步骤二：实现 lowerBound

```cpp
int lowerBound(const string& target) {
    int left = 0, right = dictionary.size();
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (dictionary[mid] >= target) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }
    return left;
}
```

### 步骤三：实现 insert

```cpp
void insertWord(const string& word) {
    int pos = lowerBound(word);
    if (pos < dictionary.size() && dictionary[pos] == word) {
        cout << "单词 \"" << word << "\" 已存在，跳过插入" << endl;
        return;
    }
    dictionary.insert(dictionary.begin() + pos, word);
    cout << "插入单词 \"" << word << "\" 成功" << endl;
}
```

### 步骤四：实现 search

```cpp
bool searchWord(const string& word) {
    int pos = lowerBound(word);
    return pos < dictionary.size() && dictionary[pos] == word;
}
```

### 步骤五：实现 startsWith

```cpp
vector<string> getWordsWithPrefix(const string& prefix) {
    string endPrefix = prefix + '{';
    int left = lowerBound(prefix);
    int right = lowerBound(endPrefix);
    
    vector<string> result;
    for (int i = left; i < right; i++) {
        result.push_back(dictionary[i]);
    }
    return result;
}
```

### 步骤六：实现 countPrefix

```cpp
int countWordsWithPrefix(const string& prefix) {
    string endPrefix = prefix + '{';
    int left = lowerBound(prefix);
    int right = lowerBound(endPrefix);
    return right - left;
}
```

### 步骤七：编写 main 函数

```cpp
int main() {
    vector<string> initialWords = {"apple", "banana", "grape", "orange", "peach"};
    loadDictionary(initialWords);
    
    string command, word, prefix;
    
    while (true) {
        cout << "\n请输入命令 (insert/search/startsWith/count/print/exit): ";
        cin >> command;
        
        if (command == "insert") {
            cin >> word;
            insertWord(word);
        } else if (command == "search") {
            cin >> word;
            cout << "单词 \"" << word << "\" " 
                 << (searchWord(word) ? "存在" : "不存在") << endl;
        } else if (command == "startsWith") {
            cin >> prefix;
            vector<string> words = getWordsWithPrefix(prefix);
            cout << "以 \"" << prefix << "\" 开头的单词 (" << words.size() << "个): ";
            for (const string& w : words) {
                cout << w << " ";
            }
            cout << endl;
        } else if (command == "count") {
            cin >> prefix;
            cout << "以 \"" << prefix << "\" 开头的单词数量: " 
                 << countWordsWithPrefix(prefix) << endl;
        } else if (command == "print") {
            cout << "词典内容: ";
            for (const string& w : dictionary) {
                cout << w << " ";
            }
            cout << endl;
        } else if (command == "exit") {
            break;
        } else {
            cout << "未知命令，请重新输入！" << endl;
        }
    }
    
    return 0;
}
```

## 核心数据结构设计

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

class Dictionary {
private:
    vector<string> words;
    
    int lowerBound(const string& target) const {
        int left = 0, right = words.size();
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (words[mid] >= target) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }
        return left;
    }
    
public:
    void load(const vector<string>& initialWords) {
        words = initialWords;
        sort(words.begin(), words.end());
    }
    
    void insert(const string& word) {
        int pos = lowerBound(word);
        if (pos < words.size() && words[pos] == word) {
            cout << "❌ 单词 \"" << word << "\" 已存在" << endl;
            return;
        }
        words.insert(words.begin() + pos, word);
        cout << "✅ 插入单词 \"" << word << "\" 成功" << endl;
    }
    
    bool search(const string& word) const {
        int pos = lowerBound(word);
        return pos < words.size() && words[pos] == word;
    }
    
    vector<string> startsWith(const string& prefix) const {
        string endPrefix = prefix + '{';
        int left = lowerBound(prefix);
        int right = lowerBound(endPrefix);
        
        vector<string> result;
        for (int i = left; i < right; i++) {
            result.push_back(words[i]);
        }
        return result;
    }
    
    int countPrefix(const string& prefix) const {
        string endPrefix = prefix + '{';
        int left = lowerBound(prefix);
        int right = lowerBound(endPrefix);
        return right - left;
    }
    
    void print() const {
        cout << "\n=== 词典内容 ===" << endl;
        for (size_t i = 0; i < words.size(); i++) {
            cout << i + 1 << ". " << words[i] << endl;
        }
    }
    
    size_t size() const {
        return words.size();
    }
};
```

### 数据结构说明

| 数据结构 | 类型 | 说明 |
|----------|------|------|
| words | vector\<string\> | 存储有序单词列表 |

### 核心方法说明

| 方法 | 返回值 | 说明 |
|------|--------|------|
| load(initialWords) | void | 加载初始词典并排序 |
| insert(word) | void | 插入单词，保持有序 |
| search(word) | bool | 精确查找单词是否存在 |
| startsWith(prefix) | vector\<string\> | 返回以 prefix 开头的单词列表 |
| countPrefix(prefix) | int | 返回以 prefix 开头的单词数量 |
| print() | void | 输出词典内容 |

## 核心代码框架或伪代码

### lowerBound 函数伪代码

```
function lowerBound(target):
    left = 0
    right = length(words)
    
    while left < right:
        mid = left + (right - left) / 2
        if words[mid] >= target:
            right = mid
        else:
            left = mid + 1
    
    return left
```

### startsWith 函数伪代码

```
function startsWith(prefix):
    endPrefix = prefix + '{'  // '{' 是 'z' 的下一个字符
    
    left = lowerBound(prefix)
    right = lowerBound(endPrefix)
    
    result = empty list
    for i from left to right - 1:
        add words[i] to result
    
    return result
```

### insertWord 函数伪代码

```
function insertWord(word):
    pos = lowerBound(word)
    
    if pos < length(words) and words[pos] == word:
        print "单词已存在"
        return
    
    insert word at position pos
    print "插入成功"
```

### 主程序交互菜单伪代码

```
function main():
    dictionary = Dictionary()
    dictionary.load(["apple", "banana", "grape", "orange", "peach"])
    
    while true:
        print "\n命令菜单:"
        print "1. insert <word> - 插入单词"
        print "2. search <word> - 精确查找"
        print "3. startsWith <prefix> - 前缀查询"
        print "4. count <prefix> - 前缀计数"
        print "5. print - 显示词典"
        print "6. exit - 退出"
        
        read command
        
        if command == "insert":
            read word
            dictionary.insert(word)
        elif command == "search":
            read word
            print dictionary.search(word) ? "存在" : "不存在"
        elif command == "startsWith":
            read prefix
            words = dictionary.startsWith(prefix)
            print words
        elif command == "count":
            read prefix
            print dictionary.countPrefix(prefix)
        elif command == "print":
            dictionary.print()
        elif command == "exit":
            break
```

## 测试用例

### 测试用例一：查询前缀 "ap"

**操作**：`startsWith("ap")`

**词典**：`["apple", "banana", "grape", "orange", "peach"]`

**期望输出**：

```
以 "ap" 开头的单词 (1个): apple
```

**验证**：

```
lowerBound("ap") → 0（"apple" >= "ap"）
lowerBound("ap{") → 1（"banana" >= "ap{"）
范围: [0, 1) → ["apple"]
```

### 测试用例二：查询前缀 "b"

**操作**：`startsWith("b")`

**期望输出**：

```
以 "b" 开头的单词 (1个): banana
```

**验证**：

```
lowerBound("b") → 1（"banana" >= "b"）
lowerBound("b{") → 2（"grape" >= "b{"）
范围: [1, 2) → ["banana"]
```

### 测试用例三：查询前缀 "p"

**操作**：`startsWith("p")`

**期望输出**：

```
以 "p" 开头的单词 (1个): peach
```

### 测试用例四：插入单词 "avocado"

**操作序列**：

```
insert("avocado")
startsWith("a")
```

**期望输出**：

```
✅ 插入单词 "avocado" 成功
以 "a" 开头的单词 (2个): apple avocado
```

**验证**：

插入后词典变为：`["apple", "avocado", "banana", "grape", "orange", "peach"]`

```
lowerBound("a") → 0
lowerBound("a{") → 2（"banana" >= "a{"）
范围: [0, 2) → ["apple", "avocado"]
```

### 测试用例五：查询前缀 "z"

**操作**：`startsWith("z")`

**期望输出**：

```
以 "z" 开头的单词 (0个):
```

**验证**：

```
lowerBound("z") → 5（所有单词都 < "z"）
lowerBound("z{") → 5
范围: [5, 5) → 空列表
```

### 测试用例六：查询前缀 "g"

**操作**：`startsWith("g")`

**期望输出**：

```
以 "g" 开头的单词 (1个): grape
```

### 测试用例七：插入已存在单词

**操作**：`insert("banana")`

**期望输出**：

```
❌ 单词 "banana" 已存在
```

### 测试用例总结表

| 步骤 | 操作 | 词典状态 | 期望结果 |
|------|------|----------|----------|
| 1 | 初始加载 | ["apple", "banana", "grape", "orange", "peach"] | — |
| 2 | startsWith("ap") | 同上 | ["apple"], count=1 |
| 3 | startsWith("b") | 同上 | ["banana"], count=1 |
| 4 | startsWith("p") | 同上 | ["peach"], count=1 |
| 5 | insert("avocado") | ["apple", "avocado", "banana", "grape", "orange", "peach"] | 插入成功 |
| 6 | startsWith("a") | 同上 | ["apple", "avocado"], count=2 |
| 7 | startsWith("z") | 同上 | [], count=0 |
| 8 | startsWith("g") | 同上 | ["grape"], count=1 |
| 9 | insert("banana") | 同上 | 提示已存在 |

## 扩展方向

### 扩展一：文件加载与保存

```cpp
void loadFromFile(const string& filename) {
    ifstream file(filename);
    string word;
    while (file >> word) {
        words.push_back(word);
    }
    sort(words.begin(), words.end());
    file.close();
}

void saveToFile(const string& filename) const {
    ofstream file(filename);
    for (const string& word : words) {
        file << word << endl;
    }
    file.close();
}
```

### 扩展二：模糊匹配

支持通配符 `*` 匹配：

```cpp
vector<string> fuzzySearch(const string& pattern) const {
    vector<string> result;
    for (const string& word : words) {
        if (matchesPattern(word, pattern)) {
            result.push_back(word);
        }
    }
    return result;
}
```

### 扩展三：按词频排序

增加词频统计，返回最热门的前 N 个结果：

```cpp
class DictionaryWithFrequency {
private:
    vector<string> words;
    unordered_map<string, int> frequency;
    
public:
    void insert(const string& word) {
        int pos = lowerBound(word);
        if (pos < words.size() && words[pos] == word) {
            frequency[word]++;
            return;
        }
        words.insert(words.begin() + pos, word);
        frequency[word] = 1;
    }
    
    vector<string> getTopWords(int n) const {
        vector<pair<string, int>> freqList(frequency.begin(), frequency.end());
        sort(freqList.begin(), freqList.end(), 
             [](const auto& a, const auto& b) { return a.second > b.second; });
        
        vector<string> result;
        for (int i = 0; i < min(n, (int)freqList.size()); i++) {
            result.push_back(freqList[i].first);
        }
        return result;
    }
};
```

### 扩展四：缓存功能

加速频繁查询的前缀：

```cpp
class DictionaryWithCache {
private:
    vector<string> words;
    unordered_map<string, vector<string>> cache;
    
    vector<string> getWordsWithPrefixInternal(const string& prefix) const {
        string endPrefix = prefix + '{';
        int left = lowerBound(prefix);
        int right = lowerBound(endPrefix);
        
        vector<string> result;
        for (int i = left; i < right; i++) {
            result.push_back(words[i]);
        }
        return result;
    }
    
public:
    vector<string> startsWith(const string& prefix) {
        if (cache.find(prefix) != cache.end()) {
            return cache[prefix];
        }
        
        vector<string> result = getWordsWithPrefixInternal(prefix);
        cache[prefix] = result;
        return result;
    }
    
    void insert(const string& word) {
        cache.clear();  // 插入后清空缓存
        // ... 插入逻辑
    }
};
```

### 扩展五：Trie（前缀树）版本对比

```cpp
struct TrieNode {
    bool isEnd;
    TrieNode* children[26];
    TrieNode() : isEnd(false) {
        memset(children, 0, sizeof(children));
    }
};

class Trie {
private:
    TrieNode* root;
    
    void collectWords(TrieNode* node, string prefix, vector<string>& result) const {
        if (node->isEnd) {
            result.push_back(prefix);
        }
        for (int i = 0; i < 26; i++) {
            if (node->children[i]) {
                collectWords(node->children[i], prefix + (char)('a' + i), result);
            }
        }
    }
    
public:
    Trie() : root(new TrieNode()) {}
    
    void insert(const string& word) {
        TrieNode* node = root;
        for (char c : word) {
            int idx = c - 'a';
            if (!node->children[idx]) {
                node->children[idx] = new TrieNode();
            }
            node = node->children[idx];
        }
        node->isEnd = true;
    }
    
    vector<string> startsWith(const string& prefix) const {
        TrieNode* node = root;
        for (char c : prefix) {
            int idx = c - 'a';
            if (!node->children[idx]) {
                return {};
            }
            node = node->children[idx];
        }
        
        vector<string> result;
        collectWords(node, prefix, result);
        return result;
    }
};
```

### 二分查找 vs Trie 对比表

| 对比项 | 二分查找 | Trie |
|--------|---------|------|
| 前缀查询时间 | O(log n + k) | O(k + m) |
| 内存占用 | O(n * L) | O(n * L)（可能更多） |
| 插入时间 | O(n)（数组移动） | O(L) |
| 适合场景 | 静态词典、查询为主 | 动态词典、频繁插入 |
| 实现难度 | 低 | 中 |

其中：n = 单词数量，L = 平均单词长度，k = 查询前缀长度，m = 匹配的单词数量