"""
Resource Service
- generate_resources: 个性化资源生成（Phase 3B: 动态 fallback + LLM 集成）
- 资源库索引读取、详情、搜索、统计 (Phase 4A)
- 用户资源包 CRUD (Phase 4B)
"""
import json
import logging
import random
from pathlib import Path
from typing import Optional

from database import SessionLocal
from models.resource import UserResourcePackage

from services import profile_service

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
LIBRARY_DIR = DATA_DIR / "resource_library"
INDEX_PATH = LIBRARY_DIR / "index.json"

# ═══════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════

ALLOWED_MODULES = {
    '复杂度分析', '线性表', '栈与队列', '递归与调用栈',
    '树与二叉树', '图结构与图算法', '排序与查找',
    '散列表', '动态规划入门', '综合项目实践',
}

ALLOWED_TYPES = {'图解讲解', '代码示例', '易错点', '分层练习', '项目案例'}

ALLOWED_LANGUAGES = {'Python', 'C', 'C++', 'Java'}

# Topic keyword → normalized module
TOPIC_TO_MODULE: dict[str, str] = {
    '复杂度': '复杂度分析', '大O': '复杂度分析', '时间复杂度': '复杂度分析', '空间复杂度': '复杂度分析',
    '线性表': '线性表', '链表': '线性表', '顺序表': '线性表', '数组': '线性表',
    '栈': '栈与队列', '队列': '栈与队列',
    '递归': '递归与调用栈', '调用栈': '递归与调用栈',
    '二叉树': '树与二叉树', '树遍历': '树与二叉树', '二叉搜索树': '树与二叉树', '树的遍历': '树与二叉树',
    '图': '图结构与图算法', 'BFS': '图结构与图算法', 'DFS': '图结构与图算法', '最短路径': '图结构与图算法', '图遍历': '图结构与图算法',
    '排序': '排序与查找', '查找': '排序与查找', '二分查找': '排序与查找', '快速排序': '排序与查找', '归并排序': '排序与查找',
    '散列': '散列表', '哈希': '散列表',
    '动态规划': '动态规划入门', 'DP': '动态规划入门',
    '项目': '综合项目实践', '综合': '综合项目实践',
}

# Resource type → content spec
RESOURCE_TYPE_SPECS: dict[str, dict] = {
    '图解讲解': {
        'section_kinds': ['highlight', 'steps', 'compare', 'complexity', 'text'],
        'min_sections': 3,
        'description': '图文并茂的概念讲解，包含核心要点、分步骤拆解、对比分析',
    },
    '代码示例': {
        'section_kinds': ['code', 'highlight', 'steps', 'text'],
        'min_sections': 2,
        'description': '完整可运行的代码示例，每行有注释，包含测试用例',
    },
    '易错点': {
        'section_kinds': ['warning', 'code', 'compare', 'text'],
        'min_sections': 2,
        'description': '常见错误分析与纠正，包含错误示例和正确写法的对比',
    },
    '分层练习': {
        'section_kinds': ['practice', 'answer_hint', 'text'],
        'min_sections': 3,
        'description': '分层递进练习（基础→进阶→提高），每题含提示',
    },
    '项目案例': {
        'section_kinds': ['task', 'steps', 'code', 'text'],
        'min_sections': 3,
        'description': '完整项目实践案例，分阶段实现，包含代码和说明',
    },
}

# ═══════════════════════════════════════════════════════════════════
# Phase 3B: Core helper functions
# ═══════════════════════════════════════════════════════════════════

def resolve_module_name(topic: str) -> str:
    """Map any topic string to a normalized 10-module name."""
    if not topic:
        return '递归与调用栈'
    for keyword, module in TOPIC_TO_MODULE.items():
        if keyword in topic:
            return module
    return '递归与调用栈'


def normalize_programming_language(lang: str) -> str:
    """Normalize to one of: Python, C, C++, Java. Defaults to Python."""
    if not lang or lang == '暂不确定':
        return 'Python'
    lang_lower = lang.strip().lower()
    if lang_lower in ('python', 'py'):
        return 'Python'
    if lang_lower == 'c':
        return 'C'
    if lang_lower in ('c++', 'cpp', 'cplusplus', 'c＋＋'):
        return 'C++'
    if lang_lower == 'java':
        return 'Java'
    return 'Python'


def get_resource_type_spec(resource_type: str) -> dict:
    """Return stable content template specification for a resource type."""
    return RESOURCE_TYPE_SPECS.get(resource_type, RESOURCE_TYPE_SPECS['图解讲解'])


def build_generation_context(
    course_id: str,
    knowledge_point: str,
    difficulty: str = "入门",
    language: str = "Python",
    resource_types: list[str] | None = None,
    quick_profile: dict | None = None,
) -> dict:
    """Assemble generation_context from all inputs — drives personalization."""
    qp = quick_profile or {}

    effective_types = resource_types if resource_types else ['图解讲解', '代码示例', '分层练习']
    effective_types = [t for t in effective_types if t in ALLOWED_TYPES]
    if not effective_types:
        effective_types = ['图解讲解', '代码示例', '分层练习']

    normalized_lang = normalize_programming_language(
        qp.get('programming_language') or language
    )
    module_name = resolve_module_name(knowledge_point)

    foundation = qp.get('foundation_level', '') or ''
    goal = qp.get('learning_goal', '') or ''
    difficulties = qp.get('current_difficulties', []) or []
    prefs = qp.get('expression_preferences', []) or []

    has_profile = bool(foundation or goal or difficulties or prefs)

    signature_parts = [
        module_name,
        '|'.join(sorted(effective_types)),
        normalized_lang,
        goal or '未指定目标',
        foundation or '未指定基础',
    ]

    return {
        'topic': knowledge_point,
        'course_id': course_id,
        'module': module_name,
        'difficulty': difficulty,
        'language': language,
        'normalized_language': normalized_lang,
        'resource_types': effective_types,
        'foundation_level': foundation,
        'learning_goal': goal,
        'current_difficulties': difficulties,
        'expression_preferences': prefs,
        'has_profile': has_profile,
        'generation_signature': '|'.join(signature_parts),
        'personalization_source': 'quick_profile' if has_profile else 'defaults',
    }


# ═══════════════════════════════════════════════════════════════════
# Language-specific code templates (per topic)
# ═══════════════════════════════════════════════════════════════════

def build_language_specific_code_example(topic: str, language: str) -> dict | None:
    """
    Build a {'code': str, 'language': str, 'heading': str} dict
    with topic-and-language-specific code. Returns None for non-code topics.
    """
    module = resolve_module_name(topic)
    lang = normalize_programming_language(language)

    templates = _CODE_TEMPLATES.get(module, {})
    code = templates.get(lang, '')
    if not code:
        code = templates.get('Python', '# 示例代码\npass')

    headings = {
        '复杂度分析': f'时间复杂度示例（{lang}）',
        '线性表': f'线性表操作示例（{lang}）',
        '栈与队列': f'栈与队列实现（{lang}）',
        '递归与调用栈': f'递归函数示例（{lang}）',
        '树与二叉树': f'二叉树遍历实现（{lang}）',
        '图结构与图算法': f'图的遍历实现（{lang}）',
        '排序与查找': f'排序与查找算法（{lang}）',
        '散列表': f'散列表操作示例（{lang}）',
        '动态规划入门': f'动态规划示例（{lang}）',
        '综合项目实践': f'综合项目代码（{lang}）',
    }

    return {
        'code': code.strip(),
        'language': lang,
        'heading': headings.get(module, f'代码示例（{lang}）'),
    }


_CODE_TEMPLATES: dict[str, dict[str, str]] = {
    '复杂度分析': {
        'Python': '''import time

def o1_example(arr):
    """O(1) — 常数时间：直接访问索引"""
    return arr[0] if arr else None

def on_example(arr):
    """O(n) — 线性时间：遍历数组"""
    total = 0
    for x in arr:
        total += x
    return total

def on2_example(arr):
    """O(n²) — 平方时间：双重循环"""
    n = len(arr)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((arr[i], arr[j]))
    return pairs

# 测试
if __name__ == '__main__':
    data = list(range(1000))
    t0 = time.time(); o1_example(data); t1 = time.time()
    print(f"O(1) 耗时: {(t1-t0)*1e6:.1f} μs")''',
        'C': '''#include <stdio.h>
#include <time.h>

// O(1) — 常数时间
int get_first(int arr[], int n) { return n > 0 ? arr[0] : -1; }

// O(n) — 线性时间
int sum_all(int arr[], int n) {
    int total = 0;
    for (int i = 0; i < n; i++) total += arr[i];
    return total;
}

// O(n²) — 平方时间
void print_pairs(int arr[], int n) {
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            printf("(%d, %d)\\n", arr[i], arr[j]);
}''',
        'C++': '''#include <iostream>
#include <vector>
#include <chrono>
using namespace std;

// O(1) — 常数时间
int get_first(const vector<int>& arr) { return arr.empty() ? -1 : arr[0]; }

// O(n) — 线性时间
int sum_all(const vector<int>& arr) {
    int total = 0;
    for (int x : arr) total += x;
    return total;
}

// O(n²) — 平方时间
void print_pairs(const vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            cout << "(" << arr[i] << ", " << arr[j] << ")" << endl;
}''',
        'Java': '''import java.util.*;

public class ComplexityDemo {
    // O(1) — 常数时间
    static int getFirst(int[] arr) { return arr.length > 0 ? arr[0] : -1; }

    // O(n) — 线性时间
    static int sumAll(int[] arr) {
        int total = 0;
        for (int x : arr) total += x;
        return total;
    }

    // O(n²) — 平方时间
    static void printPairs(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++)
                System.out.printf("(%d, %d)%n", arr[i], arr[j]);
    }
}''',
    },
    '线性表': {
        'Python': '''class ListNode:
    """单链表节点"""
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, val):
        """尾部插入 — O(n)"""
        node = ListNode(val)
        if not self.head:
            self.head = node
            return
        cur = self.head
        while cur.next:
            cur = cur.next
        cur.next = node

    def prepend(self, val):
        """头部插入 — O(1)"""
        self.head = ListNode(val, self.head)

    def delete(self, val):
        """删除第一个值为 val 的节点 — O(n)"""
        if not self.head:
            return
        if self.head.val == val:
            self.head = self.head.next
            return
        cur = self.head
        while cur.next and cur.next.val != val:
            cur = cur.next
        if cur.next:
            cur.next = cur.next.next

    def to_list(self):
        result = []
        cur = self.head
        while cur:
            result.append(cur.val)
            cur = cur.next
        return result

# 测试
ll = LinkedList()
ll.append(1); ll.append(2); ll.prepend(0)
print(ll.to_list())  # [0, 1, 2]''',
        'C': '''#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int val;
    struct Node* next;
} Node;

Node* create_node(int val) {
    Node* n = (Node*)malloc(sizeof(Node));
    n->val = val; n->next = NULL;
    return n;
}

void append(Node** head, int val) {
    Node* n = create_node(val);
    if (!*head) { *head = n; return; }
    Node* cur = *head;
    while (cur->next) cur = cur->next;
    cur->next = n;
}

void prepend(Node** head, int val) {
    Node* n = create_node(val);
    n->next = *head;
    *head = n;
}

void print_list(Node* head) {
    for (Node* cur = head; cur; cur = cur->next)
        printf("%d ", cur->val);
    printf("\\n");
}''',
        'C++': '''#include <iostream>
using namespace std;

struct ListNode {
    int val;
    ListNode* next;
    ListNode(int v = 0, ListNode* n = nullptr) : val(v), next(n) {}
};

class LinkedList {
public:
    ListNode* head = nullptr;

    void append(int val) {
        auto* n = new ListNode(val);
        if (!head) { head = n; return; }
        ListNode* cur = head;
        while (cur->next) cur = cur->next;
        cur->next = n;
    }

    void prepend(int val) { head = new ListNode(val, head); }

    void print() {
        for (auto* cur = head; cur; cur = cur->next)
            cout << cur->val << " ";
        cout << endl;
    }
};''',
        'Java': '''class ListNode {
    int val;
    ListNode next;
    ListNode(int v) { val = v; }
}

class LinkedList {
    ListNode head;

    void append(int val) {
        ListNode n = new ListNode(val);
        if (head == null) { head = n; return; }
        ListNode cur = head;
        while (cur.next != null) cur = cur.next;
        cur.next = n;
    }

    void prepend(int val) {
        ListNode n = new ListNode(val);
        n.next = head;
        head = n;
    }

    void print() {
        for (ListNode cur = head; cur != null; cur = cur.next)
            System.out.print(cur.val + " ");
        System.out.println();
    }
}''',
    },
    '栈与队列': {
        'Python': '''from collections import deque

# === 栈（Stack）— LIFO ===
stack = []
stack.append('a')   # push
stack.append('b')
print(stack.pop())  # 'b' — 后进先出
print(stack[-1])    # 'a' — peek 栈顶

# === 队列（Queue）— FIFO ===
queue = deque()
queue.append('x')   # enqueue
queue.append('y')
print(queue.popleft())  # 'x' — 先进先出
print(queue[0])         # 'y' — peek 队首

# === 应用：括号匹配 ===
def is_valid(s):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif not stack or stack.pop() != pairs[ch]:
            return False
    return len(stack) == 0

print(is_valid("()[]{}"))  # True
print(is_valid("([)]"))    # False''',
        'C': '''#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX 100

// 栈
typedef struct { int data[MAX]; int top; } Stack;
void push(Stack* s, int v) { if (s->top < MAX) s->data[++(s->top)] = v; }
int pop(Stack* s) { return s->top >= 0 ? s->data[(s->top)--] : -1; }

// 队列（循环队列）
typedef struct { int data[MAX]; int front, rear; } Queue;
void enqueue(Queue* q, int v) { q->data[q->rear++] = v; }
int dequeue(Queue* q) { return q->front < q->rear ? q->data[q->front++] : -1; }

// 括号匹配
bool is_valid(const char* s) {
    char stack[MAX]; int top = -1;
    for (int i = 0; s[i]; i++) {
        if (s[i] == '(' || s[i] == '[' || s[i] == '{')
            stack[++top] = s[i];
        else {
            if (top < 0) return false;
            char c = stack[top--];
            if ((s[i] == ')' && c != '(') ||
                (s[i] == ']' && c != '[') ||
                (s[i] == '}' && c != '{')) return false;
        }
    }
    return top < 0;
}''',
        'C++': '''#include <iostream>
#include <stack>
#include <queue>
using namespace std;

bool isValid(const string& s) {
    stack<char> st;
    for (char ch : s) {
        if (ch == '(' || ch == '[' || ch == '{') {
            st.push(ch);
        } else {
            if (st.empty()) return false;
            char top = st.top(); st.pop();
            if ((ch == ')' && top != '(') ||
                (ch == ']' && top != '[') ||
                (ch == '}' && top != '{')) return false;
        }
    }
    return st.empty();
}

int main() {
    // 栈
    stack<int> st;
    st.push(1); st.push(2);
    cout << st.top() << endl; st.pop();  // 2

    // 队列
    queue<int> q;
    q.push(10); q.push(20);
    cout << q.front() << endl; q.pop();  // 10

    cout << isValid("()[]{}") << endl;  // 1
    return 0;
}''',
        'Java': '''import java.util.*;

public class StackQueueDemo {
    static boolean isValid(String s) {
        Deque<Character> stack = new ArrayDeque<>();
        for (char ch : s.toCharArray()) {
            if (ch == '(' || ch == '[' || ch == '{') {
                stack.push(ch);
            } else {
                if (stack.isEmpty()) return false;
                char top = stack.pop();
                if ((ch == ')' && top != '(') ||
                    (ch == ']' && top != '[') ||
                    (ch == '}' && top != '{')) return false;
            }
        }
        return stack.isEmpty();
    }

    public static void main(String[] args) {
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(1); stack.push(2);
        System.out.println(stack.pop());  // 2

        Queue<Integer> queue = new LinkedList<>();
        queue.offer(10); queue.offer(20);
        System.out.println(queue.poll());  // 10

        System.out.println(isValid("()[]{}"));  // true
    }
}''',
    },
    '递归与调用栈': {
        'Python': '''def factorial(n):
    """阶乘：n! = n × (n-1)! — 基准 n ≤ 1"""
    if n <= 1:          # 基准情形（递归出口）
        return 1
    return n * factorial(n - 1)  # 递归情形

def fibonacci(n):
    """斐波那契：F(n) = F(n-1) + F(n-2) — 双分支递归"""
    if n <= 1:          # 基准情形
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# 记忆化优化
def fibonacci_memo(n, memo=None):
    if memo is None:
        memo = {}
    if n <= 1:
        return n
    if n not in memo:
        memo[n] = fibonacci_memo(n - 1, memo) + fibonacci_memo(n - 2, memo)
    return memo[n]

print("5! =", factorial(5))           # 120
print("fib(10) =", fibonacci_memo(10)) # 55''',
        'C': '''#include <stdio.h>

// 阶乘 — 递归版
int factorial(int n) {
    if (n <= 1) return 1;          // 基准情形
    return n * factorial(n - 1);   // 递归情形
}

// 斐波那契 — 递归版（有重复计算）
int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

// 记忆化搜索
int memo[100] = {0};
int fib_memo(int n) {
    if (n <= 1) return n;
    if (memo[n]) return memo[n];
    return memo[n] = fib_memo(n - 1) + fib_memo(n - 2);
}

int main() {
    printf("5! = %d\\n", factorial(5));     // 120
    printf("fib(10) = %d\\n", fib_memo(10)); // 55
    return 0;
}''',
        'C++': '''#include <iostream>
#include <unordered_map>
using namespace std;

// 阶乘
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// 记忆化斐波那契
long long fib_memo(int n, unordered_map<int, long long>& memo) {
    if (n <= 1) return n;
    if (memo.count(n)) return memo[n];
    return memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo);
}

int main() {
    cout << "5! = " << factorial(5) << endl;
    unordered_map<int, long long> m;
    cout << "fib(50) = " << fib_memo(50, m) << endl;
    return 0;
}''',
        'Java': '''import java.util.*;

public class RecursionDemo {
    static int factorial(int n) {
        if (n <= 1) return 1;          // 基准情形
        return n * factorial(n - 1);   // 递归情形
    }

    static long fibMemo(int n, Map<Integer, Long> memo) {
        if (n <= 1) return n;
        if (memo.containsKey(n)) return memo.get(n);
        long val = fibMemo(n - 1, memo) + fibMemo(n - 2, memo);
        memo.put(n, val);
        return val;
    }

    public static void main(String[] args) {
        System.out.println("5! = " + factorial(5));     // 120
        Map<Integer, Long> m = new HashMap<>();
        System.out.println("fib(50) = " + fibMemo(50, m));
    }
}''',
    },
    '树与二叉树': {
        'Python': '''class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# 前序：根→左→右
def preorder(root):
    if root is None: return []
    return [root.val] + preorder(root.left) + preorder(root.right)

# 中序：左→根→右
def inorder(root):
    if root is None: return []
    return inorder(root.left) + [root.val] + inorder(root.right)

# 后序：左→右→根
def postorder(root):
    if root is None: return []
    return postorder(root.left) + postorder(root.right) + [root.val]

# 层序（BFS）
from collections import deque
def levelorder(root):
    if root is None: return []
    result, q = [], deque([root])
    while q:
        node = q.popleft()
        result.append(node.val)
        if node.left: q.append(node.left)
        if node.right: q.append(node.right)
    return result

# 测试
tree = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3))
print("前序:", preorder(tree))   # [1, 2, 4, 5, 3]
print("中序:", inorder(tree))    # [4, 2, 5, 1, 3]
print("后序:", postorder(tree))  # [4, 5, 2, 3, 1]
print("层序:", levelorder(tree)) # [1, 2, 3, 4, 5]''',
        'C': '''#include <stdio.h>
#include <stdlib.h>

typedef struct TreeNode {
    int val;
    struct TreeNode *left, *right;
} TreeNode;

TreeNode* new_node(int v) {
    TreeNode* n = malloc(sizeof(TreeNode));
    n->val = v; n->left = n->right = NULL;
    return n;
}

void preorder(TreeNode* root) {
    if (!root) return;
    printf("%d ", root->val);
    preorder(root->left);
    preorder(root->right);
}

void inorder(TreeNode* root) {
    if (!root) return;
    inorder(root->left);
    printf("%d ", root->val);
    inorder(root->right);
}

void postorder(TreeNode* root) {
    if (!root) return;
    postorder(root->left);
    postorder(root->right);
    printf("%d ", root->val);
}

int main() {
    TreeNode* root = new_node(1);
    root->left = new_node(2); root->right = new_node(3);
    root->left->left = new_node(4); root->left->right = new_node(5);

    printf("前序: "); preorder(root); printf("\\n");
    printf("中序: "); inorder(root); printf("\\n");
    printf("后序: "); postorder(root); printf("\\n");
    return 0;
}''',
        'C++': '''#include <iostream>
#include <queue>
using namespace std;

struct TreeNode {
    int val;
    TreeNode *left, *right;
    TreeNode(int v = 0, TreeNode* l = nullptr, TreeNode* r = nullptr)
        : val(v), left(l), right(r) {}
};

void preorder(TreeNode* root) {
    if (!root) return;
    cout << root->val << " ";
    preorder(root->left);
    preorder(root->right);
}

void inorder(TreeNode* root) {
    if (!root) return;
    inorder(root->left);
    cout << root->val << " ";
    inorder(root->right);
}

void levelorder(TreeNode* root) {
    if (!root) return;
    queue<TreeNode*> q;
    q.push(root);
    while (!q.empty()) {
        auto* n = q.front(); q.pop();
        cout << n->val << " ";
        if (n->left) q.push(n->left);
        if (n->right) q.push(n->right);
    }
}

int main() {
    auto* root = new TreeNode(1,
        new TreeNode(2, new TreeNode(4), new TreeNode(5)),
        new TreeNode(3));

    cout << "前序: "; preorder(root); cout << endl;
    cout << "中序: "; inorder(root); cout << endl;
    cout << "层序: "; levelorder(root); cout << endl;
    return 0;
}''',
        'Java': '''import java.util.*;

class TreeNode {
    int val;
    TreeNode left, right;
    TreeNode(int v) { val = v; }
}

public class TreeTraversal {
    static List<Integer> preorder(TreeNode root) {
        if (root == null) return new ArrayList<>();
        List<Integer> res = new ArrayList<>();
        res.add(root.val);
        res.addAll(preorder(root.left));
        res.addAll(preorder(root.right));
        return res;
    }

    static List<Integer> inorder(TreeNode root) {
        if (root == null) return new ArrayList<>();
        List<Integer> res = new ArrayList<>(inorder(root.left));
        res.add(root.val);
        res.addAll(inorder(root.right));
        return res;
    }

    static List<Integer> levelorder(TreeNode root) {
        List<Integer> res = new ArrayList<>();
        if (root == null) return res;
        Queue<TreeNode> q = new LinkedList<>();
        q.offer(root);
        while (!q.isEmpty()) {
            TreeNode n = q.poll();
            res.add(n.val);
            if (n.left != null) q.offer(n.left);
            if (n.right != null) q.offer(n.right);
        }
        return res;
    }

    public static void main(String[] args) {
        TreeNode root = new TreeNode(1);
        root.left = new TreeNode(2); root.right = new TreeNode(3);
        root.left.left = new TreeNode(4); root.left.right = new TreeNode(5);

        System.out.println("前序: " + preorder(root));
        System.out.println("中序: " + inorder(root));
        System.out.println("层序: " + levelorder(root));
    }
}''',
    },
    '图结构与图算法': {
        'Python': '''from collections import deque

def bfs(graph, start):
    """广度优先搜索 — 队列实现"""
    visited = set([start])
    queue = deque([start])
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order

def dfs(graph, start, visited=None, order=None):
    """深度优先搜索 — 递归实现"""
    if visited is None:
        visited = set()
    if order is None:
        order = []
    visited.add(start)
    order.append(start)
    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            dfs(graph, neighbor, visited, order)
    return order

# 示例图（邻接表）
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E'],
}

print("BFS:", bfs(graph, 'A'))  # A B C D E F
print("DFS:", dfs(graph, 'A'))  # A B D E F C''',
        'C': '''#include <stdio.h>
#include <stdbool.h>
#define N 100

int graph[N][N]; // 邻接矩阵
bool visited[N];

void dfs_matrix(int v, int n) {
    visited[v] = true;
    printf("%d ", v);
    for (int i = 0; i < n; i++)
        if (graph[v][i] && !visited[i])
            dfs_matrix(i, n);
}

void bfs_matrix(int start, int n) {
    bool vis[N] = {false};
    int queue[N], front = 0, rear = 0;
    vis[start] = true;
    queue[rear++] = start;
    while (front < rear) {
        int v = queue[front++];
        printf("%d ", v);
        for (int i = 0; i < n; i++)
            if (graph[v][i] && !vis[i]) {
                vis[i] = true;
                queue[rear++] = i;
            }
    }
}''',
        'C++': '''#include <iostream>
#include <vector>
#include <queue>
using namespace std;

void dfs(int v, const vector<vector<int>>& adj, vector<bool>& visited) {
    visited[v] = true;
    cout << v << " ";
    for (int u : adj[v])
        if (!visited[u])
            dfs(u, adj, visited);
}

void bfs(int start, const vector<vector<int>>& adj) {
    vector<bool> visited(adj.size(), false);
    queue<int> q;
    visited[start] = true;
    q.push(start);
    while (!q.empty()) {
        int v = q.front(); q.pop();
        cout << v << " ";
        for (int u : adj[v])
            if (!visited[u]) {
                visited[u] = true;
                q.push(u);
            }
    }
}

int main() {
    int n = 6;
    vector<vector<int>> adj(n);
    adj[0] = {1, 2}; adj[1] = {0, 3, 4}; adj[2] = {0, 5};
    adj[3] = {1}; adj[4] = {1, 5}; adj[5] = {2, 4};

    cout << "DFS: "; vector<bool> vis(n, false);
    dfs(0, adj, vis); cout << endl;
    cout << "BFS: "; bfs(0, adj); cout << endl;
    return 0;
}''',
        'Java': '''import java.util.*;

public class GraphTraversal {
    static void dfs(int v, List<List<Integer>> adj, boolean[] visited, List<Integer> order) {
        visited[v] = true;
        order.add(v);
        for (int u : adj.get(v))
            if (!visited[u])
                dfs(u, adj, visited, order);
    }

    static List<Integer> bfs(int start, List<List<Integer>> adj) {
        List<Integer> order = new ArrayList<>();
        boolean[] visited = new boolean[adj.size()];
        Queue<Integer> q = new LinkedList<>();
        visited[start] = true;
        q.offer(start);
        while (!q.isEmpty()) {
            int v = q.poll();
            order.add(v);
            for (int u : adj.get(v))
                if (!visited[u]) {
                    visited[u] = true;
                    q.offer(u);
                }
        }
        return order;
    }

    public static void main(String[] args) {
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < 6; i++) adj.add(new ArrayList<>());
        adj.get(0).addAll(Arrays.asList(1, 2));
        adj.get(1).addAll(Arrays.asList(0, 3, 4));
        adj.get(2).addAll(Arrays.asList(0, 5));
        adj.get(3).add(1); adj.get(4).addAll(Arrays.asList(1, 5));
        adj.get(5).addAll(Arrays.asList(2, 4));

        List<Integer> dfsOrder = new ArrayList<>();
        dfs(0, adj, new boolean[6], dfsOrder);
        System.out.println("DFS: " + dfsOrder);
        System.out.println("BFS: " + bfs(0, adj));
    }
}''',
    },
    '排序与查找': {
        'Python': '''def binary_search(arr, target):
    """二分查找 — O(log n)，要求数组有序"""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def quicksort(arr):
    """快速排序 — O(n log n) 平均"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

# 测试
data = [3, 6, 8, 10, 1, 2, 1]
sorted_data = quicksort(data)
print("排序后:", sorted_data)                      # [1, 1, 2, 3, 6, 8, 10]
print("查找 6 的索引:", binary_search(sorted_data, 6))  # 4''',
        'C': '''#include <stdio.h>

// 二分查找
int binary_search(int arr[], int n, int target) {
    int left = 0, right = n - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}

// 快速排序分区
int partition(int arr[], int low, int high) {
    int pivot = arr[high], i = low - 1;
    for (int j = low; j < high; j++)
        if (arr[j] <= pivot) { i++; int t = arr[i]; arr[i] = arr[j]; arr[j] = t; }
    int t = arr[i + 1]; arr[i + 1] = arr[high]; arr[high] = t;
    return i + 1;
}

void quicksort(int arr[], int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quicksort(arr, low, pi - 1);
        quicksort(arr, pi + 1, high);
    }
}''',
        'C++': '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int binary_search_cpp(const vector<int>& arr, int target) {
    int left = 0, right = arr.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}

void quicksort(vector<int>& arr, int low, int high) {
    if (low >= high) return;
    int pivot = arr[(low + high) / 2], i = low, j = high;
    while (i <= j) {
        while (arr[i] < pivot) i++;
        while (arr[j] > pivot) j--;
        if (i <= j) swap(arr[i++], arr[j--]);
    }
    quicksort(arr, low, j);
    quicksort(arr, i, high);
}''',
        'Java': '''import java.util.Arrays;

public class SortSearchDemo {
    static int binarySearch(int[] arr, int target) {
        int left = 0, right = arr.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) return mid;
            else if (arr[mid] < target) left = mid + 1;
            else right = mid - 1;
        }
        return -1;
    }

    static void quicksort(int[] arr, int low, int high) {
        if (low >= high) return;
        int pivot = arr[(low + high) / 2], i = low, j = high;
        while (i <= j) {
            while (arr[i] < pivot) i++;
            while (arr[j] > pivot) j--;
            if (i <= j) { int t = arr[i]; arr[i] = arr[j]; arr[j] = t; i++; j--; }
        }
        quicksort(arr, low, j);
        quicksort(arr, i, high);
    }

    public static void main(String[] args) {
        int[] data = {3, 6, 8, 10, 1, 2, 1};
        quicksort(data, 0, data.length - 1);
        System.out.println("排序后: " + Arrays.toString(data));
        System.out.println("查找 6: " + binarySearch(data, 6));
    }
}''',
    },
    '散列表': {
        'Python': '''# Python dict 就是散列表实现
# 演示：字符频率统计

def char_frequency(s):
    """统计字符串中每个字符的出现次数"""
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    return freq

# 演示：两数之和
def two_sum(nums, target):
    """在数组中找到两个数，使其和为 target"""
    seen = {}  # value → index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# 处理冲突：链地址法示意
class SimpleHashTable:
    def __init__(self, size=10):
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        return hash(key) % self.size

    def put(self, key, value):
        bucket = self.table[self._hash(key)]
        for i, (k, v) in enumerate(bucket):
            if k == key: bucket[i] = (key, value); return
        bucket.append((key, value))

    def get(self, key):
        for k, v in self.table[self._hash(key)]:
            if k == key: return v
        return None

print(char_frequency("hello"))      # {'h':1,'e':1,'l':2,'o':1}
print(two_sum([2, 7, 11, 15], 9))  # [0, 1]''',
        'C': '''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define SIZE 10

typedef struct Entry {
    char* key; int value; struct Entry* next;
} Entry;

Entry* table[SIZE] = {NULL};

int hash_func(const char* key) {
    int h = 0;
    while (*key) h = (h * 31 + *key++) % SIZE;
    return h;
}

void put(const char* key, int value) {
    int idx = hash_func(key);
    Entry* e = table[idx];
    while (e) { if (strcmp(e->key, key) == 0) { e->value = value; return; } e = e->next; }
    Entry* n = malloc(sizeof(Entry));
    n->key = strdup(key); n->value = value;
    n->next = table[idx]; table[idx] = n;
}

int get(const char* key) {
    Entry* e = table[hash_func(key)];
    while (e) { if (strcmp(e->key, key) == 0) return e->value; e = e->next; }
    return -1;
}''',
        'C++': '''#include <iostream>
#include <unordered_map>
#include <vector>
using namespace std;

vector<int> twoSum(const vector<int>& nums, int target) {
    unordered_map<int, int> seen;  // value → index
    for (int i = 0; i < (int)nums.size(); i++) {
        int complement = target - nums[i];
        if (seen.count(complement))
            return {seen[complement], i};
        seen[nums[i]] = i;
    }
    return {};
}

int main() {
    unordered_map<char, int> freq;
    for (char ch : string("hello"))
        freq[ch]++;

    for (auto& [ch, count] : freq)
        cout << ch << ": " << count << endl;

    auto res = twoSum({2, 7, 11, 15}, 9);
    cout << "[" << res[0] << ", " << res[1] << "]" << endl;
    return 0;
}''',
        'Java': '''import java.util.*;

public class HashMapDemo {
    static int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> seen = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (seen.containsKey(complement))
                return new int[]{seen.get(complement), i};
            seen.put(nums[i], i);
        }
        return new int[]{};
    }

    public static void main(String[] args) {
        Map<Character, Integer> freq = new HashMap<>();
        for (char ch : "hello".toCharArray())
            freq.put(ch, freq.getOrDefault(ch, 0) + 1);
        System.out.println(freq);  // {h=1, e=1, l=2, o=1}

        int[] res = twoSum(new int[]{2, 7, 11, 15}, 9);
        System.out.println(Arrays.toString(res));  // [0, 1]
    }
}''',
    },
    '动态规划入门': {
        'Python': '''# === 斐波那契：自底向上 DP ===
def fib_dp(n):
    if n <= 1: return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

# === 0/1 背包问题 ===
def knapsack(values, weights, capacity):
    """dp[i][w] = 前 i 件物品，容量 w 的最大价值"""
    n = len(values)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(
                    dp[i - 1][w],  # 不选第 i 件
                    dp[i - 1][w - weights[i - 1]] + values[i - 1]  # 选
                )
            else:
                dp[i][w] = dp[i - 1][w]
    return dp[n][capacity]

print("fib(10) =", fib_dp(10))                            # 55
print("背包最大价值:", knapsack([60, 100, 120], [10, 20, 30], 50))  # 220''',
        'C': '''#include <stdio.h>

int max(int a, int b) { return a > b ? a : b; }

int fib_dp(int n) {
    if (n <= 1) return n;
    int dp[n + 1]; dp[0] = 0; dp[1] = 1;
    for (int i = 2; i <= n; i++)
        dp[i] = dp[i - 1] + dp[i - 2];
    return dp[n];
}

int knapsack(int v[], int w[], int n, int cap) {
    int dp[n + 1][cap + 1];
    for (int i = 0; i <= n; i++) dp[i][0] = 0;
    for (int j = 0; j <= cap; j++) dp[0][j] = 0;
    for (int i = 1; i <= n; i++)
        for (int j = 1; j <= cap; j++)
            if (w[i - 1] <= j)
                dp[i][j] = max(dp[i - 1][j], dp[i - 1][j - w[i - 1]] + v[i - 1]);
            else
                dp[i][j] = dp[i - 1][j];
    return dp[n][cap];
}''',
        'C++': '''#include <iostream>
#include <vector>
using namespace std;

int fib_dp(int n) {
    if (n <= 1) return n;
    vector<int> dp(n + 1);
    dp[0] = 0; dp[1] = 1;
    for (int i = 2; i <= n; i++)
        dp[i] = dp[i - 1] + dp[i - 2];
    return dp[n];
}

int knapsack(const vector<int>& v, const vector<int>& w, int cap) {
    int n = v.size();
    vector<vector<int>> dp(n + 1, vector<int>(cap + 1, 0));
    for (int i = 1; i <= n; i++)
        for (int j = 1; j <= cap; j++)
            if (w[i - 1] <= j)
                dp[i][j] = max(dp[i - 1][j], dp[i - 1][j - w[i - 1]] + v[i - 1]);
            else
                dp[i][j] = dp[i - 1][j];
    return dp[n][cap];
}

int main() {
    cout << "fib(10) = " << fib_dp(10) << endl;  // 55
    vector<int> v = {60, 100, 120}, w = {10, 20, 30};
    cout << "背包最大价值: " << knapsack(v, w, 50) << endl;  // 220
    return 0;
}''',
        'Java': '''import java.util.*;

public class DPDemo {
    static int fibDP(int n) {
        if (n <= 1) return n;
        int[] dp = new int[n + 1];
        dp[0] = 0; dp[1] = 1;
        for (int i = 2; i <= n; i++)
            dp[i] = dp[i - 1] + dp[i - 2];
        return dp[n];
    }

    static int knapsack(int[] v, int[] w, int cap) {
        int n = v.length;
        int[][] dp = new int[n + 1][cap + 1];
        for (int i = 1; i <= n; i++)
            for (int j = 1; j <= cap; j++)
                if (w[i - 1] <= j)
                    dp[i][j] = Math.max(dp[i - 1][j], dp[i - 1][j - w[i - 1]] + v[i - 1]);
                else
                    dp[i][j] = dp[i - 1][j];
        return dp[n][cap];
    }

    public static void main(String[] args) {
        System.out.println("fib(10) = " + fibDP(10));  // 55
        int[] v = {60, 100, 120}, w = {10, 20, 30};
        System.out.println("背包最大价值: " + knapsack(v, w, 50));  // 220
    }
}''',
    },
    '综合项目实践': {
        'Python': '''# 综合项目：简单的学生成绩管理系统
# 综合运用：线性表（列表）、排序、查找、散列表

class StudentManager:
    def __init__(self):
        self.students = []  # 线性表存储学生列表

    def add(self, name, score):
        self.students.append({'name': name, 'score': score})

    def remove(self, name):
        self.students = [s for s in self.students if s['name'] != name]

    def get_score(self, name):
        """散列表思想：O(1) 查找需要额外索引"""
        for s in self.students:
            if s['name'] == name:
                return s['score']
        return None

    def rank(self):
        """按成绩排序 — 使用内置排序"""
        return sorted(self.students, key=lambda s: s['score'], reverse=True)

    def stats(self):
        scores = [s['score'] for s in self.students]
        if not scores: return {}
        return {
            '平均分': sum(scores) / len(scores),
            '最高分': max(scores),
            '最低分': min(scores),
        }

# 测试
sm = StudentManager()
sm.add('Alice', 85); sm.add('Bob', 92); sm.add('Carol', 78)
print("排名:", [(s['name'], s['score']) for s in sm.rank()])
print("统计:", sm.stats())''',
        'C': '''#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX 100

typedef struct { char name[32]; int score; } Student;

Student students[MAX];
int count = 0;

void add(const char* name, int score) {
    strcpy(students[count].name, name);
    students[count++].score = score;
}

int cmp(const void* a, const void* b) {
    return ((Student*)b)->score - ((Student*)a)->score;
}

void rank_all() {
    qsort(students, count, sizeof(Student), cmp);
    for (int i = 0; i < count; i++)
        printf("%d. %s: %d\\n", i + 1, students[i].name, students[i].score);
}

int main() {
    add("Alice", 85); add("Bob", 92); add("Carol", 78);
    rank_all();
    return 0;
}''',
        'C++': '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

struct Student { string name; int score; };

class StudentManager {
    vector<Student> students;
public:
    void add(const string& name, int score) { students.push_back({name, score}); }
    void rank_all() {
        sort(students.begin(), students.end(),
             [](auto& a, auto& b) { return a.score > b.score; });
        for (int i = 0; i < (int)students.size(); i++)
            cout << i + 1 << ". " << students[i].name << ": " << students[i].score << endl;
    }
    double avg() {
        double sum = 0;
        for (auto& s : students) sum += s.score;
        return students.empty() ? 0 : sum / students.size();
    }
};

int main() {
    StudentManager sm;
    sm.add("Alice", 85); sm.add("Bob", 92); sm.add("Carol", 78);
    sm.rank_all();
    cout << "平均分: " << sm.avg() << endl;
    return 0;
}''',
        'Java': '''import java.util.*;

class Student {
    String name; int score;
    Student(String n, int s) { name = n; score = s; }
}

public class StudentManager {
    List<Student> students = new ArrayList<>();

    void add(String name, int score) { students.add(new Student(name, score)); }

    void rankAll() {
        students.sort((a, b) -> Integer.compare(b.score, a.score));
        for (int i = 0; i < students.size(); i++)
            System.out.printf("%d. %s: %d%n", i + 1, students.get(i).name, students.get(i).score);
    }

    double avg() {
        return students.stream().mapToInt(s -> s.score).average().orElse(0);
    }

    public static void main(String[] args) {
        StudentManager sm = new StudentManager();
        sm.add("Alice", 85); sm.add("Bob", 92); sm.add("Carol", 78);
        sm.rankAll();
        System.out.println("平均分: " + sm.avg());
    }
}''',
    },
}


# ═══════════════════════════════════════════════════════════════════
# Phase 3B: Dynamic fallback generation
# ═══════════════════════════════════════════════════════════════════

def _topic_display_name(topic: str) -> str:
    """Extract a clean display name for the topic."""
    return topic.strip()


def _build_type_sections(resource_type: str, module: str, topic: str, lang: str) -> list[dict]:
    """Build type-specific, topic-aware sections for fallback resources."""
    display = _topic_display_name(topic)
    code_info = build_language_specific_code_example(topic, lang)

    if resource_type == '图解讲解':
        sections = [
            {'kind': 'highlight', 'heading': f'{display} — 核心要点',
             'content': f'围绕"{display}"的核心概念与基本原理展开讲解。内容根据学习者的基础水平和学习目标动态调整深度和侧重点。'},
            {'kind': 'steps', 'heading': '理解步骤',
             'steps': [
                 f'第一步：理解{display}的基本定义和核心思想',
                 f'第二步：通过具体示例观察{display}的执行过程',
                 f'第三步：手动模拟{display}的关键步骤',
                 f'第四步：总结{display}的适用场景和局限性',
             ]},
            {'kind': 'compare', 'heading': '对比分析',
             'content': f'将{display}与相关概念进行对比，突出其独特之处和适用条件。理解"什么时候用"比"怎么用"更重要。'},
            {'kind': 'complexity', 'heading': '复杂度特征',
             'content': f'分析{display}的时间复杂度和空间复杂度特征，说明最优、最差和平均情况下的表现。'},
        ]
        if code_info:
            sections.insert(2, {'kind': 'code', 'heading': code_info['heading'],
                                'content': code_info['code'], 'language': code_info['language']})

    elif resource_type == '代码示例':
        sections = [
            {'kind': 'highlight', 'heading': f'{display} — 代码概览',
             'content': f'以下代码展示了{display}的完整{lang}实现。每行附有详细注释，建议先通读一遍，再逐行理解。'},
        ]
        if code_info:
            sections.append({'kind': 'code', 'heading': code_info['heading'],
                             'content': code_info['code'], 'language': code_info['language']})
        sections.append({'kind': 'steps', 'heading': '代码阅读指南',
                         'steps': [
                             '第1步：先找到函数入口和返回值',
                             '第2步：理解核心数据结构（变量、数组、指针等）',
                             '第3步：追踪关键循环或递归的执行流程',
                             '第4步：修改参数观察输出变化',
                         ]})

    elif resource_type == '易错点':
        sections = [
            {'kind': 'warning', 'heading': f'易错点 1：{display}中的常见陷阱',
             'content': f'许多学习者在{display}上容易犯的错误包括：边界条件遗漏、循环终止条件错误、忽略特殊情况（如空输入）。务必在使用前检查这些边界。'},
            {'kind': 'compare', 'heading': '错误 vs 正确',
             'content': f'对比错误写法和正确写法，理解为什么某些看似"差不多"的代码会导致完全不同的结果。细节决定成败。'},
            {'kind': 'code', 'heading': f'正确写法参考（{lang}）',
             'content': code_info['code'] if code_info else f'# {display} — 正确实现\n# 注意边界条件和特殊情况处理',
             'language': lang},
        ]

    elif resource_type == '分层练习':
        sections = [
            {'kind': 'practice', 'heading': f'基础层 — {display}概念理解',
             'content': f'1. 用自己的话解释{display}的核心思想\n2. {display}有哪些关键特征？请列举至少3个\n3. 判断对错：{display}的常见应用场景'},
            {'kind': 'practice', 'heading': f'进阶层 — {display}代码补全',
             'content': f'4. 补全{display}的核心代码（框架已给出）\n5. 修改参数，观察{display}行为变化\n6. 分析代码的时间复杂度'},
            {'kind': 'practice', 'heading': f'提高层 — {display}综合应用',
             'content': f'7. 将{display}应用于一个新的问题场景\n8. 比较{display}的两种不同实现方式的优劣'},
            {'kind': 'answer_hint', 'heading': '提示与参考答案',
             'content': f'基础层答案方向：{display}的关键在于理解其基本原理和适用条件。进阶层请参考代码示例中的完整实现。提高层建议先画出流程图再编码。'},
        ]

    elif resource_type == '项目案例':
        sections = [
            {'kind': 'task', 'heading': f'项目概述：基于{display}的实践',
             'content': f'设计一个围绕"{display}"的小型实战项目。综合运用{module}的核心知识与编程技能，完成从需求分析到代码实现的完整流程。'},
            {'kind': 'steps', 'heading': '第一阶段：需求分析与设计',
             'steps': [
                 f'步骤1：明确项目目标 — 这个项目要解决什么问题？',
                 f'步骤2：设计数据结构 — 用哪些数据结构来表示问题？',
                 f'步骤3：设计算法流程 — 核心逻辑的步骤是什么？',
             ]},
            {'kind': 'steps', 'heading': '第二阶段：代码实现',
             'steps': [
                 '步骤4：搭建项目框架（类、函数定义）',
                 '步骤5：实现核心功能',
                 '步骤6：添加测试用例',
             ]},
            {'kind': 'text', 'heading': '第三阶段：测试与优化',
             'content': '用多种测试数据验证项目的正确性。分析时间/空间复杂度，思考是否有优化空间。'},
        ]
        if code_info:
            sections.insert(3, {'kind': 'code', 'heading': f'参考代码框架（{lang}）',
                                'content': code_info['code'], 'language': code_info['language']})

    else:
        sections = [{'kind': 'text', 'heading': display, 'content': f'关于"{display}"的学习资源。'}]

    return sections


def _build_personalized_reason(gen_context: dict, resource_type: str) -> str:
    """Build a personalized match reason string from generation context."""
    parts = []
    foundation = gen_context.get('foundation_level', '')
    goal = gen_context.get('learning_goal', '')
    prefs = gen_context.get('expression_preferences', [])
    difficulties = gen_context.get('current_difficulties', [])
    module = gen_context.get('module', '')

    if foundation:
        level_map = {'基础薄弱': '侧重基础概念和详细步骤', '一般': '侧重代码实践和常见模式', '较好': '侧重进阶技巧和综合应用'}
        parts.append(level_map.get(foundation, f'适配{foundation}水平'))

    if goal:
        goal_map = {'概念理解': '以图解和步骤拆解为主', '考试复习': '以考点归纳和易错分析为主',
                    '刷题训练': '以代码示例和分层练习为主', '项目实践': '以项目案例和综合应用为主'}
        parts.append(goal_map.get(goal, f'适配{goal}目标'))

    if prefs:
        pref_text = '、'.join(prefs[:3])
        parts.append(f'表达方式包含{pref_text}')

    if difficulties:
        diff_text = '、'.join(difficulties[:2])
        parts.append(f'针对薄弱点"{diff_text}"加强练习')

    if not parts:
        parts.append(f'围绕"{module}"模块系统生成，适合入门学习')

    return ' | '.join(parts)


def build_dynamic_fallback(gen_context: dict) -> dict:
    """Build personalized resource cards entirely from gen_context — no fixed JSON."""
    topic = gen_context['topic']
    module = gen_context['module']
    lang = gen_context['normalized_language']
    resource_types = gen_context['resource_types']
    difficulty = gen_context['difficulty']

    cards: list[dict] = []
    for i, rt in enumerate(resource_types):
        spec = get_resource_type_spec(rt)
        sections = _build_type_sections(rt, module, topic, lang)
        display = _topic_display_name(topic)

        card = {
            'id': f'res-fb-{i + 1:03d}',
            'title': f'{display} — {rt}',
            'type': rt,
            'course': '数据结构与算法',
            'knowledge_point': display,
            'difficulty': difficulty,
            'language': lang,
            'summary': f'围绕"{display}"的{rt}，适配{module}模块。{spec["description"]}',
            'sections': sections,
            'key_concepts': [display, module],
            'learning_tips': [f'建议配合{display}相关的代码实践一起学习', '先理解原理再动手实现'],
            'recommended_usage': f'先浏览整体结构，再逐节深入学习{display}的核心内容。',
            'estimated_time': '20-30分钟',
            'match_reason': _build_personalized_reason(gen_context, rt),
            'personalized_reason': _build_personalized_reason(gen_context, rt),
            'programming_language_used': lang,
        }
        cards.append(card)

    return {
        'resource_cards': cards,
        'topic': topic,
        'normalized_module': module,
        'resource_types_used': resource_types,
        'programming_language_used': lang,
        'personalization_source': gen_context['personalization_source'],
        'personalization_summary': {
            'foundation_level': gen_context['foundation_level'],
            'learning_goal': gen_context['learning_goal'],
            'current_difficulties': gen_context['current_difficulties'],
            'expression_preferences': gen_context['expression_preferences'],
            'matched_module': module,
        },
        'generation_signature': gen_context['generation_signature'],
        'fallback': True,
    }


# ═══════════════════════════════════════════════════════════════════
# Phase 3B: Validation and post-processing
# ═══════════════════════════════════════════════════════════════════

def _validate_and_fix_code_language(cards: list[dict], expected_lang: str) -> int:
    """Check all code sections in all cards. Fix language mismatches. Returns fix count."""
    normalized_expected = normalize_programming_language(expected_lang)
    fixes = 0
    for card in cards:
        sections = card.get('sections', []) or []
        for section in sections:
            if section.get('kind') == 'code' or section.get('codeBlock') or section.get('language'):
                current = section.get('language', '')
                if current and normalize_programming_language(current) != normalized_expected:
                    section['language'] = normalized_expected
                    fixes += 1
                elif not current:
                    section['language'] = normalized_expected
                    fixes += 1
    return fixes


def finalize_resource_cards(cards: list[dict], gen_context: dict) -> list[dict]:
    """
    Post-process resource cards:
    1. Validate structural completeness (id, title, type, summary)
    2. Fix code language consistency
    3. Inject programming_language_used and personalized_reason
    4. Remove empty/null sections
    """
    lang = gen_context.get('normalized_language', 'Python')
    module = gen_context.get('module', '')
    topic = gen_context.get('topic', '')

    _validate_and_fix_code_language(cards, lang)

    valid_cards: list[dict] = []
    for card in cards:
        if not isinstance(card, dict):
            continue
        title = card.get('title')
        rtype = card.get('type')
        if not title or not rtype:
            continue

        # Ensure required fields
        card.setdefault('id', f'res-{random.randint(1000, 9999)}')
        card.setdefault('course', '数据结构与算法')
        card.setdefault('knowledge_point', topic)
        card.setdefault('difficulty', gen_context.get('difficulty', '入门'))
        card.setdefault('language', lang)
        card.setdefault('summary', card.get('summary', f'关于"{topic}"的{rtype}学习资源。'))

        # Inject language and personalization
        card['programming_language_used'] = lang
        if not card.get('personalized_reason'):
            card['personalized_reason'] = _build_personalized_reason(gen_context, rtype)
        if not card.get('match_reason'):
            card['match_reason'] = card['personalized_reason']

        # Clean sections: remove entries with null/empty content
        sections = card.get('sections', [])
        if isinstance(sections, list):
            cleaned = [s for s in sections if isinstance(s, dict) and (s.get('content') or s.get('steps') or s.get('codeBlock') or s.get('items'))]
            card['sections'] = cleaned

        valid_cards.append(card)

    return valid_cards


# ═══════════════════════════════════════════════════════════════════
# Resource Generation (Phase 3B: dynamic fallback + LLM)
# ═══════════════════════════════════════════════════════════════════

def generate_resources(
    course_id: str,
    knowledge_point: str,
    difficulty: str = "入门",
    language: str = "Python",
    resource_types: list[str] | None = None,
    quick_profile: dict | None = None,
    learning_topic: str = "",
):
    """
    Generate personalized learning resources.

    All paths (Mock, LLM, Fallback) go through:
    1. build generation_context from all inputs
    2. Generate cards (LLM or dynamic fallback)
    3. finalize_resource_cards() post-processing

    The response ALWAYS includes verification fields:
    topic, normalized_module, resource_types_used,
    programming_language_used, personalization_source,
    personalization_summary, generation_signature
    """
    from services.llm_service import get_llm, MockProvider

    # Use learning_topic as knowledge_point if the latter is generic
    effective_topic = knowledge_point
    if learning_topic and learning_topic.strip():
        effective_topic = learning_topic.strip()

    # Build generation context
    gen_context = build_generation_context(
        course_id=course_id,
        knowledge_point=effective_topic,
        difficulty=difficulty,
        language=language,
        resource_types=resource_types,
        quick_profile=quick_profile,
    )

    llm = get_llm()

    # Mock mode: use dynamic fallback (NOT fixed JSON)
    if isinstance(llm, MockProvider):
        result = build_dynamic_fallback(gen_context)
        result['resource_cards'] = finalize_resource_cards(result['resource_cards'], gen_context)
        return result

    # Real LLM: try LLM first, fall back to dynamic fallback on failure
    try:
        llm_result = _generate_via_llm(llm, gen_context)
        if llm_result is not None:
            return llm_result
    except Exception as e:
        logger.warning("LLM generate_resources failed: %s — falling back to dynamic fallback", e)

    result = build_dynamic_fallback(gen_context)
    result['resource_cards'] = finalize_resource_cards(result['resource_cards'], gen_context)
    return result


def _generate_via_llm(llm, gen_context: dict) -> dict | None:
    """
    Render prompt with gen_context, call LLM, validate + enrich response.

    Returns full response dict (with verification fields) on success, None on failure.
    """
    from services.prompt_service import render_template

    rendered = render_template(
        "generate_resources",
        topic=gen_context['topic'],
        module=gen_context['module'],
        difficulty=gen_context['difficulty'],
        language=gen_context['normalized_language'],
        resource_types=gen_context['resource_types'],
        foundation_level=gen_context.get('foundation_level', '未指定'),
        learning_goal=gen_context.get('learning_goal', '未指定'),
        current_difficulties=gen_context.get('current_difficulties', []),
        expression_preferences=gen_context.get('expression_preferences', []),
    )

    if not rendered:
        logger.warning("generate_resources template render returned empty")
        return None

    messages: list[dict] = [
        {"role": "system", "content": rendered},
        {
            "role": "user",
            "content": (
                f"请为以下学习需求生成资源推荐：\n"
                f"主题：{gen_context['topic']}\n"
                f"模块：{gen_context['module']}\n"
                f"难度：{gen_context['difficulty']}\n"
                f"编程语言：{gen_context['normalized_language']}\n"
                f"偏好类型：{', '.join(gen_context['resource_types'])}\n"
                f"基础水平：{gen_context.get('foundation_level', '未指定')}\n"
                f"学习目标：{gen_context.get('learning_goal', '未指定')}\n"
                f"困难点：{', '.join(gen_context.get('current_difficulties', []))}\n"
                f"表达偏好：{', '.join(gen_context.get('expression_preferences', []))}"
            ),
        },
    ]

    result = llm.chat_json(messages, temperature=0.7)

    if not isinstance(result, dict):
        logger.warning("LLM chat_json returned non-dict (type=%s)", type(result).__name__)
        return None

    cards = result.get("resource_cards")
    if not isinstance(cards, list) or len(cards) == 0:
        logger.warning("LLM response missing or empty 'resource_cards' list")
        return None

    # Validate and enrich each card
    enriched_cards: list[dict] = []
    for i, card in enumerate(cards):
        if not isinstance(card, dict):
            continue
        title = card.get("title")
        res_type = card.get("type")
        summary = card.get("summary", "")

        if not isinstance(title, str) or not title.strip():
            continue
        if not isinstance(res_type, str) or not res_type.strip():
            continue
        if not isinstance(summary, str):
            summary = ""

        enriched_cards.append({
            "id": card.get("id", f"res-llm-{i + 1:03d}"),
            "title": title.strip(),
            "type": res_type.strip(),
            "course": "数据结构与算法",
            "knowledge_point": gen_context['topic'],
            "difficulty": gen_context.get('difficulty', '入门'),
            "language": gen_context['normalized_language'],
            "summary": summary.strip(),
            "sections": card.get("sections", []),
            "key_concepts": card.get("key_concepts", []),
            "learning_tips": card.get("learning_tips", []),
            "recommended_usage": card.get("recommended_usage", ""),
            "estimated_time": card.get("estimated_time", ""),
            "match_reason": card.get("match_reason", ""),
            "personalized_reason": card.get("personalized_reason", ""),
        })

    if not enriched_cards:
        logger.warning("All LLM-generated resource cards were invalid")
        return None

    # Post-process
    final_cards = finalize_resource_cards(enriched_cards, gen_context)

    return {
        'resource_cards': final_cards,
        'topic': gen_context['topic'],
        'normalized_module': gen_context['module'],
        'resource_types_used': gen_context['resource_types'],
        'programming_language_used': gen_context['normalized_language'],
        'personalization_source': gen_context['personalization_source'],
        'personalization_summary': {
            'foundation_level': gen_context['foundation_level'],
            'learning_goal': gen_context['learning_goal'],
            'current_difficulties': gen_context['current_difficulties'],
            'expression_preferences': gen_context['expression_preferences'],
            'matched_module': gen_context['module'],
        },
        'generation_signature': gen_context['generation_signature'],
        'fallback': False,
    }


# ---- Internal helpers ----

def _load_index() -> Optional[dict]:
    """加载 resource_library/index.json"""
    if not INDEX_PATH.exists():
        logger.warning("Resource library index not found: %s", INDEX_PATH)
        return None
    try:
        with open(INDEX_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to read resource library index: %s", e)
        return None


def _read_content_file(content_path: str) -> tuple[Optional[str], Optional[str]]:
    """
    读取资源正文文件
    返回 (content_type, content_str) 或 (content_type, None)
    """
    full_path = LIBRARY_DIR / content_path
    if not full_path.exists():
        logger.warning("Resource content file not found: %s", full_path)
        return None, None

    suffix = full_path.suffix.lower()
    try:
        with open(full_path, encoding="utf-8") as f:
            raw = f.read()
        if suffix == ".json":
            return "json", raw
        elif suffix in (".md", ".txt"):
            return "markdown", raw
        else:
            return "markdown", raw
    except OSError as e:
        logger.warning("Failed to read content file %s: %s", full_path, e)
        return None, None


def _filter_resources(
    resources: list[dict],
    course_code: Optional[str] = None,
    topic_code: Optional[str] = None,
    resource_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    language: Optional[str] = None,
    tags: Optional[list[str]] = None,
    search: Optional[str] = None,
) -> list[dict]:
    """在资源列表中按条件筛选"""
    result = resources
    if course_code:
        result = [r for r in result if r.get("courseCode") == course_code]
    if topic_code:
        result = [r for r in result if r.get("topicCode") == topic_code]
    if resource_type:
        result = [r for r in result if r.get("type") == resource_type]
    if difficulty:
        result = [r for r in result if r.get("difficulty") == difficulty]
    if language:
        result = [r for r in result if r.get("language") == language]
    if tags:
        for tag in tags:
            result = [r for r in result if tag in (r.get("tags") or [])]
    if search:
        search_lower = search.lower()
        result = [
            r for r in result
            if search_lower in (r.get("title") or "").lower()
            or search_lower in (r.get("summary") or "").lower()
        ]
    return result


# ---- Public API: Resource Library (Phase 4A) ----

def list_library_resources(
    course_code: Optional[str] = None,
    topic_code: Optional[str] = None,
    resource_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    language: Optional[str] = None,
    tags: Optional[list[str]] = None,
    search: Optional[str] = None,
) -> dict:
    """
    资源库列表（支持多条件筛选）
    返回元数据列表，不含正文内容
    """
    index = _load_index()
    if index is None:
        return {"resources": [], "total": 0, "source": "resource_library_unavailable"}

    all_resources = index.get("resources", [])
    filtered = _filter_resources(
        all_resources, course_code, topic_code, resource_type,
        difficulty, language, tags, search,
    )

    items = []
    for r in filtered:
        items.append({
            "id": r.get("id"),
            "title": r.get("title"),
            "course": r.get("course"),
            "courseCode": r.get("courseCode"),
            "topic": r.get("topic"),
            "topicCode": r.get("topicCode"),
            "type": r.get("type"),
            "difficulty": r.get("difficulty"),
            "language": r.get("language"),
            "tags": r.get("tags"),
            "estimatedTime": r.get("estimatedTime"),
            "summary": r.get("summary"),
            "resource_type": r.get("resource_type"),
            "module": r.get("module"),
        })

    return {
        "resources": items,
        "total": len(items),
        "source": "resource_library_index",
    }


def get_library_resource_detail(resource_id: str) -> Optional[dict]:
    """资源详情 — 元数据 + 正文内容"""
    index = _load_index()
    if index is None:
        return None

    all_resources = index.get("resources", [])
    match = None
    for r in all_resources:
        if r.get("id") == resource_id:
            match = r
            break

    if not match:
        return None

    detail = {
        "id": match.get("id"),
        "title": match.get("title"),
        "course": match.get("course"),
        "courseCode": match.get("courseCode"),
        "topic": match.get("topic"),
        "topicCode": match.get("topicCode"),
        "type": match.get("type"),
        "difficulty": match.get("difficulty"),
        "language": match.get("language"),
        "tags": match.get("tags"),
        "estimatedTime": match.get("estimatedTime"),
        "summary": match.get("summary"),
        "contentPath": match.get("contentPath"),
        "source": match.get("source"),
        "version": match.get("version"),
        "updatedAt": match.get("updatedAt"),
        "resource_type": match.get("resource_type"),
        "module": match.get("module"),
    }

    content_path = match.get("contentPath")
    if content_path:
        content_type, raw = _read_content_file(content_path)
        detail["content_type"] = content_type or "unknown"
        if content_type == "json" and raw:
            try:
                detail["content_json"] = json.loads(raw)
                detail["content"] = None
            except json.JSONDecodeError:
                detail["content"] = raw
                detail["content_json"] = None
        else:
            detail["content"] = raw
            detail["content_json"] = None
    else:
        detail["content_type"] = "none"
        detail["content"] = None
        detail["content_json"] = None

    return detail


def get_library_stats() -> dict:
    """资源库统计：按课程、类型、难度分组计数"""
    index = _load_index()
    if index is None:
        return {
            "total_resources": 0,
            "by_course": {},
            "by_type": {},
            "by_difficulty": {},
            "source": "resource_library_unavailable",
        }

    all_resources = index.get("resources", [])
    by_course: dict[str, int] = {}
    by_type: dict[str, int] = {}
    by_difficulty: dict[str, int] = {}

    for r in all_resources:
        cc = r.get("courseCode", "unknown")
        rt = r.get("type", "unknown")
        diff = r.get("difficulty", "unknown")
        by_course[cc] = by_course.get(cc, 0) + 1
        by_type[rt] = by_type.get(rt, 0) + 1
        by_difficulty[diff] = by_difficulty.get(diff, 0) + 1

    return {
        "total_resources": len(all_resources),
        "by_course": dict(sorted(by_course.items())),
        "by_type": dict(sorted(by_type.items())),
        "by_difficulty": dict(sorted(by_difficulty.items())),
        "source": "resource_library_index",
    }


# ---- Phase 4B: User Resource Package CRUD ----

def get_user_packages(user_id: int) -> list[dict]:
    """获取用户的资源包列表"""
    db = None
    try:
        db = SessionLocal()
        packages = db.query(UserResourcePackage).filter(
            UserResourcePackage.user_id == user_id
        ).order_by(UserResourcePackage.created_at.desc()).all()
        return [
            {
                "id": p.id,
                "user_id": p.user_id,
                "resource_id": p.resource_id,
                "library_resource_id": None,
                "custom_title": p.custom_title,
                "topic": p.topic,
                "course_name": p.course_name,
                "resource_type": p.resource_type,
                "estimated_time": p.estimated_time,
                "purpose": p.purpose,
                "priority": p.priority,
                "note": p.note,
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in packages
        ]
    except Exception as e:
        logger.warning("Failed to get packages for user %d: %s", user_id, e)
        return []
    finally:
        if db:
            db.close()


def add_to_package(user_id: int, data: dict) -> Optional[dict]:
    """添加资源到用户资源包（含去重：user_id + custom_title + topic + course_name）"""
    db = None
    try:
        db = SessionLocal()

        # Dedup: check if the same resource already exists for this user
        title = data.get("custom_title", "")
        topic = data.get("topic", "")
        course = data.get("course_name", "")
        existing = db.query(UserResourcePackage).filter(
            UserResourcePackage.user_id == user_id,
            UserResourcePackage.custom_title == title,
            UserResourcePackage.topic == topic,
            UserResourcePackage.course_name == course,
        ).first()

        if existing:
            return {
                "id": existing.id,
                "user_id": existing.user_id,
                "resource_id": existing.resource_id,
                "library_resource_id": None,
                "custom_title": existing.custom_title,
                "topic": existing.topic,
                "course_name": existing.course_name,
                "resource_type": existing.resource_type,
                "estimated_time": existing.estimated_time,
                "purpose": existing.purpose,
                "priority": existing.priority,
                "note": existing.note,
                "status": existing.status,
                "created_at": existing.created_at.isoformat() if existing.created_at else None,
                "updated_at": existing.updated_at.isoformat() if existing.updated_at else None,
                "detail": "already_saved",
            }

        pkg = UserResourcePackage(
            user_id=user_id,
            resource_id=data.get("resource_id"),
            custom_title=title,
            topic=topic,
            course_name=course,
            resource_type=data.get("resource_type"),
            estimated_time=data.get("estimated_time"),
            purpose=data.get("purpose"),
            priority=data.get("priority"),
            note=data.get("note"),
            status="saved",
        )
        db.add(pkg)
        db.commit()
        db.refresh(pkg)
        return {
            "id": pkg.id,
            "user_id": pkg.user_id,
            "resource_id": pkg.resource_id,
            "library_resource_id": data.get("library_resource_id"),
            "custom_title": pkg.custom_title,
            "topic": pkg.topic,
            "course_name": pkg.course_name,
            "resource_type": pkg.resource_type,
            "estimated_time": pkg.estimated_time,
            "purpose": pkg.purpose,
            "priority": pkg.priority,
            "note": pkg.note,
            "status": pkg.status,
            "created_at": pkg.created_at.isoformat() if pkg.created_at else None,
            "updated_at": pkg.updated_at.isoformat() if pkg.updated_at else None,
        }
    except Exception as e:
        logger.warning("Failed to add package for user %d: %s", user_id, e)
        if db:
            db.rollback()
        return None
    finally:
        if db:
            db.close()


def update_package_item(package_id: int, user_id: int, data: dict) -> Optional[dict]:
    """更新用户资源包条目"""
    db = None
    try:
        db = SessionLocal()
        pkg = db.query(UserResourcePackage).filter(
            UserResourcePackage.id == package_id,
            UserResourcePackage.user_id == user_id,
        ).first()
        if not pkg:
            return None

        updatable = [
            "custom_title", "topic", "course_name", "resource_type",
            "estimated_time", "purpose", "priority", "note", "status",
        ]
        for field in updatable:
            if field in data:
                setattr(pkg, field, data[field])

        db.commit()
        db.refresh(pkg)
        return {
            "id": pkg.id,
            "user_id": pkg.user_id,
            "resource_id": pkg.resource_id,
            "library_resource_id": None,
            "custom_title": pkg.custom_title,
            "topic": pkg.topic,
            "course_name": pkg.course_name,
            "resource_type": pkg.resource_type,
            "estimated_time": pkg.estimated_time,
            "purpose": pkg.purpose,
            "priority": pkg.priority,
            "note": pkg.note,
            "status": pkg.status,
            "created_at": pkg.created_at.isoformat() if pkg.created_at else None,
            "updated_at": pkg.updated_at.isoformat() if pkg.updated_at else None,
        }
    except Exception as e:
        logger.warning("Failed to update package #%d: %s", package_id, e)
        if db:
            db.rollback()
        return None
    finally:
        if db:
            db.close()


def delete_package_item(package_id: int, user_id: int) -> bool:
    """删除用户资源包条目"""
    db = None
    try:
        db = SessionLocal()
        pkg = db.query(UserResourcePackage).filter(
            UserResourcePackage.id == package_id,
            UserResourcePackage.user_id == user_id,
        ).first()
        if not pkg:
            return False
        db.delete(pkg)
        db.commit()
        return True
    except Exception as e:
        logger.warning("Failed to delete package #%d: %s", package_id, e)
        if db:
            db.rollback()
        return False
    finally:
        if db:
            db.close()
