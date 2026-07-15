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

# Topic keyword → normalized module (ordered: longer/more-specific keywords first)
TOPIC_TO_MODULE: dict[str, str] = {
    '时间复杂度': '复杂度分析', '空间复杂度': '复杂度分析', '复杂度': '复杂度分析', '大O': '复杂度分析',
    '顺序表': '线性表', '链表': '线性表', '线性表': '线性表', '数组': '线性表',
    '调用栈': '递归与调用栈', '递归': '递归与调用栈', '栈': '栈与队列', '队列': '栈与队列',
    '二叉搜索树': '树与二叉树', '树的遍历': '树与二叉树', '树遍历': '树与二叉树', '二叉树': '树与二叉树',
    '最短路径': '图结构与图算法', '图遍历': '图结构与图算法', 'BFS': '图结构与图算法', 'DFS': '图结构与图算法', '图': '图结构与图算法',
    '二分查找': '排序与查找', '快速排序': '排序与查找', '归并排序': '排序与查找', '排序': '排序与查找', '查找': '排序与查找',
    '哈希': '散列表', '散列': '散列表',
    '动态规划': '动态规划入门', 'DP': '动态规划入门',
    '综合': '综合项目实践', '项目': '综合项目实践',
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


def normalize_resource_type(rt: str) -> str:
    """Normalize resource type to one of ALLOWED_TYPES. Returns '' if unrecognized."""
    if not rt:
        return ''
    rt = rt.strip()
    if rt in ALLOWED_TYPES:
        return rt
    # Handle common variants
    aliases = {
        'code_example': '代码示例', 'code': '代码示例', '代码': '代码示例',
        'visual': '图解讲解', 'diagram': '图解讲解', '图解': '图解讲解',
        'mistake': '易错点', 'pitfall': '易错点', '易错': '易错点',
        'practice': '分层练习', 'exercise': '分层练习', '练习': '分层练习',
        'project': '项目案例', 'case': '项目案例', '项目': '项目案例',
    }
    return aliases.get(rt.lower(), rt)  # return normalized or original


def _count_cn(text: str) -> int:
    """Count Chinese characters (U+4E00–U+9FFF) in a string."""
    if not text:
        return 0
    return sum(1 for ch in text if '一' <= ch <= '鿿')


def _count_lines(text: str) -> int:
    """Count non-empty lines in a code string."""
    if not text:
        return 0
    return len([ln for ln in text.split('\n') if ln.strip()])


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

    # ── Phase 14B-4: strict resource_types handling ──
    # selected_resource_types = exactly what the user requested (may be None/empty)
    # effective_types = validated list used for generation (defaults to triple only when truly empty)
    user_requested_types = resource_types if isinstance(resource_types, list) and len(resource_types) > 0 else None
    if user_requested_types:
        effective_types = [t for t in user_requested_types if t in ALLOWED_TYPES]
        if not effective_types:
            effective_types = user_requested_types  # keep user's types even if unknown to ALLOWED_TYPES
    else:
        effective_types = ['图解讲解', '代码示例', '分层练习']

    normalized_lang = normalize_programming_language(
        qp.get('programming_language') or language
    )

    # ── Topic sanitization: detect and fix garbled/corrupted topic ──
    raw_topic = knowledge_point or ''
    # Strip non-CJK, non-ASCII garbage that signals encoding corruption
    if '?' in raw_topic and not any('一' <= ch <= '鿿' for ch in raw_topic):
        # Topic is corrupted — try quick_profile and fallbacks
        raw_topic = (qp.get('topic') or qp.get('knowledge_point') or '').strip()
        if not raw_topic or ('?' in raw_topic and not any('一' <= ch <= '鿿' for ch in raw_topic)):
            raw_topic = '二叉树前序遍历'  # Last-resort fallback for data structures course
        logger.warning("Garbled topic detected, using fallback: %r", raw_topic)

    module_name = resolve_module_name(raw_topic)

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
        'topic': raw_topic,
        'course_id': course_id,
        'module': module_name,
        'difficulty': difficulty,
        'language': language,
        'normalized_language': normalized_lang,
        'resource_types': effective_types,
        'selected_resource_types': user_requested_types,  # exactly what user asked for (Phase 14B-4)
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
        'Python': '''def sum_list(arr, n=None):
    """递归求和：sum(arr[0:n]) = arr[n-1] + sum(arr[0:n-1])"""
    if n is None:
        n = len(arr)
    if n <= 0:              # 基准情形：空数组和为 0
        return 0
    return arr[n - 1] + sum_list(arr, n - 1)

def reverse_string(s):
    """递归反转字符串：reverse(s) = reverse(s[1:]) + s[0]"""
    if len(s) <= 1:         # 基准情形：空串或单字符
        return s
    return reverse_string(s[1:]) + s[0]

def gcd(a, b):
    """辗转相除法求最大公约数 — 欧几里得算法"""
    if b == 0:              # 基准情形
        return a
    return gcd(b, a % b)    # 递归情形

print("sum([1,2,3,4,5]) =", sum_list([1, 2, 3, 4, 5]))  # 15
print("reverse('hello') =", reverse_string("hello"))      # "olleh"
print("gcd(48, 18) =", gcd(48, 18))                       # 6''',
        'C': '''#include <stdio.h>

int sum_list(int arr[], int n) {
    if (n <= 0) return 0;                   // 基准情形
    return arr[n - 1] + sum_list(arr, n - 1);
}

void reverse_print(char s[], int idx) {
    if (s[idx] == '\\0') return;             // 基准情形
    reverse_print(s, idx + 1);               // 先递归到末尾
    putchar(s[idx]);                         // 回退时输出（实现反转）
}

int gcd(int a, int b) {
    if (b == 0) return a;
    return gcd(b, a % b);
}

int main() {
    int arr[] = {1, 2, 3, 4, 5};
    printf("sum = %d\\n", sum_list(arr, 5));   // 15
    printf("reverse of hello: ");
    reverse_print("hello", 0);                // "olleh"
    printf("\\ngcd(48,18) = %d\\n", gcd(48, 18)); // 6
    return 0;
}''',
        'C++': '''#include <iostream>
using namespace std;

int sum_list(int arr[], int n) {
    if (n <= 0) return 0;
    return arr[n - 1] + sum_list(arr, n - 1);
}

void reverse_print(const string& s, int idx) {
    if (idx >= s.length()) return;           // 基准情形
    reverse_print(s, idx + 1);
    cout << s[idx];                          // 回退时输出
}

int gcd(int a, int b) {
    if (b == 0) return a;
    return gcd(b, a % b);
}

int main() {
    int arr[] = {1, 2, 3, 4, 5};
    cout << "sum = " << sum_list(arr, 5) << endl;     // 15
    cout << "reverse of hello: ";
    reverse_print("hello", 0);                         // "olleh"
    cout << endl;
    cout << "gcd(48,18) = " << gcd(48, 18) << endl;   // 6
    return 0;
}''',
        'Java': '''public class RecursionDemo {
    static int sumList(int[] arr, int n) {
        if (n <= 0) return 0;                   // 基准情形
        return arr[n - 1] + sumList(arr, n - 1);
    }

    static void reversePrint(String s, int idx) {
        if (idx >= s.length()) return;           // 基准情形
        reversePrint(s, idx + 1);
        System.out.print(s.charAt(idx));         // 回退时输出
    }

    static int gcd(int a, int b) {
        if (b == 0) return a;
        return gcd(b, a % b);
    }

    public static void main(String[] args) {
        int[] arr = {1, 2, 3, 4, 5};
        System.out.println("sum = " + sumList(arr, 5));      // 15
        System.out.print("reverse of hello: ");
        reversePrint("hello", 0);                            // "olleh"
        System.out.println();
        System.out.println("gcd(48,18) = " + gcd(48, 18));   // 6
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


def _topic_display_name(topic: str) -> str:
    """Extract a clean display name from the topic string."""
    if not topic:
        return '数据结构与算法'
    return topic.strip().rstrip('。，,;；')


# ═══════════════════════════════════════════════════════════════════
# Module-aware content database (used by generic builders)
# ═══════════════════════════════════════════════════════════════════

_MODULE_CONTENT: dict[str, dict] = {
    '复杂度分析': {
        'overview': (
            '复杂度分析是衡量算法效率的核心工具，分为时间复杂度（执行时间随输入规模的增长趋势）'
            '和空间复杂度（额外内存使用量随输入规模的增长趋势）。'
            '掌握复杂度分析是写出高性能代码的基础——它能帮助你在编码之前就预判算法在极端数据下的表现。'
        ),
        'concepts': ['时间复杂度', '空间复杂度', '大O表示法', '最好/最差/平均情况', '渐进分析'],
        'errors': [
            ('错误一：混淆时间复杂度和实际运行时间',
             '时间复杂度描述的是"增长趋势"而非具体的执行秒数。O(n²) 的算法在 n=10 时可能比 O(n) 的算法更快，'
             '因为常数因子在 n 较小时起主导作用。但 n 增大到 10⁵ 时，趋势差异会碾压常数因子。'
             '正确做法：用小规模测试验证正确性，用大规模测试验证复杂度。'),
            ('错误二：嵌套循环的复杂度计算遗漏内层',
             '外层循环 O(n)，内层循环 O(log n) → 总复杂度 O(n log n)，而非 O(n)。'
             '许多初学者看到循环嵌套就直接写 O(n²)，但实际内层的规模可能随外层的 i 变化。'
             '正确做法：逐层分析每层循环的迭代次数，然后将它们相乘。'),
            ('错误三：递归算法只关注深度忽略每层代价',
             '递归算法的总复杂度 = 递归层数 × 每层的计算量。例如归并排序每层 O(n) 共 log n 层 → O(n log n)。'
             '只关注递归深度而忽略每层的合并操作会严重低估真实复杂度。'),
        ],
        'practice': [
            '基础题：分析以下代码的时间复杂度——for i in range(n): for j in range(i+1, n): print(i,j)。（答案：O(n²)，内层执行 n(n-1)/2 次）',
            '进阶：分析递归函数 T(n) = 2T(n/2) + n 的时间复杂度，用递推树绘制展开过程。（答案：O(n log n)）',
        ],
        'project_idea': '设计一个复杂度分析工具：接收一段伪代码描述（嵌套循环、递归），自动推导其时间复杂度和空间复杂度的大O表示，并画出 n=10,100,1000 时的增长曲线对比图。',
    },
    '线性表': {
        'overview': (
            '线性表是最基础的数据结构，包括顺序存储（数组/顺序表）和链式存储（链表）两种实现方式。'
            '顺序表支持 O(1) 随机访问但插入删除需移动元素（O(n)）；链表插入删除 O(1)（已知位置）但随机访问需遍历（O(n)）。'
            '理解两者的时空权衡是数据结构选型的入门第一课。'
        ),
        'concepts': ['顺序表', '单链表', '双向链表', '循环链表', '头插法', '尾插法', '双指针技巧'],
        'errors': [
            ('错误一：链表删除时忘记更新前驱指针',
             '删除链表中间的节点时，仅仅 free/delete 该节点而忘记将前驱节点的 next 指向被删节点的后继，'
             '会导致链表断裂或后续节点被泄漏。正确做法：在遍历中找到前驱节点后，执行 prev.next = curr.next 再释放 curr。'),
            ('错误二：头插法忘记更新头指针',
             '在链表头部插入新节点后，必须将头指针指向新节点。如果函数传的是头指针的副本（值传递），'
             '外部调用者的头指针不会更新——需要使用指针的指针（或返回新头指针）。'),
            ('错误三：顺序表插入未检查容量',
             '顺序表插入前应检查当前元素个数是否已达容量上限。在满容量时继续插入会导致数组越界写入——'
             '这是 C/C++ 中最隐蔽的内存错误之一。正确做法：插入前检查 size < capacity，否则先扩容（realloc/vector::push_back）。'),
        ],
        'practice': [
            '基础题：实现单链表的插入（头插、尾插、中间插入）和删除操作，并写出完整的测试用例覆盖空链表、单节点链表和多节点链表。',
            '进阶：使用双指针技巧（快慢指针）检测链表中是否存在环——快指针每次走两步，慢指针每次走一步，若相遇则有环。分析该算法的时间复杂度。',
        ],
        'project_idea': '实现一个简单的联系人管理系统：用双向链表存储联系人（姓名、电话），支持按姓名排序、按首字母分组显示、增删改查，并比较链表与数组实现在此场景下的实际性能差异。',
    },
    '栈与队列': {
        'overview': (
            '栈（Stack）是后进先出（LIFO）的线性结构，队列（Queue）是先进先出（FIFO）的线性结构。'
            '栈的核心操作是 push（入栈）和 pop（出栈），天然适合处理括号匹配、表达式求值、DFS 等问题。'
            '队列的核心操作是 enqueue（入队）和 dequeue（出队），天然适合 BFS、任务调度、消息缓冲等场景。'
        ),
        'concepts': ['LIFO', 'FIFO', 'push/pop', 'enqueue/dequeue', '循环队列', '单调栈', '双端队列'],
        'errors': [
            ('错误一：栈空时直接 pop 导致下溢',
             '在 pop 或 top 操作前必须检查栈是否为空。空栈上执行 pop 在数组实现中会导致索引为 -1 的越界访问，'
             '在链式实现中会导致空指针解引用。正确做法：所有 pop/top 操作前加 if (isEmpty()) 守卫。'),
            ('错误二：循环队列的队空和队满条件混淆',
             '在循环队列的数组实现中，队空条件 front==rear 和队满条件 (rear+1)%capacity==front 的区别在于——'
             '循环队列会浪费一个数组位置来区分队空和队满。如果所有位置都存数据，则队空和队满都表现为 front==rear。'
             '正确做法：保留一个空位，或用额外的 size 字段记录当前元素个数。'),
            ('错误三：括号匹配只统计数量不检查顺序',
             '用计数器 i++（遇到 \'(\'）和 i--（遇到 \')\'）判断括号是否匹配时，只能验证数量，无法检测 ")( " 这种非法顺序。'
             '正确做法：用栈——左括号入栈，右括号时检查栈顶是否匹配。'),
        ],
        'practice': [
            '基础题：实现"用两个栈模拟队列"——栈 A 负责入队（push），栈 B 负责出队（pop）。当 B 空时将 A 中所有元素弹出压入 B。分析每个操作的均摊时间复杂度。',
            '进阶：实现单调栈解决"每日温度"问题——给定温度数组，求每一天需要等几天才能遇到更高的温度。分析单调栈如何将 O(n²) 暴力优化为 O(n)。',
        ],
        'project_idea': '实现一个简单计算器：用栈处理中缀表达式转后缀表达式（逆波兰表达式），再对后缀表达式求值。支持加减乘除和括号，处理除零错误和非法输入。',
    },
    '递归与调用栈': {
        'overview': (
            '递归是一种函数调用自身的编程技术，其正确性建立在三个要素之上：基准情形（base case）终止递归、'
            '递归体将问题分解为同类更小的子问题、每次递归调用都向基准情形靠近。'
            '系统通过调用栈（call stack）管理递归——每层调用的参数、局部变量和返回地址被压入栈帧，'
            '基准情形触发栈帧逐层弹出（回溯）。理解调用栈是理解所有递归算法的关键。'
        ),
        'concepts': ['基准情形', '递归体', '调用栈', '栈帧', '尾递归', '递归树', '记忆化'],
        'errors': [
            ('错误一：忘记基准情形导致无限递归',
             '递归函数缺少终止条件，或因条件永远无法满足（如参数未向基准方向减小），导致调用栈无限增长直至溢出。'
             '正确做法：递归函数的第一行永远是"if (base_case) return base_value;"，这是铁律而非可选建议。'),
            ('错误二：混淆递归深度和递归树宽度',
             '二叉树的前序遍历递归深度 = O(h)（树高），每个节点的计算量为 O(1)，空间复杂度 = O(h)。'
             '但归并排序的递归调用虽然在语法上是两次递归调用，调用栈深度仍为 O(log n)（不是 O(2^log n)），'
             '因为两次递归调用是顺序执行而非同时占栈。正确做法：分析递归调用树的形状——是线性链还是平衡树？'),
            ('错误三：Python 默认递归限制约 1000',
             'Python 的 sys.setrecursionlimit 默认约 1000，递归深度超过此限制会触发 RecursionError。'
             '对于深度可能超过千的量级的递归（如退化为链表的二叉树），必须改用迭代实现或显式栈。'),
        ],
        'practice': [
            '基础题：实现递归版的数组求和 sum_recursive(arr, n) ——基准情形 n==0 返回 0，递归体返回 arr[n-1] + sum_recursive(arr, n-1)。画出 n=4 时的调用栈帧变化图。',
            '进阶：对比汉诺塔问题的递归解和迭代解——写出 n 个盘子的递归解法并分析其时间复杂度（O(2^n)）。用栈模拟递归实现迭代版本。',
        ],
        'project_idea': '实现一个递归可视化工具：输入一个递归函数（如 factorial、fibonacci、二叉树遍历），输出其完整调用栈树形图，标注每层调用的参数值、局部变量和返回值。用缩进表示栈深度。',
    },
    '树与二叉树': {
        'overview': (
            '树是一种非线性层次数据结构，二叉树是最基础的树结构——每个节点最多有两个子节点（左子节点和右子节点）。'
            '二叉树的三种深度优先遍历（前序/中序/后序）和一种广度优先遍历（层序）是理解和操作树结构的核心工具。'
            '二叉搜索树（BST）在最左/最右节点分别存储最小/最大值，左 < 根 < 右的性质使得查找、插入、删除均为 O(h)。'
        ),
        'concepts': ['二叉树', '二叉搜索树(BST)', '前序/中序/后序遍历', '层序遍历', '递归与栈', 'nullptr', '树高与平衡'],
        'errors': [
            ('错误一：遍历时忘记 nullptr 判断导致空指针访问',
             '递归遍历函数中，如果忘记在开头检查 root == nullptr（C/C++中等价于 root == NULL），'
             '当访问到叶子节点的下一层时会解引用空指针导致段错误（Segmentation Fault）。正确做法：递归树遍历函数的第一行必须是空指针检查。'),
            ('错误二：混淆前序/中序/后序三种遍历',
             '三种遍历的函数体结构几乎完全相同，唯一区别是 cout（或 visit）语句在两个递归调用的相对位置：'
             '前序→cout 在最前，中序→cout 在中间，后序→cout 在最后。"前/中/后"指的是根节点被第几个访问。'),
            ('错误三：BST 插入时忘记处理相等元素',
             'BST 的经典实现假设所有键值唯一。如果插入一个已存在的键值且代码中没有相应分支，'
             '可能陷入无限递归或覆盖已有节点。正确做法：明确设计——是覆盖值（更新）、忽略（不插入）还是支持重复（用 count 字段或右子树）。'),
        ],
        'practice': [
            '基础题：给定二叉树 [1,2,3,4,5,null,6]，分别写出前序、中序、后序遍历的结果序列，并画出每种遍历的访问路径（在树结构图上标注访问序号）。',
            '进阶：实现二叉搜索树的插入、查找、删除操作。删除操作需处理三种情况：叶子节点（直接删除）、单子节点（子承父位）、双子节点（用后继节点替换）。',
        ],
        'project_idea': '实现一个 BST 性能基准测试工具：随机生成不同规模（n=10²,10³,10⁴,10⁵）的插入序列，对比随机插入和顺序插入下的树高、查找时间和内存占用。验证平衡树（AVL 或红黑树）的优势。',
    },
    '图结构与图算法': {
        'overview': (
            '图（Graph）由顶点集合 V 和边集合 E 组成，是描述对象间关系的最通用数据结构。'
            '图的存储方式主要包括邻接矩阵（适合稠密图，O(V²)空间）和邻接表（适合稀疏图，O(V+E)空间）。'
            'BFS（广度优先搜索）使用队列实现逐层扩展，天然适合无权图最短路径问题；'
            'DFS（深度优先搜索）使用栈或递归实现深入探索，适合连通分量检测和拓扑排序。'
        ),
        'concepts': ['邻接矩阵', '邻接表', 'BFS', 'DFS', 'visited标记', '最短路径', '拓扑排序', '连通分量'],
        'errors': [
            ('错误一：visited 标记在出队时而非入队时',
             'BFS 中在节点出队时才标记 visited，而非入队时立即标记。'
             '后果：同一层的两个节点可能将同一个邻居重复入队，导致结果中出现重复节点。'
             '正确做法：入队时立即标记 visited[node]=true——"一入队就标记，出队只是读取"。'),
            ('错误二：不连通图仅从单起点遍历',
             '仅从一个起点开始 BFS/DFS，如果图不连通，未被遍历到的节点的 visited 仍为 false。'
             '正确做法：DFS/BFS 模板必须包含外层循环 for each vertex: if not visited[v]: dfs(v)，确保所有连通分量都被覆盖。'),
            ('错误三：稀疏图用邻接矩阵导致 O(V²) 性能浪费',
             '稀疏图（边数远小于 V²）使用邻接矩阵时，每次遍历邻居需要扫描一整行（O(V)），'
             'BFS/DFS 总复杂度从 O(V+E) 退化为 O(V²)。正确做法：除非题目明确图是稠密的，否则默认使用邻接表。'),
        ],
        'practice': [
            '基础题：对给定的 6 节点无向图，分别从节点 A 出发执行 BFS 和 DFS，写出访问序列和队列/栈的每轮状态。图中包含一个三角形（A-B-C-A），观察 visited 标记如何防止无限循环。',
            '进阶：实现拓扑排序的两种方法——DFS 三色标记法（WHITE/GRAY/BLACK）和 BFS 入度法（Kahn算法）。对比两种方法的优缺点和在检测环上的差异。',
        ],
        'project_idea': '实现一个简单的地图导航原型：用图表示城市路网（节点=路口，边=道路，权重=距离），用 Dijkstra 算法求两点间最短路径。支持添加/删除道路，用 BFS 检测路网的连通性。',
    },
    '排序与查找': {
        'overview': (
            '排序和查找是计算机科学中最基本的算法操作。排序算法大致分为比较类（快速排序、归并排序、堆排序）'
            '和非比较类（计数排序、基数排序），前者下界为 O(n log n)，后者在特定条件下可达 O(n)。'
            '二分查找是已排序序列上 O(log n) 的查找算法，通过每次将搜索范围减半来快速定位目标。'
            '稳定性是排序算法的一个重要性质——相等元素的相对顺序在排序前后保持不变。'
        ),
        'concepts': ['快速排序', '归并排序', '二分查找', '稳定性', 'partition', '时间复杂度O(nlogn)', 'left/right/mid'],
        'errors': [
            ('错误一：二分查找的 mid 计算可能整数溢出',
             'mid = (left + right) / 2 在 left 和 right 都接近 INT_MAX 时，left+right 会溢出——'
             '这在处理大型数组（n>10⁹）时是实际存在的 bug。正确做法：mid = left + (right - left) / 2，避免了中间和溢出。'),
            ('错误二：二分查找 while 循环条件 left <= right vs left < right 混淆',
             '两种写法都是正确的，但退出循环后的 left/right 含义不同：left<=right 的版本退出时 left>right，'
             '适合查找"精确值是否存在"；left<right 的版本退出时 left==right，适合查找"插入位置"（lower_bound）。'
             '混用两种模板会导致死循环或漏查。选择一种模板后始终套用它，不要混搭。'),
            ('错误三：快速排序固定选首/尾元素作 pivot 遇已排序数组退化为 O(n²)',
             '固定选第一个或最后一个元素作 pivot，在已排序数组上每次 partition 只排除一个元素，'
             '递归深度 = n → 总复杂度 O(n²)。随机 pivot（随机选一元素与末尾交换）或三数取中法可将退化概率降至极低。'),
        ],
        'practice': [
            '基础题：实现二分查找的两种变体——精确查找（target 存在返回 index，否则返回 -1）和左边界查找（返回 target 首次出现位置，不存在返回插入位置）。用 [1,2,2,2,3,4] 和 target=2 验证两种输出的差异。',
            '进阶：实现归并排序并用 [3a,2,3b,1] 验证其稳定性——排序后 3a 是否仍在 3b 前面？对比快速排序在同样输入上的输出，直观理解稳定性的含义。',
        ],
        'project_idea': '实现一个排序算法性能对比工具：对随机数组、近乎有序数组、逆序数组、全等数组分别运行快速排序、归并排序、堆排序，测量运行时间和比较/交换次数，输出性能对比表和可视化图表，分析每种算法的优势和退化场景。',
    },
    '散列表': {
        'overview': (
            '散列表（Hash Table）通过散列函数将键映射到数组索引，实现平均 O(1) 的插入、查找和删除操作。'
            '当两个不同的键被映射到同一索引时发生哈希冲突（collision），冲突解决方法主要有两类：'
            '链地址法（每个桶存一个链表，冲突时追加到链表尾部）和开放寻址法（冲突时按某种规则探测下一个空闲桶）。'
            '负载因子 lambda = n/m（存储元素数/桶数）是衡量散列表性能的核心指标——lambda 越大性能越差。'
        ),
        'concepts': ['散列函数', '哈希冲突', '链地址法', '开放寻址法', '负载因子', 'rehash', 'unordered_map/dict'],
        'errors': [
            ('错误一：用不可哈希的类型作为键',
             '在 Python 中，list 和 dict 是不可哈希的（因为它们是可变类型），不能用作 dict 的键或 set 的元素。'
             '尝试 dict[[]]=1 会抛出 TypeError: unhashable type: "list"。正确做法：用 tuple 代替 list 作为键；用 frozenset 代替 set。'),
            ('错误二：负载因子过大导致性能退化',
             '当负载因子接近或超过 1 时（开放寻址法下甚至接近 0.7），冲突急剧增多，'
             '散列表的操作从平均 O(1) 退化到 O(n)。正确做法：当负载因子超过阈值（通常 0.75）时触发 rehash——'
             '分配更大的桶数组（通常翻倍）并重新散列所有已有元素。'),
            ('错误三：自定义类型的散列函数未重载 == 运算符',
             '在 C++ 中，如果为自定义类型特化了 std::hash<T>，但没有重载 operator==，'
             'unordered_set/unordered_map 无法判断两个哈希值相等的对象是否真正相等，导致重复元素或查找失败。'
             '规则：如果两个对象 a == b 返回 true，则 hash(a) == hash(b) 必须成立。'),
        ],
        'practice': [
            '基础题：用 Python 的 dict 实现两数之和（Two Sum）的 O(n) 解法——遍历数组，对于每个元素 x，检查 target-x 是否在 hash_map 中。对比暴力双循环 O(n²) 解法在 n=10⁵ 时的性能差异。',
            '进阶：实现简单散列表（链地址法）——包含 put(key, value)、get(key)、remove(key) 操作。散列函数用 key % capacity，负载因子 > 0.75 时触发 rehash（容量翻倍）。用随机键值对测试平均 O(1) 性能。',
        ],
        'project_idea': '实现一个简单的 LRU Cache（最近最少使用缓存）：用哈希表 + 双向链表实现 get 和 put 均为 O(1)。哈希表存储 key→node 的映射，双向链表维护访问顺序（头部=最近使用，尾部=最久未使用）。这是面试极高频率的经典设计。',
    },
    '动态规划入门': {
        'overview': (
            '动态规划（Dynamic Programming，DP）是一种通过将原问题分解为重叠子问题来求解最优化的算法范式。'
            'DP 适用于具有两大特性的问题：最优子结构（最优解可由子问题最优解构造）和重叠子问题（同一子问题被多次递归调用）。'
            'DP 的核心三要素：状态定义（dp[i] 或 dp[i][j] 代表什么）、状态转移方程（如何从已知状态推导新状态）、'
            '边界初始化（dp[0]、dp[*][0] 等基础状态的值）。经典例子包括斐波那契数列、0/1 背包、最长公共子序列等。'
        ),
        'concepts': ['状态定义', '状态转移方程', '最优子结构', '重叠子问题', '记忆化搜索', '自底向上', '空间优化'],
        'errors': [
            ('错误一：状态定义不清晰导致转移方程无法写出',
             '最常见的问题是"不知道 dp[i] 应该代表什么"。正确的思考顺序是：先明确问题的决策变量（哪些是可控的），'
             '再用这些变量定义状态。例如 0/1 背包中决策变量是"考虑了前几件物品"和"剩余容量"，'
             '所以状态自然定义为 dp[i][w] = 前 i 件物品在容量 w 下的最大价值。先定状态再写方程。'),
            ('错误二：忘记初始化 dp 边界导致错误结果',
             'dp[0][*] 和 dp[*][0] 的初始值通常为 0（表示空集或零容量），但某些问题的边界值不是 0——'
             '例如最长递增子序列中 dp[i] 的初始值应为 1（每个元素自身构成长度为 1 的递增子序列）。'
             '在写转移方程之前必须明确所有边界值的含义和数值。'),
            ('错误三：空间优化时循环方向写反',
             '0/1 背包的一维 dp 优化要求内层循环从 W 向 0 反向遍历——正向遍历等价于完全背包（物品可无限选取）。'
             '验证方法：用 n=1, wt=[2], val=[10], W=4 分别用正向和反向遍历测试，正向输出 20（选了两次），反向输出 10（只能选一次）。'),
        ],
        'practice': [
            '基础题：实现斐波那契数列的三种解法——(1) 朴素递归 O(2^n)、(2) 记忆化搜索 O(n)、(3) 自底向上 DP O(n)。用 n=30 测试，记录各自的运行时间，感受指数 vs 线性的巨大差异。',
            '进阶：实现最长公共子序列（LCS）的 DP 解法——dp[i][j] = 前 i 个字符和前 j 个字符的 LCS 长度。若 s1[i-1]==s2[j-1] 则 dp[i][j]=dp[i-1][j-1]+1，否则 dp[i][j]=max(dp[i-1][j], dp[i][j-1])。回溯 dp 表输出 LCS 字符串本身。',
        ],
        'project_idea': '实现 0/1 背包问题求解器——同时支持自底向上 DP（二维表格）和记忆化搜索（递归 + memo），读取 JSON 格式的物品列表和容量，输出最大价值和选中物品列表。包含一维空间优化版本，对比三种实现的运行时间和内存占用。',
    },
    '综合项目实践': {
        'overview': (
            '综合项目实践是将多个数据结构与算法知识点融会贯通的应用环节。不同于单一知识点的练习，'
            '综合项目要求在有限的约束条件（时间、空间、正确性）下做出合理的架构设计和算法选择。'
            '典型的综合项目包括：设计一个搜索引擎索引、实现一个简易数据库查询引擎、构建路径规划系统等。'
            '成功完成综合项目的关键不在于写出最精巧的代码，而在于能清晰阐述"为什么选这个数据结构而不是那个"。'
        ),
        'concepts': ['需求分析', '架构设计', '数据结构选型', '算法集成', '性能测试', '代码组织'],
        'errors': [
            ('错误一：过早优化——在需求明确之前就纠结底层数据结构的微优化',
             '在项目初期，先实现一个能跑通的功能版本（哪怕用最简单的数据结构），再通过性能测试确定真正的瓶颈所在。'
             '例如先用 Python 的 list 实现功能，如果 profile 显示查找是瓶颈，再替换为 dict 或 set。避免"为了用 AVL 树而用 AVL 树"。'),
            ('错误二：忽视边界条件和错误处理',
             '实际项目中的输入可能是空文件、格式错误、极端规模（n=0 或 n=10⁶），没有防御性代码会导致程序崩溃。'
             '正确做法：每个模块的入口都有输入校验，边界情况至少用 if-else 显式处理，而非依赖"好像不会发生"的假设。'),
        ],
        'practice': [
            '综合项目：设计一个简单的拼写检查器——读取词典文件构建 Trie（前缀树），对输入文本中的每个单词检查是否存在于字典中，对不存在的单词输出最相似的候选词（编辑距离）。涉及 Trie 的插入和查找、动态规划（编辑距离）、字符串处理。',
        ],
        'project_idea': '设计一个"公交线路规划器"：用图表示城市公交网络（节点=站点，边=公交线路连接），实现以下功能：(1) 最少换乘方案（BFS 以换乘次数为距离）；(2) 最短时间方案（Dijkstra 以行驶时间+换乘时间之和为权重）；(3) 所有可达站点查询（从指定站点出发的 DFS）。这是数据结构课程综合项目的经典选题。',
    },
}


def _build_type_sections(resource_type: str, module: str, topic: str, lang: str) -> list[dict]:
    """Build module-aware, type-specific sections for fallback resources.

    Uses _MODULE_CONTENT to produce topic-relevant content rather than
    f-string-templated generic text. Falls back gracefully for unknown modules.
    """
    display = _topic_display_name(topic)
    code_info = build_language_specific_code_example(topic, lang)
    mc = _MODULE_CONTENT.get(module, {})

    if resource_type == '图解讲解':
        overview = mc.get('overview', f'围绕"{display}"的核心概念与基本原理展开深度讲解。通过图示化的方式帮助学习者建立直观理解，是学习数据结构的重要基础内容。')
        concepts = mc.get('concepts', [display, module])
        sections = [
            {'kind': 'highlight', 'heading': f'{display} — 核心要点',
             'content': overview},
            {'kind': 'example', 'heading': f'{display} — 具体示例说明',
             'content': mc.get(
                 'example_text',
                 f'以具体的场景和数据演示"{display}"的完整执行过程。'
                 f'通过一步步追踪数据变化，让抽象的概念变得可感知、可验证。'
                 f'建议跟随示例手动模拟一遍，加深对核心机制的理解。'
             )},
            {'kind': 'steps', 'heading': f'{display} — 分步骤拆解',
             'steps': mc.get('visual_steps', [
                 f'第一步：理解{display}的基本定义和核心数据结构——明确输入是什么、输出是什么，以及中间涉及的数据结构（{", ".join(concepts[:3])}等）',
                 f'第二步：通过具体示例观察{display}的逐步执行——在纸上或调试器中跟踪每一步的数据变化，特别注意变量的更新顺序和条件的判断时机',
                 f'第三步：手动模拟{display}的关键步骤——脱离代码，用纸笔复现算法的完整流程，这是检验是否真正理解的最高效方法',
                 f'第四步：总结{display}的适用场景和局限性——明确"什么时候应该用它"和"什么时候不该用它"，这比会写代码本身更重要',
                 f'第五步：与相关概念进行对比——将{display}与{module}中的其他相关概念进行对比分析，理解各自的优劣和选择依据',
             ])},
            {'kind': 'table', 'heading': f'{display} — 核心概念与对比分析',
             'content': mc.get('compare_table',
                               f'{display}与{module}中相关概念的对比分析表。'
                               f'通过结构化对比的方式帮助学习者快速建立知识网络，理解不同概念之间的关系和边界。'
             )},
            {'kind': 'warnings', 'heading': f'{display} — 常见误区与注意事项',
             'content': mc.get('errors', [{'heading': '', 'body': ''}])[0][1] if mc.get('errors') and len(mc['errors']) > 0 else
                        f'学习{display}时最常见的误区包括：混淆核心概念的定义边界、忽略边界条件的处理、'
                        f'在不适用的场景下套用该算法。建议对照{module}的标准教材逐一排查。'},
            {'kind': 'practice', 'heading': '即时练习',
             'content': mc.get('practice', ['', ''])[0] if mc.get('practice') and len(mc['practice']) > 0 else
                        f'请用自己的话解释{display}的核心原理，并举一个具体的应用场景。然后手动模拟一遍该算法在简单输入上的执行过程。'},
            {'kind': 'answer_hint', 'heading': '练习提示与检查要点',
             'content': mc.get('practice', ['', ''])[1] if mc.get('practice') and len(mc['practice']) > 1 else
                        f'检查要点：(1) 你的解释中是否准确使用了{module}的专业术语？'
                        f'(2) 手动模拟的每一步是否与代码的逻辑一致？(3) 能否举出至少一个{display}不适用的反例场景？'},
        ]
        if code_info:
            sections.insert(3, {'kind': 'code', 'heading': code_info['heading'],
                                'content': code_info['code'], 'language': code_info['language']})

    elif resource_type == '代码示例':
        sections = [
            {'kind': 'highlight', 'heading': f'{display} — 代码整体说明',
             'content': mc.get(
                 'code_overview',
                 f'以下代码展示了{display}的完整{lang}实现。代码涵盖了核心逻辑、边界条件处理和典型测试用例，'
                 f'属于{module}模块中最重要的编码实践之一。建议先通读一遍代码建立整体印象，再对照步骤详解逐段深入理解。'
             )},
        ]
        if code_info:
            sections.append({'kind': 'code', 'heading': code_info['heading'],
                             'content': code_info['code'], 'language': code_info['language']})
        sections += [
            {'kind': 'steps', 'heading': '代码逐段详解',
             'steps': [
                 f'第1段：数据结构定义——代码中定义了哪些关键数据结构（如类、结构体、数组）？每个字段的含义和初始值是什么？理解数据结构是理解后续算法逻辑的前提',
                 f'第2段：函数入口与参数——主函数的签名是什么？每个参数代表什么含义？输入的数据范围有何约束（如 n≥0、元素大于 0 等）？这些约束决定了边界条件的设计',
                 f'第3段：核心算法逻辑——追踪主循环或递归体的执行流程。重点理解循环终止条件、变量的更新规则、以及为什么这个顺序（而非其他顺序）能够正确解决问题',
                 f'第4段：边界条件处理——代码在哪些地方做了防御性检查（如空数组判断、nullptr 检查、索引越界保护）？如果去掉这些检查，在什么输入下程序会崩溃？',
                 f'第5段：测试用例与验证——代码末尾的 main 函数或测试块覆盖了哪些典型场景？能否再补充 1-2 个边界测试用例（如 n=0、全部相等、退化为链表等情况）？',
             ]},
            {'kind': 'complexity', 'heading': '时间复杂度与空间复杂度分析',
             'content': f'分析{display}的时间复杂度和空间复杂度。说明最优情况、最差情况和平均情况下的复杂度特征，'
                        f'以及复杂度的推导依据（不能只给 O(N) 而不说明为什么）。'
                        f'如果存在退化场景（如树退化为链表、重复元素过多导致 hash 冲突），请单独说明退化后的复杂度变化。'},
            {'kind': 'warnings', 'heading': '注意事项一：边界条件的处理',
             'content': mc.get('errors', [('', '')])[0][1] if mc.get('errors') and len(mc['errors']) > 0 else
                        f'最常见的严重错误是忽略{display}的边界情况（空输入、单元素、所有元素相同等）。'
                        f'正确做法：在写核心逻辑之前，先列出所有可能的边界情况并写出相应的处理分支。'},
            {'kind': 'warnings', 'heading': '注意事项二：常见编码错误',
             'content': mc.get('errors', [('', ''), ('', '')])[1][1] if mc.get('errors') and len(mc['errors']) > 1 else
                        f'在{display}的代码实现中，循环条件、指针偏移和返回值处理是最容易出错的地方。'
                        f'建议每次写完代码后，用至少 3 组不同类型的输入进行测试验证。'},
            {'kind': 'warnings', 'heading': '注意事项三：性能与语言特性',
             'content': mc.get('errors', [('', ''), ('', ''), ('', '')])[2][1] if mc.get('errors') and len(mc['errors']) > 2 else
                        f'在{lang}中实现{display}时，应注意语言特性对性能的影响。'
                        f'例如递归深度限制、内存分配开销、STL/标准库的使用技巧等。'},
            {'kind': 'practice', 'heading': '变式练习',
             'content': f'练习：基于上述{display}的代码，完成以下修改——(1) 调整核心条件以适应新的约束场景；'
                        f'(2) 将递归版改写为迭代版（或反之），比较两种实现的性能和可读性；'
                        f'(3) 用另一组不同的测试数据验证两种实现的输出是否完全一致。'},
            {'kind': 'next_action', 'heading': '延伸学习建议',
             'content': f'学完{display}的代码实现后，建议按以下顺序继续学习：'
                        f'(1) 用不同的输入参数反复测试代码，确保理解每个分支的执行路径；'
                        f'(2) 将{display}与{module}中的其他相关算法做横向对比——它们解决的是同一类问题吗？什么时候该选哪个？'
                        f'(3) 挑战该知识点的变种题目，用刚学到的代码框架去解决新的问题场景。'},
        ]

    elif resource_type == '易错点':
        errors = mc.get('errors', [])
        sections = [
            {'kind': 'highlight', 'heading': f'{display} — 高频错误类别概述',
             'content': mc.get('overview', f'聚焦"{display}"中最常见、最高频的几个易错场景。'
                                           f'每个错误都包含具体的错误现象、根因分析和正确做法，'
                                           f'帮助学习者在学习阶段就建立正确的认知框架，避免在实践中反复踩坑。'),
            },
        ]
        for i, (title, body) in enumerate(errors[:4]):
            sections.append({'kind': 'warnings', 'heading': title, 'content': body})
        # Fill up to 4 warnings if needed
        if len(errors) < 1:
            sections.append({'kind': 'warnings', 'heading': f'常见错误一：{display}的边界条件遗漏',
                             'content': f'在{display}中，边界条件（如空输入、单元素、最大/最小值边界）的遗漏是最常见的错误。'
                                        f'务必在实现前用纸笔列出所有可能的边界情况，并在代码中逐一处理。'})
        if len(errors) < 2:
            sections.append({'kind': 'warnings', 'heading': f'常见错误二：{display}的循环条件和终止条件',
                             'content': f'循环的终止条件写错（如 < vs <=、and vs or）会导致死循环或遗漏元素。'
                                        f'建议用最小的测试用例（如 n=1 或 n=2）进行单步调试验证。'})
        if len(errors) < 3:
            sections.append({'kind': 'warnings', 'heading': f'常见错误三：{display}的数据结构选型错误',
                             'content': f'使用不适合的数据结构会导致程序在特定输入下性能退化（如 O(n)→O(n²)）。'
                                        f'理解每种数据结构的操作复杂度是避免此类错误的根本方法。'})
        if len(errors) < 4:
            sections.append({'kind': 'warnings', 'heading': f'常见错误四：{display}的递归或迭代实现缺陷',
                             'content': f'递归版本忘记基准情形会导致栈溢出，迭代版本忘记更新循环变量会导致死循环。'
                                        f'两种实现方式各有陷阱，掌握标准模板是最可靠的防错方法。'})
        sections += [
            {'kind': 'compare', 'heading': f'{display} — 错误写法与正确写法对比',
             'content': f'对比{display}的常见错误实现与正确实现——重点展示两者在关键分支条件上的差异。'
                        f'理解"为什么这个看似微小的差别会导致完全不同的结果"是真正掌握{display}的标志。'
                        f'建议将错误版本的代码输入调试器，单步执行观察变量值的变化，加深对正确逻辑的理解。'},
            {'kind': 'example', 'heading': '具体犯错场景',
             'content': f'以一个具体的代码片段或场景演示{display}中常见的犯错过程——'
                        f'展示在哪些输入条件下错误会被触发、程序的错误表现是什么（崩溃/死循环/错误输出），'
                        f'以及如何从错误表现反推定位到根因。'},
            {'kind': 'text', 'heading': '为什么会错 / 错在哪里 / 如何避免',
             'content': f'分析人在学习{display}时为什么会犯这些错误——是概念理解偏差、代码习惯问题还是对边界条件的敏感度不足。'
                        f'给出可操作的改进建议：(1) 背诵经过验证的标准模板；(2) 用"测试三件套"覆盖最常见边界；'
                        f'(3) 理解核心不变量，每次修改代码前在脑内用不变量验证。'},
            {'kind': 'practice', 'heading': '判断纠错练习',
             'content': f'给出 2 段包含错误的{display}代码（错误包括：条件判断缺失、循环条件错误、变量更新遗漏等），'
                        f'要求学习者找出错误位置、描述错误原因并写出修复后的正确代码。'
                        f'这是检验是否真正理解（而不仅仅是能写出代码）的最有效自测方式。'},
            {'kind': 'answer_hint', 'heading': '纠错练习提示与参考答案',
             'content': f'提示：用{module}中的最小测试用例逐行追踪代码执行，对比预期值和实际值的差异来定位错误。'
                        f'参考答案中展示了每处错误的修复方法和修复后应得的正确输出结果。'},
        ]

    elif resource_type == '分层练习':
        practice = mc.get('practice', ['', ''])
        sections = [
            {'kind': 'highlight', 'heading': f'{display} — 分层练习整体说明',
             'content': f'本练习集围绕"{display}"（{module}模块）按三个层次递进设计：'
                        f'基础层侧重概念理解和基本操作；进阶层侧重综合应用和多知识点联动；提高层侧重优化和思维拓展。'
                        f'完成全部练习后，应能熟练应对该知识点在面试和考试中的常见变体。'},
            {'kind': 'practice', 'heading': '基础层练习',
             'content': practice[0] if len(practice) > 0 else
                        f'基础题1：用自己的话解释{display}的核心原理，并写出一个最简实现（不关注性能，只验证正确性）。\n'
                        f'基础题2：手动模拟{display}在一个小规模输入上的完整执行过程，每步标注关键变量的值。'},
            {'kind': 'answer_hint', 'heading': '基础层提示',
             'content': f'基础层提示：{display}的关键在于理解其核心数据结构和基本操作流程。'
                        f'如果概念理解有困难，建议先回顾{module}的教材对应章节，确保每个术语的含义清晰后再动手实现。'},
            {'kind': 'practice', 'heading': '进阶层练习',
             'content': practice[1] if len(practice) > 1 else
                        f'进阶1：在基础实现之上加入优化（如空间优化、时间优化），对比优化前后的性能差异。\n'
                        f'进阶2：将{display}与{module}中另一个相关算法结合，解决一个综合性问题。'},
            {'kind': 'answer_hint', 'heading': '进阶层提示',
             'content': f'进阶层提示：优化时先明确当前实现的瓶颈在哪里（时间 or 空间？哪个操作最耗费资源？），再针对性地改进。'
                        f'不要为了"看起来更高级"而引入不必要的复杂度和性能开销。'},
            {'kind': 'practice', 'heading': '提高层练习',
             'content': f'提高题：将{display}应用到实际场景问题中—设计算法解决一个具体的工程问题，'
                        f'要求包含完整的输入定义、算法设计、复杂度分析和边界情况讨论。'
                        f'如果能给出至少 2 种不同的解法并对比优劣，将达到提高层的满分标准。'},
            {'kind': 'answer_hint', 'heading': '提高层提示',
             'content': f'提高层提示：这道题没有唯一的标准答案——评分标准在于"你的方案是否完整、正确、高效"。'
                        f'建议先用暴力方法给出一个正确但低效的解（建立基线），再思考如何优化到更优的复杂度。'},
            {'kind': 'check_criteria', 'heading': '每层达标检查标准',
             'content': f'基础层达标：能准确描述{display}的概念和适用场景，能独立写出核心代码并通过简单测试。\n'
                        f'进阶层达标：能在给定问题场景下选择正确的算法实现，能在有限时间内完成代码编写和调试。\n'
                        f'提高层达标：能独立分析算法的复杂度瓶颈，能给出至少一种优化方案并实现验证，能阐述设计决策的依据。'},
            {'kind': 'warnings', 'heading': '练习中的常见陷阱',
             'content': f'陷阱1（过早看答案）：在没有独立思考之前就看答案提示，会严重削弱练习效果。建议至少独立思考 15-20 分钟后再看提示。\n'
                        f'陷阱2（只做题不总结）：做完题后不总结犯过的错误和学习到的新技巧，下次遇到类似问题仍然会犯同样的错。\n'
                        f'陷阱3（忽略时间复杂度）：只关注代码能否通过示例测试，不分析算法在面对大规模输入时的性能表现——这是面试中会被重点考察的维度。'},
            {'kind': 'next_action', 'heading': '完成练习后的学习路径',
             'content': f'完成{display}的三层练习后，建议进入{module}的下一个知识模块继续递进学习。'
                        f'保持"学一个新知识点→做三层练习→回顾总结→继续下一个"的学习节奏，是最有效的长期学习策略。'},
        ]

    elif resource_type == '项目案例':
        sections = [
            {'kind': 'task', 'heading': f'项目概述：基于{display}的实践项目',
             'content': mc.get('project_idea',
                               f'设计一个围绕"{display}"的实践项目。'
                               f'综合运用{module}的核心知识与编程技能，完成从需求分析到代码实现的完整流程。'
                               f'项目应包含明确的功能目标、输入输出规范和性能约束。'),
            },
            {'kind': 'steps', 'heading': '第一阶段：需求分析与设计',
             'steps': [
                 f'步骤1：明确项目目标——这个项目要解决什么问题？使用者是谁？输入和输出分别是什么？',
                 f'步骤2：设计数据结构——根据需求选择合适的数据结构（数组/链表/树/图/哈希表等），说明选型理由',
                 f'步骤3：设计算法流程——画出核心逻辑的流程图或伪代码，明确各模块的接口和交互方式',
                 f'步骤4：规划测试方案——设计至少 5 组测试用例，覆盖正常情况和边界情况',
             ]},
            {'kind': 'steps', 'heading': '第二阶段：代码实现',
             'steps': [
                 '步骤5：搭建项目框架——定义类/结构体/函数签名，编写模块间的接口桩代码',
                 '步骤6：实现核心功能——按流程图逐步实现关键算法，每完成一步就运行测试验证',
                 '步骤7：集成与调试——将所有模块组装到一起，运行完整测试用例并修复发现的 bug',
             ]},
            {'kind': 'design', 'heading': '架构与数据结构设计说明',
             'content': f'阐述本项目选择的数据结构和算法的设计依据。'
                        f'说明核心数据结构（如数组、链表、树、图、哈希表等）的选择理由——'
                        f'为什么选这个而非那个？时间和空间的权衡点在哪里？'
                        f'描述模块划分方案和各模块的职责边界。'},
            {'kind': 'warnings', 'heading': '常见实现风险一：边界条件遗漏',
             'content': f'实际项目中容易忽略的边界情况包括：输入为空、数据量达到上限、异常输入格式等。'
                        f'建议在每个模块的入口处添加输入校验逻辑，并在集成测试阶段专门测试边界场景。'},
            {'kind': 'warnings', 'heading': '常见实现风险二：性能瓶颈未提前评估',
             'content': f'在项目初期就应预估输入规模和数据特征，据此选择合适的数据结构和算法。'
                        f'如果输入规模可能达到 10⁵ 或更大，O(n²) 的算法需要在设计阶段就被排除。'},
            {'kind': 'next_action', 'heading': '项目拓展方向',
             'content': f'完成基础版本后，建议从以下方向拓展项目：(1) 添加持久化功能（读写文件/数据库）；'
                        f'(2) 实现命令行或 Web 界面；(3) 引入并发或多用户支持；(4) 对比不同实现方案的性能差异。'
                        f'将项目代码和设计文档整理后放在 GitHub 上，这是面试简历上的重要加分项。'},
        ]
        if code_info:
            sections.insert(3, {'kind': 'code', 'heading': f'参考代码框架（{lang}）',
                                'content': code_info['code'], 'language': code_info['language']})

    else:
        sections = [{'kind': 'text', 'heading': display,
                     'content': f'关于"{display}"（{module}模块）的学习资源。内容覆盖核心概念、代码示例和练习指导。'}]

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


# ═══════════════════════════════════════════════════════════════════
# Phase 3C-2: Depth validation + enrichment
# ═══════════════════════════════════════════════════════════════════

_VALIDATION_RULES: dict[str, dict] = {
    '图解讲解': {
        'highlight': 40, 'example': 80, 'steps_count': 5, 'steps_each': 40,
        'table': 150, 'warnings_count': 2, 'warnings_each': 35,
        'practice': 80, 'answer_hint': 50, 'min_sections': 7,
    },
    '代码示例': {
        'highlight': 40, 'code_lines': 20, 'steps_count': 5, 'steps_each': 45,
        'complexity': 60, 'warnings_count': 3, 'warnings_each': 35,
        'practice': 80, 'next_action': 60, 'min_sections': 7,
    },
    '易错点': {
        'warnings_count': 4, 'warnings_each': 40, 'example': 100,
        'text': 180, 'practice': 80, 'answer_hint': 60, 'min_sections': 7,
    },
    '分层练习': {
        'highlight': 40, 'practice_each': 100, 'answer_hint_count': 3,
        'warnings_count': 3, 'next_action': 80, 'min_sections': 7,
    },
    '项目案例': {
        'task': 120, 'steps_count': 6, 'steps_each': 45, 'text': 180,
        'code_lines': 25, 'warnings_count': 3, 'next_action': 100, 'min_sections': 7,
    },
}

_QUICKSORT_KEYWORDS = ['快速排序', '稳定性', '不稳定排序']

# Allowed section kinds per resource type — any kind not in this set is stripped
_ALLOWED_KINDS_BY_TYPE: dict[str, set[str]] = {
    '代码示例': {'highlight', 'code', 'steps', 'complexity', 'warnings', 'warning', 'practice', 'next_action'},
    '图解讲解': {'highlight', 'example', 'steps', 'table', 'compare', 'text', 'warnings', 'warning', 'practice', 'answer_hint', 'code'},
    '易错点': {'highlight', 'warnings', 'warning', 'compare', 'example', 'text', 'practice', 'answer_hint', 'code'},
    '分层练习': {'highlight', 'practice', 'answer_hint', 'check_criteria', 'warnings', 'warning', 'next_action'},
    '项目案例': {'task', 'steps', 'design', 'text', 'code', 'warnings', 'warning', 'next_action'},
}

# Patterns that trigger forced topic-specific enrichment regardless of depth
_FORBIDDEN_CONTENT = [
    '???????', 'O(?)', 'TODO', '示例待补充',
    '相关概念A', '相关概念B', '低/中/高',
    '核心思想 | 基于递归与调用栈的核心操作模式',
]


def _find_sec(sections, kind):
    """Find all sections with given kind."""
    return [s for s in (sections or []) if isinstance(s, dict) and s.get('kind') == kind]


def _sec_content(sec):
    """Extract content string from a section dict."""
    if not isinstance(sec, dict):
        return ''
    return sec.get('content', '') or ''


def validate_resource_depth(card, gen_context):
    """
    Validate per-type hard minimum content standards (Phase 3C-2).
    Returns dict with keys: passed (bool), issues (list[str]), thin_kinds (list[str]).
    """
    rtype = card.get('type', '')
    sections = card.get('sections', []) or []
    topic = gen_context.get('topic', '')
    rules = _VALIDATION_RULES.get(rtype)
    issues = []
    thin = []

    if not rules:
        return {'passed': True, 'issues': [], 'thin_kinds': []}

    def cn(kind):
        return _count_cn(''.join(_sec_content(s) for s in _find_sec(sections, kind)))

    # ── Common checks across types ──
    min_sec = rules.get('min_sections', 0)
    if len(sections) < min_sec:
        issues.append('sections 总数 ' + str(len(sections)) + ' < ' + str(min_sec))

    # ── Type-specific checks ──
    if rtype == '图解讲解':
        if cn('highlight') < 40:
            issues.append('highlight 不足 40 个中文字符'); thin.append('highlight')
        if cn('example') < 80:
            issues.append('example 不足 80 个中文字符'); thin.append('example')
        steps = []
        for ss in _find_sec(sections, 'steps'):
            steps.extend(ss.get('steps', []) or [])
        if len(steps) < 5:
            issues.append('steps 不足 5 步'); thin.append('steps')
        else:
            bad = sum(1 for s in steps if _count_cn(s) < 40)
            if bad:
                issues.append('steps 中有 ' + str(bad) + ' 步不足 40 个中文字符'); thin.append('steps')
        best_table = max((cn(k) for k in ('table', 'compare', 'text')), default=0)
        if best_table < 150:
            issues.append('表格/对比/文字不足 150 个中文字符'); thin.append('table')
        warns = _find_sec(sections, 'warnings') + _find_sec(sections, 'warning')
        if len(warns) < 2:
            issues.append('warnings 不足 2 条'); thin.append('warnings')
        else:
            bad = sum(1 for w in warns if _count_cn(_sec_content(w)) < 35)
            if bad:
                issues.append('warnings 中有 ' + str(bad) + ' 条不足 35 个中文字符'); thin.append('warnings')
        if cn('practice') < 80:
            issues.append('practice 不足 80 个中文字符'); thin.append('practice')
        if cn('answer_hint') < 50:
            issues.append('answer_hint 不足 50 个中文字符'); thin.append('answer_hint')

    elif rtype == '代码示例':
        if cn('highlight') < 40:
            issues.append('highlight 不足 40 个中文字符'); thin.append('highlight')
        code_lines = sum(_count_lines(_sec_content(cs)) for cs in _find_sec(sections, 'code'))
        if code_lines < 20:
            issues.append('code 不足 20 行非空代码行 (当前=' + str(code_lines) + ')'); thin.append('code')
        steps = []
        for ss in _find_sec(sections, 'steps'):
            steps.extend(ss.get('steps', []) or [])
        if len(steps) < 5:
            issues.append('steps 不足 5 条'); thin.append('steps')
        else:
            bad = sum(1 for s in steps if _count_cn(s) < 45)
            if bad:
                issues.append('steps 中有 ' + str(bad) + ' 条不足 45 个中文字符'); thin.append('steps')
        if cn('complexity') < 60:
            issues.append('complexity 不足 60 个中文字符或无复杂度分析'); thin.append('complexity')
        warns = _find_sec(sections, 'warnings') + _find_sec(sections, 'warning')
        if len(warns) < 3:
            issues.append('warnings 不足 3 条'); thin.append('warnings')
        else:
            bad = sum(1 for w in warns if _count_cn(_sec_content(w)) < 35)
            if bad:
                issues.append('warnings 中有 ' + str(bad) + ' 条不足 35 个中文字符'); thin.append('warnings')
        if cn('practice') < 80:
            issues.append('practice 不足 80 个中文字符'); thin.append('practice')
        if cn('next_action') < 60:
            issues.append('next_action 不足 60 个中文字符'); thin.append('next_action')

    elif rtype == '易错点':
        warns = _find_sec(sections, 'warnings') + _find_sec(sections, 'warning')
        if len(warns) < 4:
            issues.append('易错点 warnings 不足 4 个 (当前=' + str(len(warns)) + ')'); thin.append('warnings')
        else:
            bad = sum(1 for w in warns if _count_cn(_sec_content(w)) < 40)
            if bad:
                issues.append('易错点 warnings 中有 ' + str(bad) + ' 条不足 40 个中文字符'); thin.append('warnings')
        compare_secs = _find_sec(sections, 'compare')
        has_three_col = False
        for cs in compare_secs:
            c = _sec_content(cs)
            if ('错误' in c and '正确' in c) or ('|' in c):
                has_three_col = True
        if not has_three_col:
            issues.append('compare 缺少错误/正确/纠正三列结构'); thin.append('compare')
        if cn('example') < 100:
            issues.append('example 不足 100 个中文字符'); thin.append('example')
        if cn('text') < 180:
            issues.append('text 不足 180 个中文字符'); thin.append('text')
        if cn('practice') < 80:
            issues.append('practice 不足 80 个中文字符'); thin.append('practice')
        if cn('answer_hint') < 60:
            issues.append('answer_hint 不足 60 个中文字符'); thin.append('answer_hint')
        # Special: quicksort stability counterexample
        if any(kw in topic for kw in _QUICKSORT_KEYWORDS):
            all_content = ''.join(_sec_content(s) for s in sections)
            if '3a' not in all_content or '3b' not in all_content:
                issues.append('缺少 [3a,2,3b,1] 稳定性反例演示'); thin.append('compare')

    elif rtype == '分层练习':
        if cn('highlight') < 40:
            issues.append('highlight 不足 40 个中文字符'); thin.append('highlight')
        practice_secs = _find_sec(sections, 'practice')
        thin_prac = sum(1 for ps in practice_secs if _count_cn(_sec_content(ps)) < 100)
        if thin_prac:
            issues.append('practice 中有 ' + str(thin_prac) + ' 组不足 100 个中文字符'); thin.append('practice')
        ah_secs = _find_sec(sections, 'answer_hint')
        if len(ah_secs) < 3:
            issues.append('answer_hint 不足 3 条 (当前=' + str(len(ah_secs)) + ')'); thin.append('answer_hint')
        chk = _find_sec(sections, 'check_criteria')
        if not chk:
            issues.append('缺少 check_criteria 达标标准'); thin.append('check_criteria')
        warns = _find_sec(sections, 'warnings') + _find_sec(sections, 'warning')
        if len(warns) < 3:
            issues.append('warnings 不足 3 条'); thin.append('warnings')
        if cn('next_action') < 80:
            issues.append('next_action 不足 80 个中文字符'); thin.append('next_action')

    elif rtype == '项目案例':
        if cn('task') < 120:
            issues.append('task 不足 120 个中文字符'); thin.append('task')
        steps = []
        for ss in _find_sec(sections, 'steps'):
            steps.extend(ss.get('steps', []) or [])
        if len(steps) < 6:
            issues.append('steps 不足 6 步 (当前=' + str(len(steps)) + ')'); thin.append('steps')
        else:
            bad = sum(1 for s in steps if _count_cn(s) < 45)
            if bad:
                issues.append('steps 中有 ' + str(bad) + ' 步不足 45 个中文字符'); thin.append('steps')
        code_lines = sum(_count_lines(_sec_content(cs)) for cs in _find_sec(sections, 'code'))
        if code_lines < 25:
            issues.append('code 不足 25 行 (当前=' + str(code_lines) + ')'); thin.append('code')
        warns = _find_sec(sections, 'warnings') + _find_sec(sections, 'warning')
        if len(warns) < 3:
            issues.append('warnings 不足 3 条'); thin.append('warnings')
        if cn('text') < 180:
            issues.append('text/design 不足 180 个中文字符'); thin.append('text')
        if cn('next_action') < 100:
            issues.append('next_action 不足 100 个中文字符'); thin.append('next_action')

    return {'passed': len(issues) == 0, 'issues': issues, 'thin_kinds': list(set(thin))}


# ═══════════════════════════════════════════════════════════════════
# Phase 3C-3: Semantic relevance validation
# ═══════════════════════════════════════════════════════════════════

_PLACEHOLDER_PATTERNS = ['???????', 'O(?)', 'xxx', 'XXX', 'TODO', '示例待补充', '请继续练习', '相关概念A', '相关概念B']
_IRRELEVANT_PATTERNS = ['策略模式', '负数处理', '核心思想 | 基于递归', 'factorial', 'fib_memo']

_WRONG_LANG_PATTERNS = {
    'C++': ['None', 'def ', 'elif ', 'print(', 'import ', 'from ', '#include <stdio.h>'],
    'C': ['class ', 'vector', 'cout', 'new ', 'delete ', 'public:', 'private:', '#include <iostream>'],
    'Java': ['#include', 'cout', 'printf(', 'malloc', 'free(', 'def ', 'import numpy'],
    'Python': ['#include', 'public class', 'cout', 'printf(', 'malloc', 'free(', 'System.out'],
}


def validate_resource_relevance(card, gen_context):
    """
    Phase 3C-3: Semantic relevance validation beyond length checks.
    Returns {passed: bool, issues: list[str]}.
    """
    rtype = card.get('type', '')
    topic = gen_context.get('topic', '')
    lang = gen_context.get('normalized_language', 'Python')
    module = gen_context.get('module', '')
    sections = card.get('sections', []) or []
    all_text = ' '.join(
        (s.get('content') or '') + ' ' + ' '.join(s.get('steps', []) or [])
        for s in sections if isinstance(s, dict)
    )

    issues = []

    # 1. Check topic keyword presence
    topic_keywords = topic.split('|') if '|' in topic else [topic] if topic else []
    # extract core terms from topic
    core_terms = _extract_core_terms(topic)
    missing_terms = [t for t in core_terms if t not in all_text]
    if missing_terms:
        issues.append('缺少主题关键词: ' + ', '.join(missing_terms[:3]))

    # 2. Check for placeholder/template residues
    for pat in _PLACEHOLDER_PATTERNS:
        if pat in all_text:
            issues.append('包含占位符或模板残留: ' + pat)

    # 3. Check for irrelevant generic content (unless topic matches)
    for pat in _IRRELEVANT_PATTERNS:
        if pat not in topic and pat in all_text:
            issues.append('包含与主题无关的模板内容: ' + pat)

    # 4. Check wrong-language content
    wrong_patterns = _WRONG_LANG_PATTERNS.get(lang, [])
    for pat in wrong_patterns:
        # Check in code sections specifically, and in non-code sections less strictly
        code_sections = [s for s in sections if s.get('kind') == 'code']
        other_sections = [s for s in sections if s.get('kind') != 'code']
        code_text = ' '.join(s.get('content', '') or '' for s in code_sections)
        other_text = ' '.join(s.get('content', '') or '' for s in other_sections)
        if pat in code_text:
            issues.append(lang + ' 代码段包含非' + lang + '内容: ' + pat)
        elif pat in other_text:
            issues.append('文本段包含非' + lang + '专属内容: ' + pat)

    # 5. Code example: code section language field must match
    if rtype == '代码示例':
        for s in sections:
            if s.get('kind') == 'code' and s.get('language') != lang:
                issues.append('code section 的 language 字段为 ' + str(s.get('language')) + '，期望 ' + lang)

    # 6. Type-specific semantic checks
    if rtype == '代码示例':
        if lang == 'C++':
            cpp_required = ['#include <iostream>', 'using namespace std', 'struct ', 'nullptr']
            code_all = ''.join(s.get('content', '') or '' for s in sections if s.get('kind') == 'code')
            missing_cpp = [r for r in cpp_required if r not in code_all]
            if missing_cpp:
                issues.append('C++ 代码缺少关键元素: ' + ', '.join(missing_cpp[:3]))

    elif rtype == '易错点':
        if any(kw in topic for kw in _QUICKSORT_KEYWORDS):
            if '3a' not in all_text or '3b' not in all_text:
                issues.append('快速排序稳定性反例缺失 [3a,2,3b,1]')

    return {'passed': len(issues) == 0, 'issues': issues}


def _extract_core_terms(topic):
    """Extract core searchable terms from a topic string."""
    terms = []
    if '二叉树' in topic:
        terms.append('二叉树')
        if '前序' in topic:
            terms.append('前序')
        if '中序' in topic:
            terms.append('中序')
        if '后序' in topic:
            terms.append('后序')
        if '层序' in topic:
            terms.append('层序')
        if '遍历' in topic:
            terms.append('遍历')
    elif '快速排序' in topic:
        terms.extend(['快速排序', 'partition', '不稳定'])
    elif 'BFS' in topic and 'DFS' in topic:
        terms.extend(['BFS', 'DFS', '广度', '深度'])
    elif 'BFS' in topic:
        terms.extend(['BFS', '广度优先', '队列'])
    elif 'DFS' in topic:
        terms.extend(['DFS', '深度优先', '栈'])
    elif '动态规划' in topic or 'DP' in topic:
        terms.extend(['动态规划', '状态', '转移'])
    elif '递归' in topic:
        terms.extend(['递归', '调用栈', '基准情形'])
    elif '二分' in topic:
        terms.extend(['二分', 'left', 'right', 'mid'])
    elif '散列' in topic or '哈希' in topic:
        terms.extend(['散列', '哈希', 'hash', '冲突'])
    elif '栈' in topic and '队列' in topic:
        terms.extend(['栈', '队列', 'LIFO', 'FIFO'])
    return terms


# ═══════════════════════════════════════════════════════════════════
# Topic-specific enrichment templates (Phase 3C-3)
# ═══════════════════════════════════════════════════════════════════

def _match_topic_key(topic):
    """Map topic string to enrichment key. Returns None if no specific template exists."""
    t = topic or ''
    if '二叉树' in t and ('前序' in t or '遍历' in t or 'tree' in t.lower()):
        return 'binary_tree_traversal'
    if '快速排序' in t or ('quicksort' in t.lower() and '不稳定' in t):
        return 'quicksort_stability'
    if ('BFS' in t or '广度优先' in t) and ('DFS' in t or '深度优先' in t):
        return 'bfs_dfs'
    if 'BFS' in t or '广度优先' in t:
        return 'bfs_dfs'
    if 'DFS' in t or '深度优先' in t:
        return 'bfs_dfs'
    if '动态规划' in t or 'DP' in t.lower() or 'dp' in t.lower().split():
        return 'dynamic_programming'
    if '递归' in t and ('调用栈' in t or '栈' in t):
        return 'recursion_stack'
    if '二分' in t and ('查找' in t or '搜索' in t):
        return 'binary_search'
    if '散列' in t or '哈希' in t:
        return 'hash_table'
    if '栈' in t and '队列' in t:
        return 'stack_queue'
    return None


# ── Topic: 二叉树前序遍历 / 代码示例 ──

def _enrich_preorder_code(card, gen_context):
    """Generate semantically-correct binary tree preorder code sections."""
    display = gen_context.get('topic', '二叉树前序遍历')
    lang = gen_context.get('normalized_language', 'C++')

    sections = []

    # highlight
    sections.append({
        'kind': 'highlight', 'heading': display + ' — 代码整体说明',
        'content': (
            '以下代码展示了二叉树前序遍历的完整 ' + lang + ' 实现。'
            '前序遍历的访问顺序是"根节点 → 左子树 → 右子树"，'
            '这是三种深度优先遍历中最基础也最直观的一种。'
            '代码定义了二叉树节点结构体和递归遍历函数，'
            '并提供了可直接编译运行的测试用例。'
            '重点理解：(1) 递归函数的入口和出口；(2) 根/左/右的访问顺序为何不可颠倒；'
            '(3) nullptr 作为递归边界的必要性。'
        ),
    })

    # code — language-specific
    if lang == 'C++':
        code_text = (
            '#include <iostream>\n'
            'using namespace std;\n'
            '\n'
            '// 二叉树节点定义\n'
            'struct TreeNode {\n'
            '    int val;\n'
            '    TreeNode *left, *right;\n'
            '    TreeNode(int v = 0, TreeNode* l = nullptr, TreeNode* r = nullptr)\n'
            '        : val(v), left(l), right(r) {}\n'
            '};\n'
            '\n'
            '// 前序遍历：根 → 左 → 右\n'
            'void preorder(TreeNode* root) {\n'
            '    if (root == nullptr) return;  // 递归边界：空节点直接返回\n'
            '    cout << root->val << " ";     // 第一步：访问根节点\n'
            '    preorder(root->left);         // 第二步：递归遍历左子树\n'
            '    preorder(root->right);        // 第三步：递归遍历右子树\n'
            '}\n'
            '\n'
            'int main() {\n'
            '    // 构建测试树:\n'
            '    //        1\n'
            '    //       / \\\n'
            '    //      2   3\n'
            '    //     / \\\n'
            '    //    4   5\n'
            '    TreeNode* root = new TreeNode(1,\n'
            '        new TreeNode(2, new TreeNode(4), new TreeNode(5)),\n'
            '        new TreeNode(3));\n'
            '    \n'
            '    cout << "前序遍历结果: ";\n'
            '    preorder(root);  // 期望输出: 1 2 4 5 3\n'
            '    cout << endl;\n'
            '    \n'
            '    return 0;\n'
            '}'
        )
    elif lang == 'C':
        code_text = (
            '#include <stdio.h>\n'
            '#include <stdlib.h>\n'
            '\n'
            'typedef struct TreeNode {\n'
            '    int val;\n'
            '    struct TreeNode *left, *right;\n'
            '} TreeNode;\n'
            '\n'
            'TreeNode* new_node(int v) {\n'
            '    TreeNode* n = (TreeNode*)malloc(sizeof(TreeNode));\n'
            '    n->val = v; n->left = n->right = NULL;\n'
            '    return n;\n'
            '}\n'
            '\n'
            'void preorder(TreeNode* root) {\n'
            '    if (root == NULL) return;\n'
            '    printf("%d ", root->val);\n'
            '    preorder(root->left);\n'
            '    preorder(root->right);\n'
            '}\n'
            '\n'
            'int main() {\n'
            '    TreeNode* root = new_node(1);\n'
            '    root->left = new_node(2);\n'
            '    root->right = new_node(3);\n'
            '    root->left->left = new_node(4);\n'
            '    root->left->right = new_node(5);\n'
            '    printf("前序遍历结果: ");\n'
            '    preorder(root);\n'
            '    printf("\\n");\n'
            '    return 0;\n'
            '}'
        )
    else:  # Java / Python
        code_text = (
            'class TreeNode:\n'
            '    def __init__(self, val=0, left=None, right=None):\n'
            '        self.val = val\n'
            '        self.left = left\n'
            '        self.right = right\n'
            '\n'
            'def preorder(root):\n'
            '    """前序遍历：根 → 左 → 右"""\n'
            '    if root is None:\n'
            '        return []\n'
            '    return [root.val] + preorder(root.left) + preorder(root.right)\n'
            '\n'
            '# 测试\n'
            '#        1\n'
            '#       / \\\n'
            '#      2   3\n'
            '#     / \\\n'
            '#    4   5\n'
            'tree = TreeNode(1,\n'
            '    TreeNode(2, TreeNode(4), TreeNode(5)),\n'
            '    TreeNode(3))\n'
            'print("前序遍历:", preorder(tree))  # [1, 2, 4, 5, 3]'
        ) if lang != 'Java' else (
            'class TreeNode {\n'
            '    int val;\n'
            '    TreeNode left, right;\n'
            '    TreeNode(int v) { val = v; }\n'
            '    TreeNode(int v, TreeNode l, TreeNode r) { val = v; left = l; right = r; }\n'
            '}\n'
            '\n'
            'public class PreorderTraversal {\n'
            '    // 前序遍历：根 → 左 → 右\n'
            '    static void preorder(TreeNode root) {\n'
            '        if (root == null) return;\n'
            '        System.out.print(root.val + " ");\n'
            '        preorder(root.left);\n'
            '        preorder(root.right);\n'
            '    }\n'
            '    \n'
            '    public static void main(String[] args) {\n'
            '        TreeNode root = new TreeNode(1,\n'
            '            new TreeNode(2, new TreeNode(4), new TreeNode(5)),\n'
            '            new TreeNode(3));\n'
            '        System.out.print("前序遍历: ");\n'
            '        preorder(root);  // 1 2 4 5 3\n'
            '    }\n'
            '}'
        )

    sections.append({
        'kind': 'code', 'heading': '二叉树前序遍历完整实现（' + lang + '）',
        'language': lang, 'content': code_text,
    })

    # steps — 5+ steps, each explaining preorder traversal specifically
    sections.append({
        'kind': 'steps', 'heading': '代码逐段详解',
        'steps': [
            '第1段：TreeNode 节点结构体——定义了二叉树的节点类型，包含 val（节点值）、left（左子节点指针）、right（右子节点指针）。构造函数支持创建节点时直接指定值和子树，nullptr 表示空子树。理解这个结构是理解整个遍历代码的前提。',
            '第2段：preorder 函数签名——void preorder(TreeNode* root) 表示该函数接收一个指向 TreeNode 的指针，无返回值（结果直接输出到屏幕）。root 参数代表当前子树的根节点——注意它可以是 nullptr，表示空树。',
            '第3段：递归边界 if (root == nullptr) return;——这是递归函数的第一行，也是最重要的保护语句。当遍历到叶子节点的下一层时，传入的 root 为 nullptr，直接返回避免空指针访问。如果忘记这一行，程序会在访问 root->val 时崩溃。',
            '第4段：访问根节点 cout << root->val——前序遍历的核心：在访问左右子树之前，先处理当前根节点。这里将节点值输出到屏幕。如果换成中序遍历（左→根→右），这一行应该放在两个递归调用之间；换成后序遍历（左→右→根），则放在最后。三种遍历的唯一区别就是这一行与两个递归调用的相对位置。',
            '第5段：preorder(root->left) 遍历左子树——递归调用自身处理左子树。递归的魔法在于：当你调用 preorder(root->left) 时，系统会在调用栈上压入一个新的栈帧，从 root->left 开始重新执行 preorder 的全部逻辑。这意味着左子树的每个节点也会按照"根→左→右"的顺序被访问，直到左子树全部处理完毕才返回。',
            '第6段：preorder(root->right) 遍历右子树——左子树完全处理完毕后，调用栈回退到当前节点，继续处理右子树。注意递归调用栈的后进先出特性：最先进入的根节点调用最后才返回，而最深的叶子节点调用最先返回。这正是"深度优先"的体现——优先深入而不是横向扩展。',
            '第7段：main 函数构建测试树——用 new 创建了一个包含 5 个节点的二叉树，结构为根节点 1，左子树 2（带 4 和 5），右子树 3。调用 preorder(root) 后期望输出 "1 2 4 5 3"。建议用纸笔画出这棵树，然后手动跟踪每次递归调用的参数和输出，验证你对调用栈的理解。',
        ],
    })

    # complexity
    sections.append({
        'kind': 'complexity', 'heading': '时间复杂度与空间复杂度分析',
        'content': (
            '时间复杂度：O(n)，其中 n 为二叉树的节点总数。'
            '每个节点恰好被访问一次——preorder 函数对每个节点执行一次 cout 操作，'
            '没有重复访问。即使二叉树退化为链表（每个节点只有左子节点或只有右子节点），'
            '时间复杂度仍然是 O(n)，因为每个节点依然只被访问一次。'
            '\n空间复杂度：O(h)，其中 h 为二叉树的高度。'
            '空间开销来自递归调用栈——递归的最大深度等于树的高度 h。'
            '在平衡二叉树中，h = log₂(n+1) ≈ O(log n)，空间开销很小。'
            '在最坏情况下（树退化为链表），h = n，空间复杂度退化为 O(n)。'
            '这也是递归实现的潜在风险：当 n 很大且树不平衡时，可能导致调用栈溢出。'
            '\n迭代实现的对比：如果用栈模拟递归实现前序遍历，空间复杂度同样为 O(h)，'
            '但显式栈避免了递归调用栈溢出的风险（受限于堆内存而非系统调用栈）。'
        ),
    })

    # warnings — all C++/tree specific
    sections.append({
        'kind': 'warnings', 'heading': '注意事项一：nullptr 空指针检查不可省略',
        'content': (
            '最常见的错误是忘记在 preorder 函数开头检查 root == nullptr。'
            '如果省略这个检查，当遍历到叶子节点的下一层时，root 为 nullptr，'
            '执行 root->val 会触发空指针解引用，导致程序崩溃（Segmentation Fault）。'
            '正确做法：递归函数的第一行永远是边界条件判断。'
            '测试方法：传入一个空树（preorder(nullptr)）验证程序不会崩溃。'
        ),
    })
    sections.append({
        'kind': 'warnings', 'heading': '注意事项二：前序/中序/后序的访问顺序容易混淆',
        'content': (
            '三种遍历的区别仅在于根节点的访问时机：'
            '前序=根→左→右（先访问根），中序=左→根→右（中间访问根），'
            '后序=左→右→根（最后访问根）。'
            '记忆口诀：前/中/后指的是根节点在第几个被访问。'
            '以同一棵树 [1,2,3,4,5] 验证三种遍历的输出——'
            '前序输出 1 开头，中序输出左子树值开头，后序输出 1 结尾。'
            '如果前序输出以左子树值开头，说明你错把中序当前序了。'
        ),
    })
    sections.append({
        'kind': 'warnings', 'heading': '注意事项三：递归过深导致调用栈溢出',
        'content': (
            '在 C++ 中，递归调用使用系统调用栈，默认大小通常为 1-8 MB。'
            '当二叉树退化为深度 10^5 的链表时，递归深度 = 10^5，'
            '每个栈帧约占用几十到上百字节，总空间可能超过调用栈上限，触发栈溢出。'
            '解决方案：(1) 改用显式栈的迭代实现（本练习的变式任务）；'
            '(2) 如果确定树是平衡的（如 AVL 树），递归实现是安全的；'
            '(3) 在竞赛/面试场景中，n ≤ 10^4 时递归通常安全，n ≥ 10^5 时建议用迭代。'
        ),
    })

    # practice — specific to binary tree preorder
    sections.append({
        'kind': 'practice', 'heading': '变式练习',
        'content': (
            '练习一（非递归实现）：将上述递归前序遍历改写为使用显式栈的迭代版本。'
            '要求：(1) 使用 std::stack<TreeNode*> 模拟递归调用栈；'
            '(2) 入栈顺序必须是"先右后左"——因为栈是 LIFO，后入栈的左子节点会先出栈，'
            '这就保证了左子树先于右子树被访问；(3) 用同样的测试树验证输出是否为 "1 2 4 5 3"。'
            '提示：初始化栈为 [root]，while 栈非空时弹出栈顶并访问，然后按先右后左入栈子节点。'
            '\n练习二（中序后序对比）：将上述代码分别改为中序遍历和后序遍历，'
            '只修改递归调用和 cout 的相对顺序。用同一棵测试树验证三种遍历的输出差异，'
            '并用纸笔画出每种遍历的访问路径（在树结构图上标注访问序号）。'
        ),
    })

    # next_action
    sections.append({
        'kind': 'next_action', 'heading': '学完前序遍历后的延伸学习路径',
        'content': (
            '建议按以下顺序继续学习：(1) 将前序递归改为非递归栈实现，'
            '这是验证你是否真正理解前序遍历与栈关系的标准方法——如果你能独立写完并通过测试，'
            '说明你对"根→左→右"和"栈后进先出"的关系已经建立清晰的直觉；'
            '(2) 对比前序、中序、后序三种遍历，用同一棵树画出每种遍历的访问路径和调用栈图——'
            '只有理解了三种遍历的代码差异仅在于一行代码的位置，才算真正掌握二叉树遍历；'
            '(3) 学习层序遍历（BFS），理解"深度优先 vs 广度优先"在二叉树上的体现——'
            '前序是 DFS 的一种，层序是 BFS，两者使用不同的数据结构（栈 vs 队列）；'
            '(4) 挑战 LeetCode 144（二叉树前序遍历）、94（中序）、145（后序），'
            '用递归和迭代两种方法各提交一次，对比运行时间和内存消耗。'
        ),
    })

    card['sections'] = sections
    return card


# ── Topic: 快速排序 why 不稳定 / 易错点 ──

def _enrich_quicksort_pitfalls(card, gen_context):
    """Generate quicksort stability-focused pitfalls content."""
    display = gen_context.get('topic', '快速排序为什么不稳定')
    lang = gen_context.get('normalized_language', 'Python')

    sections = []

    sections.append({
        'kind': 'highlight', 'heading': display + ' — 高频错误类别概述',
        'content': (
            '"快速排序为什么不稳定"是数据结构面试中最高频的追问之一。'
            '超过 70% 的候选人能写出快速排序代码，但只有不到 30% 能准确解释其不稳定性的根因。'
            '本资源聚焦于四个核心易错点：基准选择导致的退化、partition 边界条件、'
            '递归出口遗漏、以及最关键的——通过 [3a,2,3b,1] 反例演示稳定性破坏的完整过程。'
        ),
    })

    # 4+ warnings
    warnings_data = [
        ('易错点一：固定选首/尾元素作基准 → O(n²) 退化',
         '错误现象：固定选第一个或最后一个元素作 pivot，在已排序（或逆序）数组上每次 partition 只排除一个元素，'
         '递归深度 = n，总比较次数 ≈ n+(n-1)+...+1 = O(n²)，在 n=10^5 时远超时间限制。'
         '\n根因分析：理想的 pivot 应使左右子数组尽量均分（各约 n/2）。固定端点破坏了这一均衡性。'
         '\n正确做法：采用随机 pivot（随机选一个元素与末尾交换）或三数取中法（median-of-three），将退化概率降至极低。'),
        ('易错点二：partition 双指针的移动条件写错',
         '错误现象：while 循环中指针移动条件写成 arr[i] <= pivot（加了等号），导致全等数组 [5,5,5,5] 上指针无法移动，'
         '陷入无限循环或越界。或者忘记 while i <= j 的最终退出条件。'
         '\n根因分析：partition 核心不变量是"严格小于 pivot 的放左边，严格大于的放右边"，等于 pivot 的元素可放任意一侧。'
         '\n正确做法：内层 while 使用严格 < 和 >（不含等号）；外层 while 条件是 i <= j（含等号），保证指针交错后正确退出。'),
        ('易错点三：递归出口 if (low >= high) return; 遗漏',
         '错误现象：忘记写递归出口就直接调用 quicksort(arr, low, j) 和 quicksort(arr, i, high)，'
         '导致空子数组或单元素子数组继续无限递归，最终栈溢出。'
         '\n根因分析：快速排序有两个递归调用，容易在专注 partition 逻辑时忘记出口。'
         '\n正确做法：quicksort 函数的第一行（甚至第二行注释）必须是递归出口。测试用例应包含长度为 0、1、2 的数组。'),
        ('易错点四：不理解为什么快速排序不稳定',
         '错误现象：能写出快速排序但说不清它为什么不稳定，面试时被追问就卡壳。'
         '\n根因分析：稳定性要求"相等元素的相对顺序在排序前后不变"。快速排序的 partition 过程涉及跳跃式的远距离 swap，'
         '一个等于 pivot 的元素可能被换到很远的位置，与前面相等元素的相对顺序因此被破坏。'
         '\n正确理解：归并排序的 merge 在遇到相等元素时"优先取左半部分"，天然保持相对顺序，因此稳定。'
         '快速排序的 partition 无法做类似的保证——详见下方的 [3a,2,3b,1] 反例演示。'),
    ]
    for i, (title, body) in enumerate(warnings_data):
        sections.append({
            'kind': 'warnings', 'heading': title,
            'content': body,
        })

    # compare — stability counterexample [3a, 2, 3b, 1]
    sections.append({
        'kind': 'compare', 'heading': '稳定性反例演示 [3a, 2, 3b, 1]',
        'content': (
            '演示：快速排序为什么不稳定（Lomuto partition，以最后一个元素为基准）\n\n'
            '初始数组（相等元素 3 用编号 a/b 区分先后位置）：\n'
            '  索引: 0    1    2    3\n'
            '  元素: 3a   2    3b   1\n\n'
            '基准 pivot = arr[3] = 1（最后一个元素）\n\n'
            'partition 过程（变量 i 记录"小于 pivot 的最后一个位置"）：\n'
            '  i = -1（初始值）\n'
            '  j = 0: arr[0]=3a > 1  → 不交换，i 仍为 -1\n'
            '  j = 1: arr[1]=2  > 1  → 不交换，i 仍为 -1\n'
            '  j = 2: arr[2]=3b > 1  → 不交换，i 仍为 -1\n'
            '  j = 3: 循环结束，i+1=0，交换 arr[0] 和 arr[3]\n\n'
            '交换后数组：\n'
            '  索引: 0    1    2    3\n'
            '  元素: 1    2    3b   3a\n\n'
            '关键观察：\n'
            '- 排序前：3a（索引 0）在 3b（索引 2）的前面\n'
            '- 排序后：3b（索引 2）跑到了 3a（索引 3）的前面\n'
            '- 3a 和 3b 的值相等（都是 3），相对先后顺序发生翻转 → 排序不稳定\n\n'
            '为什么 3a 被换到 3b 后面？\n'
            'partition 将 arr[0]（3a）与 arr[3]（1）直接交换，3a 从数组最前面跳到了最后面——'
            '这个跳跃式 swap 跨越了 3b 所在的位置，无法保证 3a 和 3b 的相对顺序。'
            '这是 partition 机制的本质特征，无法通过调整 pivot 选择来修复。\n\n'
            '对比：归并排序的 merge 阶段在 arr1[i]==arr2[j] 时固定选 arr1[i]（左半部分），'
            '两个相等元素中原本在左边的仍然在左边，稳定性得到保证。'
        ),
    })

    # example
    sections.append({
        'kind': 'example', 'heading': '具体犯错场景',
        'content': (
            '场景一（面试手写代码）：面试官要求手写快速排序的 partition。候选人将 while 条件写成：\n'
            '  while (arr[i] <= pivot) i++;  // 错误！加了等号\n'
            '  while (arr[j] >= pivot) j--;  // 错误！加了等号\n'
            '测试输入 [5, 5, 5, 5]（全等数组）：i 和 j 都无法移动，导致无限循环或越界崩溃。\n'
            '修复：改为严格 < 和 >，让等于 pivot 的元素由后续的 i <= j 判断和 swap 处理。\n\n'
            '场景二（稳定性误解）：学生写完快速排序后声称它是稳定的，理由是"我把相等的元素放一起了"。\n'
            '用 [3a, 2, 3b, 1] 反例当场演示：输入包含两个相同的 3，输出中它们的相对顺序被翻转。\n'
            '学生才意识到"放一起"不等于"保持相对顺序"——稳定性关心的是原顺序，不是值是否相邻。'
        ),
    })

    # text — deep analysis
    sections.append({
        'kind': 'text', 'heading': '为什么会写错 / 错在哪里 / 如何避免',
        'content': (
            '为什么会错：partition 算法是"代码量不多但逻辑密度极高"的典型——双指针相向移动，'
            '每一行条件的微妙差异（< vs <=，i <= j vs i < j）都会导致完全不同的行为。'
            '人脑在追踪两个指针的同时移动和交换时容易出错，尤其在面试或考试的时间压力下。'
            '\n错在哪里：错误的本质是"分支条件的不完备"——没有覆盖所有可能的输入情况。'
            '例如 while (arr[i] < pivot) 不能处理 arr[i] == pivot 的情况，可能导致死循环；'
            'if (low >= high) return 缺少等号会漏掉长度为 1 的子数组。'
            '\n如何避免：(1) 背诵标准模板——快速排序的 partition 代码模式高度固定，'
            '直接背诵经过验证的标准实现是最可靠的应试策略；(2) 理解不变量——partition 过程中维护'
            '"[low..i] 全部 < pivot，[j..high] 全部 > pivot"这一核心不变量，'
            '每次修改代码前先在脑内用该不变量验证；(3) 测试三件套——每次写出 partition 后立即用'
            '已排序数组 [1,2,3,4]、逆序数组 [4,3,2,1]、全等数组 [5,5,5,5] 三个测试用例验证，'
            '这三者覆盖了绝大多数的边界条件错误。'
        ),
    })

    # practice
    sections.append({
        'kind': 'practice', 'heading': '判断纠错练习',
        'content': (
            '练习一：以下快速排序代码有 bug，请找出并写出修复方法——\n'
            'def broken_qs(arr):\n'
            '    if len(arr) <= 1: return arr\n'
            '    pivot = arr[0]  # 固定选第一个元素\n'
            '    left = [x for x in arr[1:] if x < pivot]\n'
            '    right = [x for x in arr[1:] if x > pivot]\n'
            '    return broken_qs(left) + [pivot] + broken_qs(right)\n'
            '（提示：等于 pivot 的元素去了哪里？这是稳定性问题还是正确性问题？）\n\n'
            '练习二：用 Python 内置的 sort() 和自己实现的 quicksort 分别对以下列表按第一个元素排序，'
            '观察两个版本中相等元素 (3,\'a\') 和 (3,\'c\') 的相对顺序变化：\n'
            '  data = [(3,\'a\'), (2,\'b\'), (3,\'c\'), (1,\'d\')]\n'
            '记录两种排序的输出结果，解释为什么 sort() 的输出中 (3,\'a\') 仍在 (3,\'c\') 前面，'
            '而 quicksort 的输出中可能相反。'
        ),
    })

    sections.append({
        'kind': 'answer_hint', 'heading': '纠错练习提示与参考答案',
        'content': (
            '练习一答案：等于 pivot 的元素（x == pivot）既没进 left 也没进 right，被直接丢弃了——'
            '排序后数组中所有等于原始 pivot 值（arr[0]）的元素只剩下 pivot 本身，其余全部丢失。'
            '这是正确性 bug，比稳定性 bug 更严重。修复方式之一：right 的条件改为 x >= pivot，'
            '或单独收集 equal = [x for x in arr if x == pivot] 然后在递归结果中拼接。'
            '\n练习二答案：Python 内置的 sort() 使用 Timsort 算法，是稳定的——'
            '(3,\'a\') 和 (3,\'c\') 的值（按第一个元素）相等，Timsort 保持输入中的先后顺序，'
            '因此 (3,\'a\') 仍在前。手写 quicksort 不稳定——partition 的 swap 可能将 (3,\'a\') 换到 (3,\'c\') 后面。'
            '这直接验证了快速排序的不稳定性。'
        ),
    })

    card['sections'] = sections
    return card


# ── Topic: BFS和DFS / 图解讲解 ──

def _enrich_bfs_dfs_visual(card, gen_context):
    """Generate BFS vs DFS visual explanation content."""
    display = gen_context.get('topic', 'BFS和DFS')
    lang = gen_context.get('normalized_language', 'C')

    sections = []

    sections.append({
        'kind': 'highlight', 'heading': display + ' — 核心要点',
        'content': (
            'BFS（广度优先搜索）和 DFS（深度优先搜索）是图遍历的两大基本策略。'
            'BFS 使用队列（FIFO）实现逐层扩展，天然适合求无权图的最短路径；'
            'DFS 使用栈（LIFO）或递归实现一条路走到黑再回溯，适合连通性检测和拓扑排序。'
            '二者的本质差异在于数据结构选择——队列 vs 栈——这直接决定了节点的访问顺序。'
            '理解 visited 数组的作用和标记时机（入队/入栈时标记 vs 出队/出栈时标记）是避免重复访问的关键。'
        ),
    })

    sections.append({
        'kind': 'example', 'heading': '具体示例：以 6 节点图为例',
        'content': (
            '以下用一个包含 6 个节点（编号 0-5）的无向图对比 BFS 和 DFS 的完整执行过程：\n\n'
            '图结构（邻接表表示）：\n'
            '  0 → [1, 2]\n'
            '  1 → [0, 3, 4]\n'
            '  2 → [0, 5]\n'
            '  3 → [1]\n'
            '  4 → [1, 5]\n'
            '  5 → [2, 4]\n\n'
            '从节点 0 出发——\n'
            'BFS 访问顺序（逐层）：0 → 1, 2 → 3, 4, 5\n'
            '  队列模拟：[0] → pop0 push1,2 → [1,2] → pop1 push3,4 → [2,3,4]'
            ' → pop2 push5 → [3,4,5] → pop3 → [4,5] → pop4 → [5] → pop5 → []\n'
            'DFS 访问顺序（深入到底）：0 → 1 → 3 → 4 → 5 → 2\n'
            '  栈模拟：[0] → pop0 push1,2 → [1,2] → pop1 push3,4 → [3,4,2]'
            ' → pop3 → [4,2] → pop4 push5 → [5,2] → pop5 → [2] → pop2 → []'
        ),
    })

    sections.append({
        'kind': 'steps', 'heading': 'BFS 执行步骤详解',
        'steps': [
            '步骤 1：初始化——创建 visited 数组（长度 6，全部 false）和队列 q。将起点 0 入队，同时标记 visited[0]=true。visited 标记必须在入队时完成，不能延迟到出队时——否则同一层的邻居节点可能重复入队。',
            '步骤 2：处理节点 0——出队 0，访问（记录到结果序列）。遍历 0 的邻居 [1,2]：1 未访问，入队并标记 visited[1]=true；2 未访问，入队并标记 visited[2]=true。此时队列 = [1,2]。',
            '步骤 3：处理节点 1——出队 1，访问。遍历 1 的邻居 [0,3,4]：0 已访问跳过；3 未访问，入队并标记 visited[3]=true；4 未访问，入队并标记 visited[4]=true。队列 = [2,3,4]。',
            '步骤 4：处理节点 2——出队 2，访问。遍历 2 的邻居 [0,5]：0 已访问跳过；5 未访问，入队并标记 visited[5]=true。队列 = [3,4,5]。',
            '步骤 5：依次出队 3,4,5——它们的邻居都已访问，无新节点入队。队列为空，BFS 结束。最终访问序列：[0,1,2,3,4,5]。',
        ],
    })

    sections.append({
        'kind': 'table', 'heading': 'BFS vs DFS 多维度对比',
        'content': (
            '比较维度 | BFS（广度优先搜索） | DFS（深度优先搜索）\n'
            '核心数据结构 | 队列（FIFO — 先进先出） | 栈（LIFO — 后进先出）或递归\n'
            '访问模式 | 逐层扩展，先访问距离起点近的节点 | 一条路走到底，再回溯换路\n'
            '时间复杂度 | O(V+E)，邻接表实现 | O(V+E)，邻接表实现\n'
            '空间复杂度 | O(w)，w = 图的最大宽度 | O(h)，h = 图的最大深度\n'
            '无权图最短路径 | 天然支持（首次访问时即最短） | 不支持，需要额外处理\n'
            'visited 标记时机 | 必须在入队时标记（避免重复入队） | 入栈时标记即可\n'
            '实现难度 | 需要显式维护队列 | 递归实现极简（3-5 行），迭代方式需栈\n'
            '适用问题 | 层序遍历、最短路径、N 度关系 | 连通性检测、环检测、拓扑排序、回溯\n'
            '典型题目 | LeetCode 102, 127, 200, 994 | LeetCode 78, 46, 207, 79'
        ),
    })

    sections.append({
        'kind': 'warnings', 'heading': '常见误区一：BFS 的 visited 在出队时才标记',
        'content': (
            '错误做法：在节点出队时标记 visited[node]=true。这会导致同一节点被重复入队——'
            '例如节点 A 有两个邻居 B 和 C，而 B 和 C 又都连着 D。当 B 和 C 在同一层时，'
            'B 出队时 D 入队（未标记），C 出队时 D 再次入队（仍未标记），队列中 D 出现两次。'
            '正确做法：在入队时就标记 visited，保证每个节点只入队一次。'
        ),
    })
    sections.append({
        'kind': 'warnings', 'heading': '常见误区二：DFS 递归过深导致栈溢出',
        'content': (
            '在退化为链表的图上（深度=10^5），递归 DFS 的调用栈深度=10^5，极易栈溢出。'
            'Python 默认递归限制约 1000，' + lang + ' 中系统调用栈约 1-8 MB。'
            '解决方案：(1) 改用显式栈的迭代 DFS；(2) 对于已知深度很大的图，优先选择迭代实现。'
            '面试中如不确定图深度，写迭代 DFS 更保险，多写几行代码但不会因栈溢出而失败。'
        ),
    })

    sections.append({
        'kind': 'practice', 'heading': '即时练习',
        'content': (
            '题目：给定一个 n×m 的二维字符网格 grid，\'1\' 表示陆地，\'0\' 表示水域，'
            '上下左右相邻的陆地组成一个岛屿。分别用 BFS 和 DFS 计算岛屿数量（LeetCode 200）。\n'
            '要求：(1) 先用 BFS 实现——用队列存储坐标对 (r,c)，四个方向用数组表示；'
            '(2) 再用 DFS 实现——递归进入四个方向，边界是越界或遇到 \'0\'/已访问；'
            '(3) 对比两种实现的空间占用差异：BFS 的队列最大为 O(min(n,m))，DFS 的递归栈最深为 O(n×m)。'
        ),
    })

    sections.append({
        'kind': 'answer_hint', 'heading': '练习提示与参考答案',
        'content': (
            '核心思路：遍历每个格子，遇到未访问的 \'1\'（陆地）就岛屿计数 +1，然后从该点开始 BFS/DFS 标记所有相连陆地。\n'
            'BFS 提示：用队列存储坐标元组，方向数组 directions = [(1,0),(-1,0),(0,1),(0,-1)]。'
            '在入队时就标记 visited[r][c]=true，不要等到出队再标记。\n'
            'DFS 提示：递归函数的参数为 (r, c)，基准情形为越界或 grid[r][c]==\'0\' 或 visited[r][c]。'
            '递归进入四个方向前先检查边界和 visited，避免重复递归。\n'
            '空间对比：BFS 队列在最坏情况下（全为陆地）大小 = O(min(n,m))，'
            'DFS 递归栈在最坏情况下（蛇形路径）深度 = O(n×m)。因此对于扁长网格，BFS 空间更优。'
        ),
    })

    card['sections'] = sections
    return card


# ── Topic: BFS和DFS / 分层练习 ──

def _enrich_bfs_dfs_practice(card, gen_context):
    """Generate BFS/DFS layered practice content."""
    display = gen_context.get('topic', 'BFS和DFS')
    lang = gen_context.get('normalized_language', 'C')

    sections = []

    sections.append({
        'kind': 'highlight', 'heading': display + ' — 练习整体说明',
        'content': (
            '本练习按三层递进设计——基础层验证你是否理解 BFS/DFS 的基本执行过程；'
            '进阶层测试你能否正确实现两种搜索并处理 visited 标记时机等关键细节；'
            '提高层挑战你用 BFS/DFS 解决综合问题（最短步数、连通分量、拓扑排序）。'
            '三层练习覆盖了从"能看懂"到"能写出"再到"能灵活运用"的完整学习路径。'
            '建议学习顺序：先完整做完基础层确认理解无误，再逐层挑战。'
        ),
    })

    # 基础层
    sections.append({
        'kind': 'practice', 'heading': '基础层：图遍历概念理解',
        'content': (
            '基础题 1：给定以下有向图（邻接表），从节点 A 出发，分别写出 BFS 和 DFS 的节点访问序列：\n'
            '  A → [B, C]\n  B → [D, E]\n  C → [F]\n  D → []\n  E → [F]\n  F → []\n'
            '（注意：邻接表中邻居按字母序排列，BFS 入队和 DFS 递归都按此顺序处理邻居）\n\n'
            '基础题 2：判断正误并给出理由——'
            '"BFS 使用队列所以空间一定比 DFS 大"、"递归 DFS 和迭代 DFS 的访问顺序永远相同"。\n\n'
            '基础题 3：在 BFS 中，visited 标记应该在 (A) 入队时 (B) 出队时 (C) 都可以——'
            '选择正确答案并解释为什么另两个选项会导致什么问题。'
        ),
    })
    sections.append({
        'kind': 'answer_hint', 'heading': '基础层提示',
        'content': (
            '题 1 答案：BFS 序列 A,B,C,D,E,F（逐层）；DFS 序列 A,B,D,E,F,C（深度优先）。'
            '注意 DFS 走到 D（无邻居）时回溯到 B 继续 E→F→回溯到 A 继续 C，这就是"一条路走到底再回溯"。\n'
            '题 2 答案：两个都是错的。BFS 空间 O(w) 在宽图时大但在深图时远小于 DFS 的 O(h)；'
            '递归 DFS 和迭代 DFS 如果入栈顺序一致（如都按邻居列表正序入栈），访问序列可以相同。\n'
            '题 3 答案(A)：入队时标记。如果出队时标记，同一层多个节点入队同一邻居会导致重复。'
        ),
    })

    # 进阶层
    sections.append({
        'kind': 'practice', 'heading': '进阶层：实现与关键细节',
        'content': (
            '进阶题 1：用 ' + lang + ' 实现 BFS 和 DFS（递归版），输入为邻接表和一个起始节点，'
            '输出为遍历顺序数组。要求包含 visited 标记且标记时机正确。\n\n'
            '进阶题 2：修改你的 BFS 实现，使其能同时输出"每个节点到起点的最短距离"。'
            '用 dist 数组替换单纯的 visited 数组，dist 初始化为 -1 表示未访问，'
            '起点的 dist=0，每次访问邻居时 dist[neighbor]=dist[current]+1。\n\n'
            '进阶题 3：何时选择 BFS 而非 DFS？给定以下三个场景，分别选择算法并说明理由：'
            '(a) 判断图中是否存在环路；(b) 求起点到终点的最少步数；(c) 生成迷宫的所有走法。'
        ),
    })
    sections.append({
        'kind': 'answer_hint', 'heading': '进阶层提示',
        'content': (
            '题 1 提示：BFS 用队列（FIFO），DFS 用递归（系统栈）。BFS 在入队前检查 visited，'
            'DFS 在递归调用前检查 visited。确保在主函数中也标记起点 visited。\n'
            '题 2 提示：dist[*]=-1 同时起到 visited 的作用（-1=未访问，>=0=已访问+最短距离）。'
            'BFS 的"逐层扩展"天然保证了首次访问时的距离就是最短距离，这是 BFS 的核心优势。\n'
            '题 3 答案：(a) DFS——回溯检测回边；(b) BFS——逐层扩展保证最短；(c) DFS——回溯穷举所有路径。'
        ),
    })

    # 提高层
    sections.append({
        'kind': 'practice', 'heading': '提高层：综合应用',
        'content': (
            '提高题 1（连通分量计数）：给定一个无向图，用 DFS 统计连通分量数量。'
            '思路：遍历所有节点，对每个未访问节点启动一次 DFS，DFS 过程中标记所有可达节点为一个连通分量。'
            'DFS 启动次数 = 连通分量数。要求 O(V+E) 时间。\n\n'
            '提高题 2（拓扑排序）：用 DFS 实现有向无环图（DAG）的拓扑排序。'
            '思路：在 DFS 退出节点时（后序位置）将节点加入结果栈，最后反转栈得到拓扑序。'
            '理解"为什么是后序位置加入"——因为要保证所有后继节点先于当前节点被处理。'
        ),
    })
    sections.append({
        'kind': 'answer_hint', 'heading': '提高层提示',
        'content': (
            '题 1 提示：外层循环 for each node: if !visited[node]: dfs(node); count++。'
            '每次 DFS 会标记完一整个连通分量的所有节点。注意此处的 visited 是全局的，不是每次 DFS 内部声明的。\n'
            '题 2 提示：拓扑排序基于"后序 DFS"——当 DFS 从一个节点退出时（即该节点的所有邻居都已处理完毕），'
            '将该节点入栈。DFS 全部完成后，栈顶到栈底就是拓扑序。'
            '可以验证：对于有向边 u→v，在 DFS 中 v 的后序早于 u 的后序，所以 v 在栈中更深，最终输出时 v 在 u 之前——正确。'
        ),
    })

    # 达标标准
    sections.append({
        'kind': 'check_criteria', 'heading': '每层达标标准',
        'content': (
            '基础层达标：能手动画出小图（5-8 个节点）的 BFS 队列变化和 DFS 递归调用栈变化，'
            '能准确写出两种遍历序列。未达标则重新阅读 BFS/DFS 图解讲解资源。\n'
            '进阶层达标：能独立写出 BFS（队列）和 DFS（递归）的完整代码，'
            'visited 标记时机正确，输出遍历序列无误。能解释 dist 数组如何同时替代 visited 和存储距离。'
            '未达标则用 3 个不同结构的图多练习几次。\n'
            '提高层达标：能独立实现连通分量计数和拓扑排序（DFS 后序版本），'
            '理解 BFS 最短路径和 DFS 回溯的本质差异，能在新问题前正确选择算法。'
        ),
    })

    sections.append({
        'kind': 'warnings', 'heading': '练习常见陷阱一：visited 全局 vs 局部',
        'content': (
            '初学者常见错误：在 DFS 函数内部声明 visited 数组，导致每次递归调用都重置 visited，'
            '所有节点都被重复访问，算法复杂度从 O(V+E) 退化为指数级。'
            '正确做法：visited 是全局（或外层作用域）的，一次 DFS 遍历中只初始化一次。'
        ),
    })
    sections.append({
        'kind': 'warnings', 'heading': '练习常见陷阱二：BFS/DFS 后的 visited 残留',
        'content': (
            '在统计连通分量时，一次 DFS/BFS 后 visited 数组应继续保持标记，'
            '下一次从下一个未访问节点重新启动搜索。如果错误地在每次搜索后清空 visited，'
            '则每个节点都被当作独立分量，结果错误。'
        ),
    })

    sections.append({
        'kind': 'next_action', 'heading': '完成后建议',
        'content': (
            '完成三层练习后，建议进入"图算法进阶"模块学习：Dijkstra 最短路径（BFS 的加权推广）、'
            '并查集（Union-Find，比 DFS 更高效的连通分量维护）、以及拓扑排序的 BFS 版本（Kahn 算法，基于入度表）。'
            '在此之前，确保你已在 LeetCode 上独立完成至少 5 道 BFS/DFS 标签的题目'
            '（推荐：200 岛屿数量、695 岛屿最大面积、994 腐烂的橘子、207 课程表、210 课程表 II），'
            '覆盖连通性、最短路径和拓扑排序三个维度。'
        ),
    })

    card['sections'] = sections
    return card


# ── Topic: 动态规划入门 / 项目案例 ──

def _enrich_dp_project(card, gen_context):
    """Generate DP project case content with Python code."""
    display = gen_context.get('topic', '动态规划入门')
    lang = gen_context.get('normalized_language', 'Python')

    sections = []

    sections.append({
        'kind': 'task', 'heading': display + ' — 项目任务描述',
        'content': (
            '项目名称：基于动态规划的 0/1 背包问题求解器。'
            '\n项目背景：0/1 背包问题是动态规划最经典的应用场景之一——'
            '给定 n 件物品，每件物品有重量 w[i] 和价值 v[i]，'
            '在背包总容量 W 的限制下选择物品（每件最多选一次），使总价值最大化。'
            '这是计算机科学中"有限资源下的最优决策"问题的原型，广泛应用于资源分配、投资决策等领域。'
            '\n核心目标：实现一个命令行程序，读取物品列表和背包容量，'
            '输出最大总价值和所选物品列表。要求同时支持自顶向下（记忆化搜索）和自底向上（DP 表格）两种实现，'
            '并能对比两种方法的运行时间和空间占用。'
            '\n输入格式：JSON 文件，字段包括 "capacity"（背包容量，整数）、'
            '"items"（物品列表，每项含 "name"、"weight"、"value"）。'
            '\n输出格式：JSON 文件，字段包括 "max_value"（最大价值）、'
            '"selected_items"（选中的物品名称列表）、"method"（使用的算法）、"elapsed_ms"（运行时间）。'
            '\n约束条件：物品数量 n ∈ [1, 100]，容量 W ∈ [1, 10^4]，重量和价值均为正整数。'
        ),
    })

    sections.append({
        'kind': 'steps', 'heading': '分阶段实现步骤',
        'steps': [
            '第1步：需求分析与 DP 状态定义——明确 0/1 背包的 DP 状态：dp[i][w] 表示"前 i 件物品，容量为 w 时的最大价值"。写出状态转移方程：dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt[i]] + val[i]) if w >= wt[i]，否则 dp[i][w] = dp[i-1][w]。在纸上手算 n=3, wt=[2,1,3], val=[4,2,3], W=4 的完整 dp 表格以验证方程正确性。',
            '第2步：设计项目模块结构——(a) parser.py：读取 JSON 输入，校验字段合法性；(b) solver.py：核心算法模块，包含 Solver 抽象基类和两个具体实现（MemoSolver 记忆化搜索、DPSolver 自底向上）；(c) tracer.py：回溯 dp 表格输出选中的物品列表；(d) runner.py：命令行入口，协调各模块并计时。每个模块独立可测试。',
            '第3步：实现自底向上 DP 版本（DPSolver）——用二维列表 dp[n+1][W+1] 初始化为 0，双层循环 for i in range(1,n+1): for w in range(W+1): 按转移方程填充。外层循环遍历物品（行），内层遍历容量（列）。此版本是后续优化的基准，确保 n=10, W=100 能在 1ms 内完成。',
            '第4步：实现记忆化搜索版本（MemoSolver）——用递归 + 字典 memo 保存已计算状态，key 为 (i, w) 元组。递归出口：i==0 或 w==0 时返回 0。对比两种版本的代码风格差异：DP 是"从最小子问题递推到原问题"，记忆化是"从原问题递归到最小子问题然后回溯"。两种方法结果相同但思考方向相反。',
            '第5步：实现回溯模块（tracer.py）——从 dp[n][W] 出发，逆向追踪：如果 dp[i][w] != dp[i-1][w]（说明选择了第 i 件物品），则将物品 i 加入结果，w -= wt[i-1]，i -= 1；否则 i -= 1。直到 i==0 或 w==0。这是 DP 的经典技巧——在求最优值的同时重建最优方案。',
            '第6步：编写测试与性能对比——设计 5 组测试用例（n=5,10,20,50,100），运行两种实现，记录运行时间和内存峰值。分析自底向上 DP 的空间优化：注意到 dp[i] 只依赖 dp[i-1]，可将二维 dp 压缩为一维 dp[W+1]，空间从 O(nW) 降到 O(W)。内层循环从 W 向 0 反向遍历以保证使用的是上一轮的值。',
            '第7步：文档与输出——编写 README 说明项目原理和用法，在报告中附上两种方法的性能对比表和 dp 表格的一个完整示例（n=3 的小规模，便于读者手算验证）。输出中包含"为什么一维优化要反向遍历"的详细解释（正向遍历会变成完全背包，允许同一物品被重复选取）。',
        ],
    })

    sections.append({
        'kind': 'text', 'heading': '架构与数据结构设计',
        'content': (
            '核心数据结构——二维 dp 表：dp[i][w] 是一个 (n+1)×(W+1) 的二维整数数组，'
            '第 0 行和第 0 列初始化为 0（表示 0 件物品或容量为 0 时价值为 0）。'
            'dp[i][w] 存储了前 i 件物品在容量 w 下的最优解，每个格子只依赖上一行和左边的格子，'
            '这揭示了 DP 的两个核心性质：最优子结构（每个格子由已求解的格子决定）和重叠子问题（同一状态被多次查询）。'
            '\n模块接口设计：(1) Solver.solve(items, capacity) → (max_value, dp_table) —— 返回最优值和 DP 表格；'
            '(2) Tracer.trace(dp_table, items, capacity) → selected_items —— 回溯选项；'
            '(3) 所有模块通过值传递交互（不共享可变状态），确保并发安全和可测试性。'
            '\n空间优化策略：一维 dp 数组替代二维——dp[w] = max(dp[w], dp[w-wt[i]] + val[i])，'
            'w 从 W 向 0 递减遍历。这个方向选择是"正确性 vs 性能"的经典案例——'
            '正向遍历等价于完全背包（每件物品多次选取），反向遍历才是 0/1 背包（每件物品一次）。'
        ),
    })

    # Python code skeleton
    code_text = (
        '"""0/1 Knapsack — DP + Memoization + Traceback"""\n'
        'from typing import List, Tuple\n'
        'import json\n'
        'import time\n'
        '\n'
        'class Item:\n'
        '    def __init__(self, name: str, weight: int, value: int):\n'
        '        self.name = name\n'
        '        self.weight = weight\n'
        '        self.value = value\n'
        '\n'
        '# ── 自底向上 DP ──\n'
        'def knapsack_dp(items: List[Item], W: int) -> Tuple[int, List[str]]:\n'
        '    n = len(items)\n'
        '    dp = [[0] * (W + 1) for _ in range(n + 1)]\n'
        '    \n'
        '    for i in range(1, n + 1):\n'
        '        wt_i = items[i - 1].weight\n'
        '        val_i = items[i - 1].value\n'
        '        for w in range(W + 1):\n'
        '            if wt_i <= w:\n'
        '                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - wt_i] + val_i)\n'
        '            else:\n'
        '                dp[i][w] = dp[i - 1][w]\n'
        '    \n'
        '    # 回溯选中的物品\n'
        '    selected = []\n'
        '    w = W\n'
        '    for i in range(n, 0, -1):\n'
        '        if dp[i][w] != dp[i - 1][w]:\n'
        '            selected.append(items[i - 1].name)\n'
        '            w -= items[i - 1].weight\n'
        '    selected.reverse()\n'
        '    return dp[n][W], selected\n'
        '\n'
        '# ── 记忆化搜索 ──\n'
        'def knapsack_memo(items: List[Item], W: int) -> int:\n'
        '    memo = {}\n'
        '    def dfs(i: int, w: int) -> int:\n'
        '        if i == 0 or w == 0:\n'
        '            return 0\n'
        '        if (i, w) in memo:\n'
        '            return memo[(i, w)]\n'
        '        if items[i - 1].weight > w:\n'
        '            memo[(i, w)] = dfs(i - 1, w)\n'
        '        else:\n'
        '            memo[(i, w)] = max(\n'
        '                dfs(i - 1, w),\n'
        '                dfs(i - 1, w - items[i - 1].weight) + items[i - 1].value\n'
        '            )\n'
        '        return memo[(i, w)]\n'
        '    return dfs(n, W)\n'
        '\n'
        '# ── 空间优化版（一维 dp）──\n'
        'def knapsack_1d(items: List[Item], W: int) -> int:\n'
        '    dp = [0] * (W + 1)\n'
        '    for item in items:\n'
        '        for w in range(W, item.weight - 1, -1):  # 反向遍历！\n'
        '            dp[w] = max(dp[w], dp[w - item.weight] + item.value)\n'
        '    return dp[W]\n'
        '\n'
        '# ── 主程序 ──\n'
        'if __name__ == "__main__":\n'
        '    items = [Item("A", 2, 4), Item("B", 1, 2), Item("C", 3, 3)]\n'
        '    W = 4\n'
        '    t0 = time.perf_counter()\n'
        '    max_val, sel = knapsack_dp(items, W)\n'
        '    elapsed = (time.perf_counter() - t0) * 1000\n'
        '    result = {"max_value": max_val, "selected_items": sel, "method": "dp", "elapsed_ms": round(elapsed, 3)}\n'
        '    print(json.dumps(result, ensure_ascii=False, indent=2))\n'
    )
    sections.append({
        'kind': 'code', 'heading': '核心代码框架（' + lang + '）',
        'language': lang, 'content': code_text,
    })

    sections.append({
        'kind': 'warnings', 'heading': '常见实现风险一：一维 dp 循环方向写反',
        'content': (
            '最常见的错误：在空间优化版中把内层循环 for w in range(W, ...) 写成正向 range(0, W+1)。'
            '正向遍历时 dp[w-wt[i]] 已经是本轮更新过的值（可能已经包含了当前物品），'
            '导致一件物品被重复选取——变成了完全背包而非 0/1 背包。'
            '验证方法：用 n=1, wt=[2], val=[10], W=4 测试——正向遍历会输出 20（选了两次），'
            '反向遍历正确输出 10（只能选一次）。'
        ),
    })
    sections.append({
        'kind': 'warnings', 'heading': '常见实现风险二：dp 表格下标偏移混淆',
        'content': (
            'dp[i][w] 中的 i 表示"前 i 件"而非"第 i 件"——items[0] 对应 dp[1][*]，'
            '所以代码中访问 items[i-1].weight 而不是 items[i].weight。'
            '如果弄错偏移量，整个 dp 表格都会错位。建议在代码中注释清楚"dp[i] 对应 items[0..i-1]"。'
        ),
    })

    sections.append({
        'kind': 'next_action', 'heading': '项目拓展方向',
        'content': (
            '拓展方向一（完全背包）：修改约束条件，允许每件物品选取无限次。'
            '只需将一维 dp 的内层循环改为正向遍历——这正是"正向=完全背包，反向=0/1 背包"这一规律的直接验证。'
            '跑同一组输入对比输出差异。'
            '\n拓展方向二（多维背包）：增加一个约束维度（如体积限制），将 dp 扩展为三维 dp[i][w][v]。'
            '思考：三维 dp 的空间优化（压缩为二维）是否还与一维优化遵循相同的方向法则？'
            '\n拓展方向三（性能基准测试）：用 n=100, W=10000 测试三种实现（DP 二维、DP 一维、记忆化搜索）'
            '的运行时间和内存占用，绘制 n-W-时间 三维图表，分析在何种参数范围内哪种实现更优。'
            '这是面试中展示"工程化思维"的高价值素材。'
        ),
    })

    card['sections'] = sections
    return card


# ── Topic enrichment dispatch table ──

_TOPIC_ENRICHERS = {
    ('binary_tree_traversal', '代码示例'): _enrich_preorder_code,
    ('quicksort_stability', '易错点'): _enrich_quicksort_pitfalls,
    ('bfs_dfs', '图解讲解'): _enrich_bfs_dfs_visual,
    ('bfs_dfs', '分层练习'): _enrich_bfs_dfs_practice,
    ('dynamic_programming', '项目案例'): _enrich_dp_project,
}


def enrich_resource_card(card, gen_context, thin_kinds=None):
    """
    Phase 3C-3: Topic-aware enrichment.
    Routes to topic-specific templates first (semantically-correct content),
    falls back to generic enrichment for non-specialized topics.
    """
    topic = gen_context.get('topic', '')
    rtype = card.get('type', '')

    # 1. Try topic-specific enrichment
    topic_key = _match_topic_key(topic)
    if topic_key:
        enricher = _TOPIC_ENRICHERS.get((topic_key, rtype))
        if enricher:
            logger.info(
                "Enriching via topic-specific template: key=%s type=%s topic=%s",
                topic_key, rtype, topic
            )
            return enricher(card, gen_context)

    # 2. Fall back to generic enrichment
    _enrich_generic(card, gen_context, thin_kinds)
    return card


def _enrich_generic(card, gen_context, thin_kinds=None):
    """Module-aware enrichment for topics without specific templates.

    Uses _MODULE_CONTENT[module] to produce topic-relevant content. Falls back
    to minimal template content only when the module has no knowledge entry.
    """
    rtype = card.get('type', '')
    topic = gen_context.get('topic', '')
    lang = gen_context.get('normalized_language', 'Python')
    module = gen_context.get('module', '')
    mc = _MODULE_CONTENT.get(module, {})
    display = topic.strip()

    # ── Build replacement card with module-aware content ──
    new_sections = _build_type_sections(rtype, module, topic, lang)

    # Merge: keep any existing sections whose kind is NOT in new_sections
    existing_sections = card.get('sections', []) or []
    new_kinds = {s.get('kind') for s in new_sections}
    kept_from_existing = [s for s in existing_sections if s.get('kind') not in new_kinds]

    card['sections'] = kept_from_existing + new_sections

    # Update summary if empty
    if not card.get('summary') or card.get('summary', '').startswith('关于'):
        card['summary'] = mc.get('overview', card.get('summary', ''))[:200] if mc.get('overview') else f'关于"{display}"的{rtype}学习资源，适配{module}模块。'

    return card


# ═══════════════════════════════════════════════════════════════════
# Phase 3C-3 hard override: 二叉树前序遍历 C++ 代码示例
# ═══════════════════════════════════════════════════════════════════

_BAD_WORDS = [
    '???????', 'O(?)', 'factorial', 'fib_memo', 'fibMemo',
    '相关概念A', '相关概念B', '策略模式', '负数处理', 'TODO', '示例待补充',
    'factorial(', 'fibonacci', 'fibonacci_memo',
]


def _should_override_preorder_cpp(gen_context: dict) -> bool:
    """Check if we must force the binary tree preorder C++ code card.

    STRICT scope — requires ALL of:
    - topic contains 二叉树 (or binary_tree)
    - topic contains 前序 (or preorder)
    - topic contains 遍历
    - resource_types includes 代码示例
    - language is C++
    """
    topic = (gen_context.get('topic', '') or '').strip()
    lang = gen_context.get('normalized_language', '') or ''
    types = gen_context.get('resource_types', []) or []

    has_bintree = '二叉树' in topic or 'binary_tree' in topic.lower()
    has_preorder = '前序' in topic or 'preorder' in topic.lower()
    has_traversal = '遍历' in topic
    is_code = '代码示例' in types
    is_cpp = lang == 'C++'

    return bool(has_bintree and has_preorder and has_traversal and is_code and is_cpp)


def _card_has_bad_words(card: dict) -> list[str]:
    """Scan card JSON for bad words. Returns list of found patterns."""
    text = json.dumps(card, ensure_ascii=False)
    return [w for w in _BAD_WORDS if w in text]


def build_preorder_cpp_code_card(gen_context: dict) -> dict:
    """
    Hard override: generates a complete binary tree preorder C++ code example card.
    All sections are semantically correct for this specific topic+type+language combo.
    """
    topic = gen_context.get('topic', '二叉树前序遍历')
    module = gen_context.get('module', '树与二叉树')
    lang = gen_context.get('normalized_language', 'C++')
    difficulty = gen_context.get('difficulty', '入门')

    return {
        'id': 'res-preorder-cpp-001',
        'title': '二叉树前序遍历 C++ 代码示例',
        'type': '代码示例',
        'course': '数据结构与算法',
        'knowledge_point': '二叉树前序遍历',
        'difficulty': difficulty,
        'language': lang,
        'summary': (
            '二叉树前序遍历的完整 C++ 实现，包含递归版和非递归栈版两种写法。'
            '代码定义 TreeNode 结构体和 preorder(TreeNode* root) 函数，'
            '涵盖递归调用栈的压栈/弹栈过程详解，附带复杂度分析和常见误区。'
            '适合刷题训练，直接对应 LeetCode 144 号题目。'
        ),
        'sections': [
            {
                'kind': 'highlight',
                'heading': '二叉树前序遍历 C++ 代码整体说明',
                'content': (
                    '以下代码展示了二叉树前序遍历的完整 C++ 实现。'
                    '前序遍历的访问顺序是"根节点 → 左子树 → 右子树"，'
                    '这是三种深度优先遍历中最基础的一种。'
                    '代码定义了 TreeNode 节点结构体和递归遍历函数 preorder(TreeNode* root)，'
                    '并提供了可直接编译运行的 main 函数来构建测试树并输出结果。'
                    '重点理解三个核心点：(1) 递归函数的入口 preorder(root) 和出口 nullptr 判断；'
                    '(2) 根/左/右的访问顺序（cout 在两个递归调用之前即为前序）；'
                    '(3) 递归调用栈的后进先出特性决定了深度优先的遍历路径。'
                ),
            },
            {
                'kind': 'code',
                'heading': '二叉树前序遍历完整实现（C++）',
                'language': 'C++',
                'content': (
                    '#include <iostream>\n'
                    'using namespace std;\n'
                    '\n'
                    '// 二叉树节点定义\n'
                    'struct TreeNode {\n'
                    '    int val;\n'
                    '    TreeNode *left, *right;\n'
                    '    TreeNode(int v = 0, TreeNode* l = nullptr, TreeNode* r = nullptr)\n'
                    '        : val(v), left(l), right(r) {}\n'
                    '};\n'
                    '\n'
                    '// 前序遍历：根 → 左 → 右\n'
                    'void preorder(TreeNode* root) {\n'
                    '    if (root == nullptr) return;  // 递归边界：空节点直接返回\n'
                    '    cout << root->val << " ";     // 第一步：访问根节点\n'
                    '    preorder(root->left);         // 第二步：递归遍历左子树\n'
                    '    preorder(root->right);        // 第三步：递归遍历右子树\n'
                    '}\n'
                    '\n'
                    'int main() {\n'
                    '    // 构建测试树:\n'
                    '    //        1\n'
                    '    //       / \\\n'
                    '    //      2   3\n'
                    '    //     / \\\n'
                    '    //    4   5\n'
                    '    TreeNode* root = new TreeNode(1,\n'
                    '        new TreeNode(2, new TreeNode(4), new TreeNode(5)),\n'
                    '        new TreeNode(3));\n'
                    '    \n'
                    '    cout << "前序遍历结果: ";\n'
                    '    preorder(root);  // 期望输出: 1 2 4 5 3\n'
                    '    cout << endl;\n'
                    '    return 0;\n'
                    '}'
                ),
            },
            {
                'kind': 'steps',
                'heading': '代码逐段详解',
                'steps': [
                    '第1段：TreeNode 节点结构体——定义了二叉树的节点类型，包含 val（节点值）、left（左子节点指针）、right（右子节点指针）。构造函数支持创建节点时直接指定值和子树，nullptr 表示空子树。理解这个结构体是理解整个遍历代码的前提——二叉树的每个节点都是 TreeNode 类型的对象，左右子节点通过指针连接。',
                    '第2段：preorder 函数签名——void preorder(TreeNode* root) 表示该函数接收一个指向 TreeNode 的指针 root，无返回值（遍历结果直接输出到屏幕）。root 参数代表当前子树的根节点——注意它可以是 nullptr 表示空树，这为递归终止提供了统一的判断条件。',
                    '第3段：为什么前序遍历先访问根节点——前序遍历的定义是"根→左→右"，因此在进入左右子树之前必须先处理当前根节点：cout << root->val。这是三种深度优先遍历中前序独有的特征——中序遍历将根节点放在左右之间、后序遍历将根节点放在最后。三种遍历的核心区别就是这一行代码的位置。',
                    '第4段：为什么递归访问左子树——preorder(root->left) 对左子树执行完全相同的前序遍历逻辑。递归的关键在于：每次调用 preorder(root->left) 时，系统会在调用栈上压入一个新的栈帧，这个栈帧保存了当前函数的局部状态（包括 root 指针和返回地址），然后从 root->left 开始重新从头执行 preorder 的全部逻辑。',
                    '第5段：为什么递归访问右子树——preorder(root->right) 在左子树全部处理完毕后执行。注意递归调用栈的后进先出特性：最先进入的根节点调用最后才返回，而最深的叶子节点调用最先返回。这保证了整棵树按照"先深入左侧、再回退到右侧"的顺序被遍历，这正是深度优先搜索在二叉树上的体现。',
                    '第6段：nullptr 为什么是递归终止条件——当遍历到叶子节点的下一层时（例如访问节点 4 的 left，它为空），传入的 root 为 nullptr。此时 if (root == nullptr) return; 这一行直接返回，避免在空指针上调用 root->val 导致段错误。这是所有递归树遍历函数最关键的一行防御代码——如果忘记这行，程序在访问任何叶子节点时都会崩溃。',
                    '第7段：调用栈如何在叶子节点返回后回退——以测试树为例，当 preorder(4) 输出 4 后调用 preorder(4->left) 即 preorder(nullptr)，nullptr 触发 return 回到 preorder(4)；接着 preorder(4->right) 也是 nullptr 返回；preorder(4) 的这两行都执行完毕后函数返回，调用栈回退到 preorder(2)。此时 preorder(2) 已经完成了根(2)和左子树(4)的处理，继续执行 preorder(2->right) 即 preorder(5)。这个过程就是递归调用栈"先进后出"的具体体现——根节点 preorder(1) 最先被调用但最后才返回。',
                ],
            },
            {
                'kind': 'complexity',
                'heading': '时间复杂度与空间复杂度分析',
                'content': (
                    '时间复杂度：O(n)，其中 n 为二叉树的节点总数。'
                    '每个节点恰好被访问一次——preorder 函数对每个节点执行一次 cout 操作，'
                    '没有重复访问也没有遗漏。即使二叉树退化为链表（每个节点只有左子节点或只有右子节点），'
                    '时间复杂度仍然是 O(n)，因为每个节点依然只被访问一次。'
                    '\n空间复杂度：O(h)，其中 h 为二叉树的高度。'
                    '空间开销来自递归调用栈——递归的最大深度等于树的高度 h。'
                    '在平衡二叉树中，h = log₂(n+1) ≈ O(log n)，空间开销很小。'
                    '在最坏情况下（树退化为链表，每个节点只有左子），h = n，空间复杂度退化为 O(n)。'
                    '这也是递归实现的潜在风险：当 n 很大且树不平衡时，可能导致调用栈溢出。'
                    '\n迭代实现的对比：如果用显式栈 std::stack<TreeNode*> 模拟递归实现前序遍历，'
                    '空间复杂度同样为 O(h)，但显式栈分配在堆内存中，避免了系统调用栈溢出的风险。'
                ),
            },
            {
                'kind': 'warnings',
                'heading': '注意事项一：忘记 nullptr 判断会导致空指针访问',
                'content': (
                    '最常见的严重错误是忘记在 preorder 函数开头检查 root == nullptr。'
                    '如果省略这个检查，当遍历到叶子节点时，root 为 nullptr，'
                    '执行 root->val 会触发空指针解引用（Segmentation Fault），程序直接崩溃。'
                    '正确做法：递归函数的第一行永远是边界条件判断——'
                    '这是递归树遍历与迭代循环在防御性编程上的最大区别。'
                    '测试方法：传入一个空树 preorder(nullptr)，验证程序不会崩溃。'
                ),
            },
            {
                'kind': 'warnings',
                'heading': '注意事项二：cout 的位置写错会把前序写成中序或后序',
                'content': (
                    '三种遍历的三个函数体结构完全相同，唯一区别是 cout << root->val 的位置：'
                    '前序（根→左→右）——cout 在最前面；'
                    '中序（左→根→右）——cout 在两个递归调用之间；'
                    '后序（左→右→根）——cout 在最后面。'
                    '记忆口诀：前/中/后指的是根节点在第几个被访问。'
                    '以同一棵树 [1,2,3,4,5] 验证：前序输出以 1 开头，中序输出以 4 开头，后序输出以 1 结尾。'
                    '如果前序输出以左子树值开头，说明你错把中序当前序了。'
                ),
            },
            {
                'kind': 'warnings',
                'heading': '注意事项三：递归深度过大可能导致调用栈溢出',
                'content': (
                    '在 C++ 中，系统调用栈默认大小通常为 1-8 MB。'
                    '当二叉树退化为深度 10^5 的链表时，递归深度 = 10^5，'
                    '每个栈帧约占用几十到上百字节，总空间可能超过调用栈上限触发栈溢出。'
                    '解决方案：(1) 改用显式栈的迭代实现；(2) 平衡树递归是安全的；'
                    '(3) 在竞赛或面试场景中，n ≤ 10^4 时递归通常安全，n ≥ 10^5 时建议用迭代。'
                ),
            },
            {
                'kind': 'warnings',
                'heading': '注意事项四：示例中 new 的节点未释放，工程中应注意内存管理',
                'content': (
                    '本示例代码出于简洁目的没有释放用 new 创建的 TreeNode 节点。'
                    '在实际工程代码中，应当在程序结束前遍历树并 delete 所有节点，'
                    '或使用 std::unique_ptr<TreeNode> 等智能指针来自动管理内存。'
                    '如果是在 LeetCode 等在线评测平台提交，平台会负责内存回收，'
                    '但在本地运行的完整程序中，忽视 delete 会导致内存泄漏。'
                ),
            },
            {
                'kind': 'practice',
                'heading': '变式练习',
                'content': (
                    '练习一（非递归栈实现）：将上述递归前序遍历改写为使用显式栈的迭代版本。'
                    '要求：(1) 使用 std::stack<TreeNode*> 模拟递归调用栈；'
                    '(2) 入栈顺序必须是"先右后左"——因为栈是 LIFO（后进先出），'
                    '后入栈的左子节点会先出栈被访问，这就保证了左子树先于右子树被访问，满足前序的"根→左→右"顺序；'
                    '(3) 用同一棵测试树验证递归版和非递归版的输出是否一致，期望均是 "1 2 4 5 3"。'
                    '提示：初始化栈为 {root}，while 栈非空时弹出栈顶节点并输出其值，然后按先右后左的顺序将非空子节点入栈。'
                    '\n练习二（中序后序对比）：将上述代码分别改为中序遍历和后序遍历——只修改递归调用和 cout 的相对顺序。'
                    '用同一棵测试树验证三种遍历输出的差异，并用纸笔在树结构图上标注每种遍历的访问序号（1,2,3,4,5），'
                    '直观感受三种遍历路径的不同。'
                ),
            },
            {
                'kind': 'next_action',
                'heading': '学完前序遍历后的延伸学习路径',
                'content': (
                    '建议按以下顺序继续学习：(1) 将前序递归改为非递归栈实现——'
                    '这是验证你是否真正理解前序遍历与栈关系的标准方法。'
                    '如果你能独立写出迭代版本并通过测试，说明你对"根→左→右"和"栈后进先出"的关系已建立清晰直觉；'
                    '(2) 对比前序、中序、后序三种遍历——用同一棵树画出每种遍历的访问路径和调用栈图。'
                    '只有理解了三种遍历的代码差异仅在于一行代码的位置，才算真正掌握二叉树遍历；'
                    '(3) 学习层序遍历（BFS）——理解"深度优先 vs 广度优先"在二叉树上的体现。'
                    '前序是 DFS 的一种（使用栈），层序是 BFS（使用队列），两者在数据结构和访问顺序上有本质区别；'
                    '(4) 挑战 LeetCode 144（二叉树前序遍历）、94（中序）、145（后序），'
                    '用递归和迭代两种方法各提交一次，对比运行时间和内存消耗的实际差异。'
                ),
            },
        ],
        'key_concepts': ['二叉树前序遍历', '深度优先遍历', '递归调用栈', 'TreeNode', 'nullptr'],
        'learning_tips': [
            '建议先在纸上画出测试树的结构，手动跟踪 preorder(root) 的每一次调用',
            '用调试器单步执行观察 root 指针的值如何变化以及调用栈的压栈/弹栈过程',
            '对比递归版和迭代版的代码，理解栈在两者中的不同角色',
        ],
        'recommended_usage': (
            '先通读代码获取整体结构，再对照步骤详解逐段理解。'
            '然后手动在纸上模拟一遍调用栈的压栈/弹栈过程。'
            '最后完成变式练习中的非递归栈实现来验证理解。'
        ),
        'estimated_time': '30-40 分钟',
        'match_reason': '基于刷题训练目标和 C++ 语言偏好，生成了二叉树前序遍历完整代码示例，涵盖递归实现、调用栈详解、非递归改写练习，直接对应 LeetCode 144。',
        'personalized_reason': '基于刷题训练目标和 C++ 语言偏好，生成了二叉树前序遍历完整代码示例，涵盖递归实现、调用栈详解、非递归改写练习，直接对应 LeetCode 144。',
        'programming_language_used': 'C++',
    }


def _check_cross_topic_contamination(cards: list[dict], gen_context: dict) -> None:
    """Scan cards for content that belongs to a DIFFERENT topic (Phase 14B-3 cross-topic check)."""
    topic = gen_context.get('topic', '') or ''
    topic_low = topic.lower()
    is_binary_tree = '二叉树' in topic or 'binary_tree' in topic_low or '树' in topic
    is_quicksort = '快速排序' in topic or 'quicksort' in topic_low
    is_bfs_dfs = ('BFS' in topic or '广度优先' in topic or 'DFS' in topic or '深度优先' in topic
                  or '图' in topic)
    is_dp = '动态规划' in topic or 'DP' in topic or 'dp' in topic_low.split()

    for card in cards:
        rtype = card.get('type', '')
        sections_text = json.dumps(card.get('sections', []), ensure_ascii=False)

        # Check 1: Non-binary-tree topics must NOT contain TreeNode/preorder
        if not is_binary_tree:
            if 'TreeNode' in sections_text or 'preorder' in sections_text.lower():
                logger.warning(
                    "CROSS-TOPIC CONTAMINATION: '%s' (%s) contains TreeNode/preorder "
                    "but topic=%r is not binary-tree related",
                    card.get('title', ''), rtype, topic
                )

        # Check 2: Quicksort cards must contain [3a,2,3b,1] stability counterexample
        if is_quicksort and rtype == '易错点':
            if '3a' not in sections_text or '3b' not in sections_text:
                logger.warning(
                    "MISSING CONTENT: '%s' (%s) is quicksort+易错点 but lacks [3a,2,3b,1] "
                    "stability counterexample",
                    card.get('title', ''), rtype
                )

        # Check 3: BFS/DFS cards should contain visited/队列 references
        if is_bfs_dfs:
            if 'visited' not in sections_text and '队列' not in sections_text:
                logger.warning(
                    "MISSING CONTENT: '%s' (%s) is BFS/DFS but lacks visited/队列 references",
                    card.get('title', ''), rtype
                )

        # Check 4: DP cards should contain 状态定义/状态转移 references
        if is_dp:
            if '状态定义' not in sections_text and '状态转移' not in sections_text:
                logger.warning(
                    "MISSING CONTENT: '%s' (%s) is DP but lacks 状态定义/状态转移 references",
                    card.get('title', ''), rtype
                )


# ═══════════════════════════════════════════════════════════════════
# Phase 14B-3: Topic-specific hard override templates
# ═══════════════════════════════════════════════════════════════════

def build_quicksort_stability_mistake_card(gen_context: dict) -> dict:
    """Hard override: complete 易错点 card for quicksort stability."""
    topic = gen_context.get('topic', '快速排序为什么不稳定')
    lang = gen_context.get('normalized_language', 'Java')
    difficulty = gen_context.get('difficulty', '入门')

    return {
        'id': 'res-quicksort-pitfalls-001',
        'title': '快速排序为什么不稳定 — 易错点',
        'type': '易错点',
        'course': '数据结构与算法',
        'knowledge_point': '快速排序稳定性分析',
        'difficulty': difficulty,
        'language': lang,
        'summary': (
            '聚焦快速排序四大易错场景：基准选择导致的 O(n²) 退化、partition 双指针边界条件、'
            '递归出口遗漏、以及通过 [3a,2,3b,1] 反例完整演示稳定性被破坏的过程。'
            '每项包含错误现象、根因分析和正确做法，附带判断纠错自测题和详细答案。'
        ),
        'sections': [
            {
                'kind': 'highlight',
                'heading': '快速排序为什么不稳定 — 高频错误类别概述',
                'content': (
                    '"快速排序为什么不稳定"是数据结构面试中最高频的追问之一。'
                    '超过 70% 的候选人能写出快速排序代码，但只有不到 30% 能准确解释其不稳定性的根因。'
                    '本资源聚焦四个核心易错点：基准选择导致的退化、partition 边界条件误区、'
                    '递归出口遗漏、以及最关键的——通过 [3a,2,3b,1] 反例演示稳定性被破坏的完整过程。'
                ),
            },
            {
                'kind': 'warnings',
                'heading': '易错点一：固定选首/尾元素作基准 → O(n²) 退化',
                'content': (
                    '错误现象：固定选第一个或最后一个元素作 pivot，在已排序（或逆序）数组上每次 partition '
                    '只排除一个元素，递归深度 = n，总比较次数 ≈ n+(n-1)+...+1 = O(n²)，在 n=10⁵ 时远超时间限制。'
                    '\n根因分析：理想的 pivot 应使左右子数组尽量均分（各约 n/2），固定端点破坏了这一均衡性。'
                    '\n正确做法：采用随机 pivot（随机选一个元素与末尾交换）或三数取中法（median-of-three），将退化概率降至极低。'
                ),
            },
            {
                'kind': 'warnings',
                'heading': '易错点二：partition 双指针的移动条件写错',
                'content': (
                    '错误现象：while 循环中指针移动条件写成 arr[i] <= pivot（加了等号），导致全等数组 '
                    '[5,5,5,5] 上指针无法移动，陷入无限循环或越界。或者忘记 while i <= j 的最终退出条件。'
                    '\n根因分析：partition 核心不变量是"严格小于 pivot 的放左边，严格大于的放右边"，'
                    '等于 pivot 的元素可放在任意一侧。'
                    '\n正确做法：内层 while 使用严格 < 和 >（不含等号）；外层 while 条件是 i <= j（含等号），'
                    '保证指针交错后正确退出。'
                ),
            },
            {
                'kind': 'warnings',
                'heading': '易错点三：递归出口 if (low >= high) return; 遗漏',
                'content': (
                    '错误现象：忘记写递归出口就直接调用 quicksort(arr, low, j) 和 quicksort(arr, i, high)，'
                    '导致空子数组或单元素子数组继续无限递归，最终栈溢出。'
                    '\n根因分析：快速排序有两个递归调用，容易在专注 partition 逻辑时忘记出口。'
                    '\n正确做法：quicksort 函数的第一行必须是递归出口边界条件。'
                    '测试用例应包含长度为 0、1、2 的数组来验证出口逻辑。'
                ),
            },
            {
                'kind': 'warnings',
                'heading': '易错点四：不理解为什么快速排序不稳定（核心）',
                'content': (
                    '错误现象：能写出快速排序但说不清它为什么不稳定，面试时被追问就卡壳。'
                    '\n根因分析：稳定性要求"相等元素的相对顺序在排序前后不变"。快速排序的 partition '
                    '过程涉及跳跃式的远距离 swap，一个等于 pivot 的元素可能被换到很远的位置，'
                    '与前面相等元素的相对顺序因此被破坏。'
                    '\n正确理解：归并排序的 merge 在遇到相等元素时"优先取左半部分"，天然保持相对顺序，因此稳定。'
                    '快速排序的 partition 无法做类似的保证——详见下方的 [3a,2,3b,1] 反例演示。'
                ),
            },
            {
                'kind': 'compare',
                'heading': '稳定性反例演示 [3a, 2, 3b, 1] —— 快速排序如何破坏相对顺序',
                'content': (
                    '演示：快速排序为什么不稳定（Lomuto partition，以最后一个元素为基准）\n\n'
                    '初始数组（相等元素 3 用编号 a/b 区分先后位置）：\n'
                    '  索引: 0    1    2    3\n'
                    '  元素: 3a   2    3b   1\n\n'
                    '基准 pivot = arr[3] = 1（最后一个元素）\n\n'
                    'partition 过程（变量 i 记录"小于 pivot 的最后一个位置"）：\n'
                    '  i = -1（初始值）\n'
                    '  j = 0: arr[0]=3a > 1  → 不交换，i 仍为 -1\n'
                    '  j = 1: arr[1]=2  > 1  → 不交换，i 仍为 -1\n'
                    '  j = 2: arr[2]=3b > 1  → 不交换，i 仍为 -1\n'
                    '  j = 3: 循环结束，i+1=0，交换 arr[0] 和 arr[3]\n\n'
                    '交换后数组：\n'
                    '  索引: 0    1    2    3\n'
                    '  元素: 1    2    3b   3a\n\n'
                    '关键观察：\n'
                    '- 排序前：3a（索引 0）在 3b（索引 2）的前面\n'
                    '- 排序后：3b（索引 2）跑到了 3a（索引 3）的前面\n'
                    '- 3a 和 3b 的值相等（都是 3），相对先后顺序发生翻转 → 排序不稳定\n\n'
                    '为什么 3a 被换到 3b 后面？\n'
                    'partition 将 arr[0]（3a）与 arr[3]（1）直接交换，3a 从数组最前面跳到了最后面——'
                    '这个跳跃式 swap 跨越了 3b 所在的位置，无法保证 3a 和 3b 的相对顺序。'
                    '这是 partition 机制的本质特征，无法通过调整 pivot 选择来修复。\n\n'
                    '对比：归并排序的 merge 阶段在 arr1[i]==arr2[j] 时固定选 arr1[i]（左半部分），'
                    '两个相等元素中原本在左边的仍然在左边，稳定性得到保证。'
                ),
            },
            {
                'kind': 'example',
                'heading': '具体犯错场景：面试手写代码中的典型错误',
                'content': (
                    '场景一（面试手写代码）：面试官要求手写快速排序的 partition。候选人将 while 条件写成：\n'
                    '  while (arr[i] <= pivot) i++;  // 错误！加了等号\n'
                    '  while (arr[j] >= pivot) j--;  // 错误！加了等号\n'
                    '测试输入 [5, 5, 5, 5]（全等数组）：i 和 j 都无法移动，导致无限循环或越界崩溃。'
                    '修复：改为严格 < 和 >，让等于 pivot 的元素由后续的 i <= j 判断和 swap 处理。\n\n'
                    '场景二（稳定性误解）：学生写完快速排序后声称它是稳定的，理由是"我把相等的元素放一起了"。'
                    '用 [3a, 2, 3b, 1] 反例当场演示：输入包含两个相同的 3，输出中它们的相对顺序被翻转。'
                    '学生才意识到"放一起"不等于"保持相对顺序"——稳定性关心的是原顺序，不是值是否相邻。'
                ),
            },
            {
                'kind': 'text',
                'heading': '为什么会写错 / 错在哪里 / 如何避免',
                'content': (
                    '为什么会错：partition 算法是"代码量不多但逻辑密度极高"的典型——双指针相向移动，'
                    '每一行条件的微妙差异（< vs <=，i <= j vs i < j）都会导致完全不同的行为。'
                    '人脑在追踪两个指针的同时移动和交换时容易出错，尤其在面试或考试的时间压力下。'
                    '\n错在哪里：错误的本质是"分支条件的不完备"——没有覆盖所有可能的输入情况。'
                    '例如 while (arr[i] < pivot) 不能处理 arr[i] == pivot 的情况，可能导致死循环；'
                    'if (low >= high) return 缺少等号会漏掉长度为 1 的子数组。'
                    '\n如何避免：(1) 背诵标准模板——快速排序的 partition 代码模式高度固定，'
                    '直接背诵经过验证的标准实现是最可靠的应试策略；'
                    '(2) 理解不变量——partition 过程中维护"[low..i] 全部 < pivot，[j..high] 全部 > pivot"'
                    '这一核心不变量，每次修改代码前先在脑内用该不变量验证；'
                    '(3) 测试三件套——每次写出 partition 后立即用已排序数组 [1,2,3,4]、逆序数组 [4,3,2,1]、'
                    '全等数组 [5,5,5,5] 三个测试用例验证，这三者覆盖了绝大多数的边界条件错误。'
                ),
            },
            {
                'kind': 'practice',
                'heading': '判断纠错练习',
                'content': (
                    '练习一：以下快速排序代码有 bug，请找出并写出修复方法——\n'
                    'def broken_qs(arr):\n'
                    '    if len(arr) <= 1: return arr\n'
                    '    pivot = arr[0]  # 固定选第一个元素\n'
                    '    left = [x for x in arr[1:] if x < pivot]\n'
                    '    right = [x for x in arr[1:] if x > pivot]\n'
                    '    return broken_qs(left) + [pivot] + broken_qs(right)\n'
                    '（提示：等于 pivot 的元素去了哪里？这是稳定性问题还是正确性问题？）\n\n'
                    '练习二：用 Python 的 sort() 和自己实现的 quicksort 分别对以下列表按第一个元素排序，'
                    '观察两个版本中相等元素 (3,\'a\') 和 (3,\'c\') 的相对顺序变化：\n'
                    '  data = [(3,\'a\'), (2,\'b\'), (3,\'c\'), (1,\'d\')]\n'
                    '记录两种排序的输出结果，解释为什么 sort() 的输出中 (3,\'a\') 仍在 (3,\'c\') 前面，'
                    '而 quicksort 的输出中可能相反。'
                ),
            },
            {
                'kind': 'answer_hint',
                'heading': '纠错练习提示与参考答案',
                'content': (
                    '练习一答案：等于 pivot 的元素（x == pivot）既没进 left 也没进 right，被直接丢弃了——'
                    '排序后数组中所有等于原始 pivot 值（arr[0]）的元素只剩下 pivot 本身，其余全部丢失。'
                    '这是正确性 bug，比稳定性 bug 更严重。修复方式之一：right 的条件改为 x >= pivot，'
                    '或单独收集 equal = [x for x in arr if x == pivot] 然后在递归结果中拼接。'
                    '\n练习二答案：Python 内置的 sort() 使用 Timsort 算法，是稳定的——'
                    '(3,\'a\') 和 (3,\'c\') 的值（按第一个元素）相等，Timsort 保持输入中的先后顺序，'
                    '因此 (3,\'a\') 仍在前。手写 quicksort 不稳定——partition 的 swap 可能将 (3,\'a\') 换到 (3,\'c\') 后面。'
                    '这直接验证了快速排序的不稳定性。'
                ),
            },
        ],
        'key_concepts': ['快速排序', '稳定性', 'partition', 'Lomuto', '归并排序对比'],
        'learning_tips': [
            '先理解 [3a,2,3b,1] 反例的每一步交换，再推广到任意相等元素',
            '用 Python 或 Java 实际运行快速排序，在 swap 处打印数组状态，观察相等元素的移动',
            '对比归并排序的 merge 实现，理解"优先取左半部分"如何保证稳定性',
        ],
        'recommended_usage': (
            '先通读四个易错点了解常见陷阱，再逐行跟踪 [3a,2,3b,1] 反例的 partition 过程。'
            '最后完成纠错练习来自我验证是否真正理解了稳定性的含义。'
        ),
        'estimated_time': '25-35 分钟',
        'match_reason': '基于学习目标中的排序算法专项训练，生成了快速排序稳定性专题的易错点分析，包含 [3a,2,3b,1] 反例和判断纠错练习。',
        'personalized_reason': '基于学习目标中的排序算法专项训练，生成了快速排序稳定性专题的易错点分析，包含 [3a,2,3b,1] 反例和判断纠错练习。',
        'programming_language_used': lang,
    }


def build_bfs_dfs_visual_card(gen_context: dict) -> dict:
    """Hard override: complete 图解讲解 card for BFS and DFS comparison."""
    topic = gen_context.get('topic', 'BFS和DFS')
    lang = gen_context.get('normalized_language', 'C')
    difficulty = gen_context.get('difficulty', '入门')

    return {
        'id': 'res-bfs-dfs-visual-001',
        'title': 'BFS和DFS图遍历算法对比 — 图解讲解',
        'type': '图解讲解',
        'course': '数据结构与算法',
        'knowledge_point': 'BFS和DFS',
        'difficulty': difficulty,
        'language': lang,
        'summary': (
            '通过 6 节点邻接图示例，完整演示 BFS（队列）和 DFS（栈）的逐步执行过程。'
            '包含数据结构对比表（队列 vs 栈）、visited 标记时机分析、空间复杂度'
            '差异推导，以及一道配套练习题检验理解深度。'
        ),
        'sections': [
            {
                'kind': 'highlight',
                'heading': 'BFS 和 DFS 的核心要点',
                'content': (
                    'BFS（广度优先搜索）和 DFS（深度优先搜索）是图遍历的两大基本策略。'
                    'BFS 使用队列（FIFO）实现逐层扩展，天然适合求无权图的最短路径；'
                    'DFS 使用栈（LIFO）或递归实现一条路走到黑再回溯，适合连通性检测和拓扑排序。'
                    '二者的本质差异在于数据结构选择——队列 vs 栈——这直接决定了节点的访问顺序。'
                    '理解 visited 数组的作用和标记时机（入队/入栈时标记 vs 出队/出栈时标记）是避免重复访问的关键。'
                ),
            },
            {
                'kind': 'example',
                'heading': '以 6 节点无向图为例的完整演示',
                'content': (
                    '以下用一个包含 6 个节点（编号 0-5）的无向图对比 BFS 和 DFS 的完整执行过程：\n\n'
                    '图结构（邻接表表示）：\n'
                    '  0 → [1, 2]\n'
                    '  1 → [0, 3, 4]\n'
                    '  2 → [0, 5]\n'
                    '  3 → [1]\n'
                    '  4 → [1, 5]\n'
                    '  5 → [2, 4]\n\n'
                    '从节点 0 出发——\n'
                    'BFS 访问顺序（逐层）：0 → 1, 2 → 3, 4, 5\n'
                    '  队列模拟：[0] → pop0 push1,2 → [1,2] → pop1 push3,4 → [2,3,4]'
                    ' → pop2 push5 → [3,4,5] → pop3 → [4,5] → pop4 → [5] → pop5 → []\n'
                    'DFS 访问顺序（深入到底）：0 → 1 → 3 → 4 → 5 → 2\n'
                    '  栈模拟：[0] → pop0 push1,2 → [1,2] → pop1 push3,4 → [3,4,2]'
                    ' → pop3 → [4,2] → pop4 push5 → [5,2] → pop5 → [2] → pop2 → []'
                ),
            },
            {
                'kind': 'steps',
                'heading': 'BFS 执行步骤详解',
                'steps': [
                    '步骤1：初始化——创建 visited 数组（长度6，全部false）和队列q。将起点0入队，同时标记 visited[0]=true。visited 标记必须在入队时完成，不能延迟到出队时——否则同一层的邻居节点可能重复入队，导致结果中出现重复元素。',
                    '步骤2：处理节点0——出队0，访问（记录到结果序列）。遍历0的邻居[1,2]：1未访问，入队并标记visited[1]=true；2未访问，入队并标记visited[2]=true。此时队列=[1,2]，visited状态=[T,T,T,F,F,F]。',
                    '步骤3：处理节点1——出队1，访问。遍历1的邻居[0,3,4]：0已访问跳过；3未访问，入队并标记visited[3]=true；4未访问，入队并标记visited[4]=true。队列=[2,3,4]，visited=[T,T,T,T,T,F]。',
                    '步骤4：处理节点2——出队2，访问。遍历2的邻居[0,5]：0已访问跳过；5未访问，入队并标记visited[5]=true。队列=[3,4,5]。关键观察：此时所有节点都已标记visited，但队列仍非空——BFS继续处理剩余节点。',
                    '步骤5：依次出队3,4,5——它们的邻居都已访问，无新节点入队。队列逐次缩短直到为空，BFS结束。最终访问序列：[0,1,2,3,4,5]——这是从0出发按距离分层的结果：距离0的节点先访问，距离1的次之，距离2的最后。',
                    '步骤6：DFS对比——同样从0出发，用栈（或递归）实现。入栈顺序：0入栈→pop0→push1,2→pop1→push3,4→pop3→pop4→push5→pop5→pop2。访问序列：[0,1,3,4,5,2]——优先走完一条路径再回溯，体现了"深度优先"的特性。注意push顺序影响访问顺序：如果先push2再push1，DFS路径会变为0→2→5→4→1→3。',
                ],
            },
            {
                'kind': 'table',
                'heading': 'BFS vs DFS 三维度对比表',
                'content': (
                    '对比维度 | BFS（广度优先搜索） | DFS（深度优先搜索）\n'
                    '核心数据结构 | 队列（Queue，FIFO 先进先出） | 栈（Stack，LIFO 后进先出）或递归（系统调用栈）\n'
                    '空间复杂度 | O(w)，w 为树/图的最大宽度；最坏情况（满二叉树最后一层）约 O(n) | O(h)，h 为树/图的最大深度；最坏情况（退化为链）约 O(n)\n'
                    '时间复杂度 | O(V+E)，每个节点和边均被处理一次 | O(V+E)，每个节点和边均被处理一次\n'
                    '最短路径 | 在无权图中天然保证找到从起点到任一节点的最短路径（按层数度量） | 不保证最短路径——先找到的路径可能经过更多节点\n'
                    '适用场景 | 层序遍历、无权图最短路径、社交网络中的"几度好友" | 连通性检测、拓扑排序、寻找桥和割点、回溯算法\n'
                    'visited标记时机 | 入队时立即标记（防止同层重复入队） | 入栈时标记或递归进入时标记（防止同路径上重复访问）\n'
                    '实现难度 | 需要显式维护队列，代码量稍多 | 递归实现简洁（3-4行），非递归需手动维护栈'
                ),
            },
            {
                'kind': 'warnings',
                'heading': '常见误区一：visited 标记时机错误',
                'content': (
                    '错误现象：BFS 中在节点出队时才标记 visited，而非入队时标记。'
                    '后果：同一层的两个节点可能同时将同一个邻居入队两次，导致结果序列中出现重复节点或无限循环。'
                    '正确做法：入队（或入栈）时立即标记 visited[node]=true。'
                    '口诀："一入队就标记，出队只是读取"。'
                    '验证方法：在图中故意构造一个三角形（3个节点两两相连），如果用出队标记，中间节点会被重复入队。'
                ),
            },
            {
                'kind': 'warnings',
                'heading': '常见误区二：混淆前序遍历和图 DFS',
                'content': (
                    '错误现象：把二叉树的"前序遍历"直接等同于"图的DFS"，在不连通图或多连通分量场景下遗漏节点。'
                    '本质差异：二叉树的DFS天然覆盖所有节点（从根出发一定能到达所有节点）；'
                    '图的DFS必须配合 visited 数组和"对每个未访问节点启动一次DFS"的外层循环，'
                    '否则无法遍历不连通的图。'
                    '正确做法：图的 DFS/BFS 标准模板一定包含外层循环 for each vertex: if not visited: dfs(v)。'
                ),
            },
            {
                'kind': 'practice',
                'heading': '即时练习：修改图的邻接表验证 BFS/DFS 差异',
                'content': (
                    '题目：给定图的邻接表 G = {0:[1,3], 1:[0,2,4], 2:[1,5], 3:[0,4], 4:[1,3,5], 5:[2,4]}。'
                    '从节点 0 出发，分别写出 BFS 和 DFS 的完整访问序列（每步记录队列/栈的状态）。'
                    '要求：\n'
                    '(1) BFS 中队列每轮的状态（入队前和出队后）\n'
                    '(2) DFS 中栈每轮的状态（每次 push 和 pop 后）\n'
                    '(3) 在图上用不同颜色标注 BFS（按距离分层）和 DFS（按深度分支）的访问路径\n'
                    '(4) 回答：这个图是连通图吗？如果不连通，BFS 和 DFS 的访问范围有何不同？'
                ),
            },
            {
                'kind': 'answer_hint',
                'heading': '练习提示',
                'content': (
                    'BFS 从 0 出发的访问序列参考：0 → 1,3 → 2,4 → 5（共3层：距离0→1→2）。'
                    '队列状态：[0]→[1,3]→[3,2,4]→[2,4]→[4]→[4,5]→[5]→[]。'
                    'DFS 访问序列参考：0→1→2→5→4→3（假设邻居按升序入栈，先push大的）。'
                    '栈状态：[0]→[1,3]→[2,4,3]→[5,4,3]→[4,3]→[5,3]→[3]→[]。'
                    '该图是连通图（所有6个节点形成一个连通分量），BFS和DFS都能遍历全部节点。'
                    '提示重点：对比 BFS 第3步和 DFS 第3步的队列/栈差异——BFS 在同一层内扩展，DFS 沿一条路径深入。'
                ),
            },
        ],
        'key_concepts': ['BFS', 'DFS', '队列', '栈', 'visited数组', '图遍历', '最短路径'],
        'learning_tips': [
            '用同一个图分别运行BFS和DFS，将队列/栈状态打印到纸上，直观感受FIFO vs LIFO',
            '先理解二叉树的前序遍历（DFS在树上的特例），再扩展到图的DFS',
            '记住"BFS求最短路径"和"DFS检测连通性"是两者的标志性应用',
        ],
        'recommended_usage': (
            '先在纸上画出邻接图，跟随步骤详解手动模拟BFS和DFS各一遍。'
            '然后用对比表理解两者在数据结构上的本质不同。最后完成练习验证理解。'
        ),
        'estimated_time': '35-45 分钟',
        'match_reason': '基于图算法学习目标，生成了BFS与DFS的图解对比讲解，包含队列/栈模拟、visited标记分析和配套练习。',
        'personalized_reason': '基于图算法学习目标，生成了BFS与DFS的图解对比讲解，包含队列/栈模拟、visited标记分析和配套练习。',
        'programming_language_used': lang,
    }


def build_bfs_dfs_practice_card(gen_context: dict) -> dict:
    """Hard override: complete 分层练习 card for BFS and DFS."""
    topic = gen_context.get('topic', 'BFS和DFS')
    lang = gen_context.get('normalized_language', 'C')
    difficulty = gen_context.get('difficulty', '入门')

    return {
        'id': 'res-bfs-dfs-practice-001',
        'title': 'BFS和DFS图遍历算法 — 分层练习',
        'type': '分层练习',
        'course': '数据结构与算法',
        'knowledge_point': 'BFS和DFS',
        'difficulty': difficulty,
        'language': lang,
        'summary': (
            '按基础层、进阶层、提高层递进设计的 BFS/DFS 练习集。基础层侧重概念理解和单算法应用，'
            '进阶层要求 BFS 与 DFS 的综合选择和优化，提高层引入实际场景问题。'
            '每层配有提示和达标检查标准，覆盖从"能写出代码"到"能选择合适的算法"的完整学习路径。'
        ),
        'sections': [
            {
                'kind': 'highlight',
                'heading': 'BFS和DFS分层练习整体说明',
                'content': (
                    '本练习集围绕 BFS 和 DFS 两大图遍历算法设计，按三个层次递进：'
                    '基础题建立对队列（BFS）和栈/递归（DFS）的编程直觉；'
                    '进阶题训练在不同场景下选择正确算法的判断力——什么时候用 BFS 比 DFS 好？'
                    '综合题则挑战综合应用，要求在一个问题中灵活结合两种算法的思想。'
                    '完成全部练习后，你将能熟练应对 LeetCode 中等难度的图遍历题目。'
                ),
            },
            {
                'kind': 'practice',
                'heading': '基础题：给定无向图，写出从 A 出发的 BFS 和 DFS 访问序列',
                'content': (
                    '基础题：用邻接矩阵或邻接表表示以下有向图，并分别写出从节点A出发的BFS和DFS访问序列——'
                    '图：A→B, A→C, B→D, B→E, C→F, E→F。要求：(a)画出图的邻接表结构；'
                    '(b)写出BFS每轮队列变化；(c)写出DFS每轮栈变化（假设邻居按字母序入栈）；'
                    '(d)比较两种遍历得到的访问序列有何不同。\n\n'
                    '基础题：给定二维网格 grid = [\n'
                    '  ["1","1","0","0","0"],\n'
                    '  ["1","1","0","0","0"],\n'
                    '  ["0","0","1","0","0"],\n'
                    '  ["0","0","0","1","1"]\n'
                    ']，其中"1"表示陆地、"0"表示水域。'
                    '使用 BFS 或 DFS 统计岛屿数量（连通的"1"属于同一个岛屿）。'
                    '要求写出完整的 visited 标记逻辑，并在图上标注每个岛屿的边界。'
                    '这是 LeetCode 200"岛屿数量"的原型——面试出现频率极高。'
                ),
            },
            {
                'kind': 'answer_hint',
                'heading': '基础题提示',
                'content': (
                    '基础题提示：邻接表为 {A:[B,C], B:[D,E], C:[F], D:[], E:[F], F:[]}。'
                    'BFS(A): [A]→popA pushB,C→[B,C]→popB pushD,E→[C,D,E]→popC pushF→[D,E,F]→... '
                    '最终序列 A,B,C,D,E,F（按层输出）。DFS(A): [A]→popA pushC,B→[B,C]→popB pushE,D→... '
                    '最终序列取决于入栈顺序（先C后B与先B后C不同），典型结果为 A,B,D,E,F,C。'
                    '\n基础题提示：遍历每个格子，如果值为"1"且未访问，则启动BFS/DFS将其所属岛屿全部标记为已访问，'
                    '岛屿数+1。visited 可以用与原网格同尺寸的 boolean 数组，也可以直接在 grid 上将访问过的"1"改为"0"'
                    '（修改原数组省空间）。'
                ),
            },
            {
                'kind': 'practice',
                'heading': '进阶题：分析 visited 数组在入队/出队或递归进入时标记的差异',
                'content': (
                    '进阶题：迷宫最短路径（BFS天然优势）——给定 n×m 的迷宫矩阵，0 表示通路、1 表示墙壁。'
                    '从左上角 (0,0) 出发到右下角 (n-1,m-1)，每次可以向上/下/左/右移动一步。'
                    '求最短路径的长度（步数）。如果无法到达返回 -1。\n'
                    '思考：(a) 为什么这道题用 BFS 而非 DFS？(b) 如果要求输出完整的最短路径（不仅是长度），'
                    '如何在 BFS 中记录路径？提示：用 parent 字典/数组记录每个节点的前驱。\n'
                    '核心考点：visited 数组标记时机——BFS 必须在入队时标记而非出队时标记，'
                    '否则同层节点可能被重复入队导致性能退化。DFS 则在递归进入时标记。\n\n'
                    '进阶题：课程表（DFS拓扑排序）——给定 numCourses 门课程和 prerequisites 数组（先修关系），'
                    '判断是否可能完成所有课程。例如 numCourses=4, prerequisites=[[1,0],[2,1],[3,2]]'
                    '表示 0→1→2→3 的依赖链，可以完成。但如果存在循环依赖（如 [[0,1],[1,0]]），则不可能完成。\n'
                    '思考：(a) 如何在 DFS 中检测环？提示：用三种状态标记节点——0=未访问、1=访问中（在当前递归栈中）、'
                    '2=已完成；(b) BFS 有对应的解法吗？（提示：入度表 + 拓扑排序）哪种更直观？'
                ),
            },
            {
                'kind': 'answer_hint',
                'heading': '进阶题提示',
                'content': (
                    '进阶题提示：BFS 从起点出发逐层扩展，首次抵达终点的层数即最短路径长度（无权图中BFS的最短路径性质）。'
                    'DFS 在这道题上需要遍历所有可能路径取最小值，效率远低于 BFS。'
                    '记录路径的方法：在 BFS 的每一步中，将当前节点的前驱存入 parent[x][y] = (prev_x, prev_y)，'
                    '抵达终点后从终点沿 parent 回溯到起点（使用栈或递归将路径反转）。'
                    '\n进阶题提示：DFS 三色标记法——WHITE=0（未访问），GRAY=1（当前递归栈中），BLACK=2（已完成）。'
                    'DFS 过程中遇到 GRAY 节点说明存在环。BFS 解法：构建入度表，将所有入度为 0 的节点入队，'
                    '每次出队一个节点并将其所有后继的入度减 1（新入度为 0 则入队）。最终如果处理的节点数 < numCourses，说明存在环。'
                ),
            },
            {
                'kind': 'practice',
                'heading': '综合题：使用 BFS 求最短步数，或使用 DFS 统计连通分量',
                'content': (
                    '综合题（双向 BFS 优化）：在进阶题（迷宫最短路径）的基础上，'
                    '实现从起点和终点同时进行 BFS 的双向搜索版本。当两个搜索的前沿相遇时即找到最短路径。\n'
                    '要求：(a) 实现两个队列分别从起点和终点扩展；(b) 维护两个 visited 矩阵分别记录各侧的访问步数；'
                    '(c) 当某一步中一个队列的节点在另一个队列的 visited 中已存在时，算法结束——最短路径 = bfs1步数 + bfs2步数。\n'
                    '思考：双向 BFS 相比单向 BFS 在时间复杂度上有何优势？'
                    '提示：单向 BFS 搜索范围是以起点为圆心、半径为 d 的圆（面积约 O(b^d)），'
                    '双向 BFS 是两个半径为 d/2 的圆（总面积约 O(b^(d/2))，指数级减少）。'
                    '在迷宫中 b≈4（四个方向），d=20 时，单向搜索约 4^20≈1e12 个状态，双向仅需 2×4^10≈2e6 个状态。'
                ),
            },
            {
                'kind': 'answer_hint',
                'heading': '综合题提示',
                'content': (
                    '综合题提示：双向 BFS 的关键实现细节——(1) 每次迭代选择当前 size 较小的队列进行扩展（优化常数）；'
                    '(2) 两个 visited 数组存的不只是 boolean——需要存每侧到达该节点的步数；'
                    '(3) 相遇条件：一侧扩展的新邻居节点在另一侧的 visited 中已存在且步数≥0。'
                    '测试用例：设计一个 100×100 的迷宫，单向 BFS 耗时约 2 秒，双向 BFS 耗时约 0.05 秒——差异显著。'
                    '进阶挑战：尝试将双向 BFS 的思想应用到 LeetCode 127"单词接龙"（Word Ladder）上。'
                ),
            },
            {
                'kind': 'check_criteria',
                'heading': '每层达标检查标准',
                'content': (
                    '基础题检查标准：能独立写出 BFS（队列 + visited）和 DFS（栈或递归 + visited）的完整代码模板；'
                    '能对任意给定的邻接表从指定起点出发，正确输出 BFS 和 DFS 访问序列；'
                    '能解释 visited 标记时机为什么必须在入队/入栈时而非出队/出栈时。'
                    '\n进阶题检查标准：能在读题后判断用 BFS 还是 DFS——涉及"最短"/"最少"/"层"→BFS；'
                    '涉及"所有路径"/"是否存在环"/"连通分量"→DFS；能独立完成岛屿数量和课程表两道题的完整实现。'
                    '\n综合题检查标准：能独立实现双向 BFS 并在标准迷宫测试用例上观察到性能提升；'
                    '能阐述双向 BFS 在时间复杂度上的优势原理（指数级减半）；'
                    '能举出至少 2 个适合双向 BFS 的实际应用场景（如社交网络中的"共同好友距离"、拼写检查中的单词接龙）。'
                ),
            },
            {
                'kind': 'warnings',
                'heading': '练习中的常见陷阱',
                'content': (
                    '陷阱1（BFS用栈/DFS用队列）：在BFS实现中误用栈（或DFS中误用队列），'
                    '导致算法行为完全错误——BFS变DFS（栈的LIFO）或DFS变BFS（队列的FIFO）。'
                    '这是"代码写对了但数据结构用错了"的典型错误。记住：BFS = 队列，DFS = 栈/递归。'
                    '\n陷阱2（visited数组忘记重置）：在多组测试用例之间忘记重置 visited 数组，'
                    '导致第二组及后续测试用例的结果受前一组污染，出现"偶发正确、偶发错误"的诡异行为。'
                    '\n陷阱3（邻接矩阵 vs 邻接表的遍历效率）：在稀疏图（边数远小于 V²）上使用邻接矩阵，'
                    '每次找邻居需要 O(V) 扫描一整行，BFS/DFS 总复杂度从 O(V+E) 退化为 O(V²)。'
                    '除非题目明确图是稠密的，否则一律用邻接表。'
                ),
            },
            {
                'kind': 'next_action',
                'heading': '完成练习后的学习路径',
                'content': (
                    '完成 BFS/DFS 三层练习后，建议进入以下方向：(1) 图的最短路径算法——'
                    'Dijkstra（带权图的最短路径，BFS的加权推广）、Bellman-Ford（含负权边）；'
                    '(2) 最小生成树——Prim（类似Dijkstra的贪心扩展）和 Kruskal（并查集 + 排序）；'
                    '(3) 拓扑排序的两种实现（DFS 三色标记法 vs BFS 入度法），'
                    '并挑战 LeetCode 210（课程表II——输出拓扑序列）；'
                    '(4) 回溯算法专题——DFS 与回溯的关系（回溯=DFS+状态恢复），挑战 N皇后、数独、全排列。'
                ),
            },
        ],
        'key_concepts': ['BFS', 'DFS', '队列', '栈', 'visited', '最短路径', '拓扑排序', '双向BFS'],
        'learning_tips': [
            '每道题先在自己的环境中实际编码并运行通过，再看提示',
            '对比 BFS 和 DFS 在同一道题上的实现差异，培养"选择合适算法"的直觉',
            'BFS/DFS 是图算法的基础——花足够时间打牢基础，后续学习最短路径和拓扑排序会轻松很多',
        ],
        'recommended_usage': (
            '从基础层开始逐层推进，每层达标后再进入下一层。'
            '每道题先在本地编码实现并通过测试，再对照提示检查自己的解法。'
            '进阶层和高阶层的题目建议限时完成（30-45分钟/题）模拟面试节奏。'
        ),
        'estimated_time': '90-120 分钟（分2-3次完成）',
        'match_reason': '基于图算法学习目标，生成了BFS/DFS三层递进练习题集，覆盖基础实现到双向BFS优化。',
        'personalized_reason': '基于图算法学习目标，生成了BFS/DFS三层递进练习题集，覆盖基础实现到双向BFS优化。',
        'programming_language_used': lang,
    }


def build_dp_project_card(gen_context: dict) -> dict:
    """Hard override: complete 项目案例 card for dynamic programming (0/1 knapsack)."""
    topic = gen_context.get('topic', '动态规划入门')
    lang = gen_context.get('normalized_language', 'Python')
    difficulty = gen_context.get('difficulty', '入门')

    return {
        'id': 'res-dp-project-001',
        'title': '基于动态规划的0/1背包问题求解器 — 项目案例',
        'type': '项目案例',
        'course': '数据结构与算法',
        'knowledge_point': '动态规划入门',
        'difficulty': difficulty,
        'language': lang,
        'summary': (
            '完整的 0/1 背包问题求解器项目，涵盖自顶向下（记忆化搜索）和自底向上（DP 表格）'
            '两种实现。从状态定义和状态转移方程出发，逐步搭建项目模块结构，'
            '编写核心代码框架，并包含空间优化（一维 dp）和回溯选品功能。'
            '适合作为动态规划入门的首个实践项目，25+ 行 Python 核心代码可直接运行。'
        ),
        'sections': [
            {
                'kind': 'task',
                'heading': '项目任务描述',
                'content': (
                    '项目名称：基于动态规划的 0/1 背包问题求解器。'
                    '\n项目背景：0/1 背包问题是动态规划最经典的应用场景之一——'
                    '给定 n 件物品，每件物品有重量 w[i] 和价值 v[i]，'
                    '在背包总容量 W 的限制下选择物品（每件最多选一次），使总价值最大化。'
                    '这是计算机科学中"有限资源下的最优决策"问题的原型，广泛应用于资源分配、投资决策等领域。'
                    '\n核心目标：实现一个程序，读取物品列表和背包容量，'
                    '输出最大总价值和所选物品列表。要求同时支持自顶向下（记忆化搜索）和自底向上（DP 表格）两种实现，'
                    '并能对比两种方法的运行时间和空间占用。'
                    '\n输入格式：JSON 文件，字段包括 "capacity"（背包容量，整数）、'
                    '"items"（物品列表，每项含 "name"、"weight"、"value"）。'
                    '\n输出格式：JSON 文件，字段包括 "max_value"（最大价值）、'
                    '"selected_items"（选中的物品名称列表）、"method"（使用的算法）、"elapsed_ms"（运行时间）。'
                    '\n约束条件：物品数量 n ∈ [1, 100]，容量 W ∈ [1, 10^4]，重量和价值均为正整数。'
                ),
            },
            {
                'kind': 'steps',
                'heading': '分阶段实现步骤',
                'steps': [
                    '第1步：DP状态定义与转移方程——定义dp[i][w]表示"前i件物品，容量为w时的最大价值"。写出状态转移方程：dp[i][w]=max(dp[i-1][w], dp[i-1][w-wt[i]]+val[i]) if w>=wt[i]，否则dp[i][w]=dp[i-1][w]。在纸上手算n=3,wt=[2,1,3],val=[4,2,3],W=4的完整dp表格以验证方程正确性。核心理解：每个dp[i][w]状态仅依赖dp[i-1][*]（上一行），这揭示了子问题的重叠性和最优子结构。',
                    '第2步：设计项目模块结构——(a)parser.py：读取JSON输入，校验字段合法性；(b)solver.py：核心算法模块，包含Solver抽象基类和两个具体实现（MemoSolver记忆化搜索、DPSolver自底向上）；(c)tracer.py：回溯dp表格输出选中的物品列表；(d)runner.py：命令行入口，协调各模块并计时。每个模块独立可测试，通过明确接口（max_value, selected_items）交互。',
                    '第3步：实现自底向上DP版本（DPSolver）——初始化dp为(n+1)×(W+1)的二维数组（全0）。遍历顺序：通常从小规模子问题到大规模子问题依次计算，外层循环 i 从 1 到 n（逐行扩充物品范围），内层循环 w 从 0 到 W（逐列扩充容量），确保计算 dp[i][w] 时 dp[i-1][w] 和 dp[i-1][w-wt_i] 等前置状态已经完成。如果wt_i<=w则dp[i][w]=max(dp[i-1][w], dp[i-1][w-wt_i]+val_i)，否则dp[i][w]=dp[i-1][w]。关键细节：i从1开始（对应items[0]），dp[0][*]和dp[*][0]全为0（边界条件）。',
                    '第4步：实现记忆化搜索版本（MemoSolver）——递归函数dfs(i, w)返回前i件物品容量w的最大价值，memo={(i,w): value}缓存已计算状态。递归出口：i==0或w==0返回0。两种方法的代码风格差异：DP是"从最小子问题递推到原问题"（自底向上），记忆化是"从原问题递归到最小子问题然后回溯"（自顶向下）。两种方法结果相同但思考方向相反，理解这个差异是DP入门的核心门槛。',
                    '第5步：实现回溯模块（tracer.py）——从dp[n][W]出发逆向追踪选中的物品：如果dp[i][w]!=dp[i-1][w]（说明第i件被选中），将items[i-1].name加入结果，w-=items[i-1].weight；i-=1继续。直到i==0或w==0。这是DP的核心技巧——在求最优值的同时重建最优方案，而非仅仅输出一个数字。',
                    '第6步：实现空间优化版（一维dp）——二维dp的dp[i][*]只依赖dp[i-1][*]，可压缩为一维dp[W+1]。核心代码：for item in items: for w in range(W, item.weight-1, -1): dp[w]=max(dp[w], dp[w-item.weight]+item.value)。内层循环必须从W向0反向遍历——正向遍历会变成完全背包（允许同一物品被重复选取）。这是"正确性 vs 性能"的经典案例。',
                    '第7步：测试与性能对比——设计5组测试用例（n=5,10,20,50,100），运行三种实现（DP二维、DP一维、记忆化搜索），记录运行时间和内存峰值。分析：二维DP空间O(nW)，一维DP空间O(W)，记忆化搜索时间和空间均为O(nW)但递归栈额外开销。编写对比报告和性能图表，验证"一维dp反向遍历"的正确性（用n=1,wt=[2],val=[10],W=4测试——正向遍历输出20，反向遍历输出10）。',
                ],
            },
            {
                'kind': 'design',
                'heading': '架构与数据结构设计',
                'content': (
                    '核心数据结构——二维dp表：dp[i][w]是一个(n+1)×(W+1)的二维整数数组，'
                    '第0行和第0列初始化为0（表示0件物品或容量为0时价值为0）。'
                    'dp[i][w]存储了前i件物品在容量w下的最优解，每个格子只依赖上一行和左边的格子，'
                    '揭示了DP的两个核心性质——最优子结构（每个格子由已求解的子问题决定）和重叠子问题（同一状态被多次查询）。'
                    '\n状态定义：dp[i][w] = 考虑前i件物品，背包容量为w时能获得的最大价值。'
                    '\n状态转移：dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt[i]]+val[i])，含义是不选第i件 vs 选第i件。'
                    '\n初始化：dp[0][*] = 0（0件物品时价值为0），dp[*][0] = 0（容量为0时价值为0）。'
                    '\n遍历顺序：先遍历行再遍历列——外层循环 i 从 1 到 n（逐步扩充物品范围），内层循环 w 从 0 到 W（逐列扩充容量）。'
                    '核心原则是保证计算 dp[i][w] 时它所依赖的旧状态 dp[i-1][w] 和 dp[i-1][w-wt_i] 已经被计算完成。'
                    '空间优化版（一维dp）的遍历顺序需要反向——内层循环从 W 到 0 递减遍历，'
                    '这样 dp[w-wt[i]] 仍是上一轮（i-1）的值，不会被本轮（i）覆盖，确保每件物品只被使用一次。'
                    '\n返回结果：从 dp[n][W] 读取最大总价值，然后通过回溯 dp 表格反推出选中的物品列表。'
                    '\n模块接口设计：(1)Solver.solve(items, capacity)→(max_value, dp_table)——返回最优值和DP表格；'
                    '(2)Tracer.trace(dp_table, items, capacity)→selected_items——回溯选项列表；'
                    '(3)所有模块通过值传递交互（不共享可变状态），确保并发安全和可测试性。'
                    '\n空间优化策略：一维dp数组替代二维——dp[w]=max(dp[w], dp[w-wt[i]]+val[i])，'
                    'w从W向0递减遍历。这个方向选择是决定性的——正向遍历等价于完全背包（每件物品无数件），'
                    '反向遍历才是0/1背包（每件物品仅一件）。理解这一点就掌握了0/1背包与完全背包的全部区别。'
                ),
            },
            {
                'kind': 'code',
                'heading': '核心代码框架（Python）',
                'language': 'Python',
                'content': (
                    '"""0/1 Knapsack — DP + Memoization + Traceback"""\n'
                    'from typing import List, Tuple\n'
                    'import json, time, sys\n'
                    '\n'
                    'class Item:\n'
                    '    def __init__(self, name: str, weight: int, value: int):\n'
                    '        self.name = name\n'
                    '        self.weight = weight\n'
                    '        self.value = value\n'
                    '\n'
                    '# ── 自底向上 DP（二维）──\n'
                    'def knapsack_dp(items: List[Item], W: int) -> Tuple[int, List[str]]:\n'
                    '    n = len(items)\n'
                    '    dp = [[0] * (W + 1) for _ in range(n + 1)]\n'
                    '    # dp[i][w] = 前i件物品，容量w时的最大价值\n'
                    '    for i in range(1, n + 1):\n'
                    '        wt_i = items[i - 1].weight\n'
                    '        val_i = items[i - 1].value\n'
                    '        for w in range(W + 1):\n'
                    '            if wt_i <= w:\n'
                    '                dp[i][w] = max(dp[i - 1][w],\n'
                    '                               dp[i - 1][w - wt_i] + val_i)\n'
                    '            else:\n'
                    '                dp[i][w] = dp[i - 1][w]\n'
                    '    # 回溯选中的物品\n'
                    '    selected = []\n'
                    '    w = W\n'
                    '    for i in range(n, 0, -1):\n'
                    '        if dp[i][w] != dp[i - 1][w]:\n'
                    '            selected.append(items[i - 1].name)\n'
                    '            w -= items[i - 1].weight\n'
                    '    selected.reverse()\n'
                    '    return dp[n][W], selected\n'
                    '\n'
                    '# ── 记忆化搜索（自顶向下）──\n'
                    'def knapsack_memo(items: List[Item], W: int) -> int:\n'
                    '    memo = {}\n'
                    '    def dfs(i: int, w: int) -> int:\n'
                    '        if i == 0 or w == 0:\n'
                    '            return 0\n'
                    '        if (i, w) in memo:\n'
                    '            return memo[(i, w)]\n'
                    '        if items[i - 1].weight > w:\n'
                    '            memo[(i, w)] = dfs(i - 1, w)\n'
                    '        else:\n'
                    '            memo[(i, w)] = max(\n'
                    '                dfs(i - 1, w),\n'
                    '                dfs(i - 1, w - items[i - 1].weight) + items[i - 1].value\n'
                    '            )\n'
                    '        return memo[(i, w)]\n'
                    '    return dfs(n, W)\n'
                    '\n'
                    '# ── 空间优化版（一维dp）──\n'
                    'def knapsack_1d(items: List[Item], W: int) -> int:\n'
                    '    dp = [0] * (W + 1)\n'
                    '    for item in items:\n'
                    '        # 必须反向遍历！正向=完全背包\n'
                    '        for w in range(W, item.weight - 1, -1):\n'
                    '            dp[w] = max(dp[w], dp[w - item.weight] + item.value)\n'
                    '    return dp[W]\n'
                    '\n'
                    '# ── 主程序 ──\n'
                    'if __name__ == "__main__":\n'
                    '    items = [Item("A", 2, 4), Item("B", 1, 2), Item("C", 3, 3)]\n'
                    '    W = 4\n'
                    '    t0 = time.perf_counter()\n'
                    '    max_val, sel = knapsack_dp(items, W)\n'
                    '    elapsed = (time.perf_counter() - t0) * 1000\n'
                    '    result = {"max_value": max_val, "selected_items": sel,\n'
                    '              "method": "dp", "elapsed_ms": round(elapsed, 3)}\n'
                    '    print(json.dumps(result, ensure_ascii=False, indent=2))\n'
                ),
            },
            {
                'kind': 'warnings',
                'heading': '常见实现风险一：一维dp循环方向写反',
                'content': (
                    '最常见也最致命的错误：在空间优化版中把内层循环 for w in range(W, ...) 写成正向 range(0, W+1)。'
                    '正向遍历时 dp[w-wt[i]] 已经是本轮更新过的值（可能已包含了当前物品），'
                    '导致一件物品被重复选取——变成了完全背包而非 0/1 背包。'
                    '验证方法：用 n=1, wt=[2], val=[10], W=4 测试——正向遍历输出 20（相当于选了两次物品），'
                    '反向遍历正确输出 10（只能选一次）。这是 0/1 背包和完全背包的唯一实现差异。'
                ),
            },
            {
                'kind': 'warnings',
                'heading': '常见实现风险二：dp表格下标偏移混淆',
                'content': (
                    'dp[i][w] 中的 i 表示"前 i 件物品"而非"第 i 件"。因此 items[0] 对应 dp[1][*]——'
                    '代码中访问 items[i-1].weight 而非 items[i].weight。'
                    '如果弄错下标偏移量，整个 dp 表格都会错位。建议在代码中注释"dp[i] 对应 items[0..i-1]"，'
                    '并在循环中显式写 wt_i = items[i-1].weight 而非直接内联访问——增加一层命名变量来提升可读性。'
                ),
            },
            {
                'kind': 'warnings',
                'heading': '常见实现风险三：回溯时忘记 selected.reverse()',
                'content': (
                    '回溯是从 dp[n][W] 向 dp[0][0] 逆向追踪，因此收集到的物品顺序是反的（最后选中的最先被收集）。'
                    '忘记在 return 前调用 selected.reverse() 会导致输出列表中物品顺序与直觉相反，'
                    '虽然在"仅需输出物品名称"的场景下不影响正确性，但在要求按某种顺序输出的题目中会判错。'
                    '建议养成习惯：回溯收集后统一调用 reverse() 或使用 list.insert(0, item) 在头部插入。'
                ),
            },
            {
                'kind': 'next_action',
                'heading': '项目拓展方向',
                'content': (
                    '拓展方向一（完全背包）：修改约束条件，允许每件物品选取无限次。'
                    '只需将一维 dp 的内层循环改为正向遍历——这正是"正向=完全背包，反向=0/1背包"这一规律的直接验证。'
                    '跑同一组输入，对比两种约束下的最大价值变化。'
                    '\n拓展方向二（多维背包）：增加一个约束维度（如体积限制），将 dp 扩展为三维 dp[i][w][v]。'
                    '思考：三维 dp 能否压缩为二维？空间优化的方向是否与一维优化遵循相同法则？'
                    '\n拓展方向三（性能基准测试）：用 n=100, W=10000 测试三种实现（DP二维、DP一维、记忆化搜索）'
                    '的运行时间和内存占用，绘制 n-W-时间 三维图表。'
                    '分析在何种参数范围内哪种实现更优——这是面试中展示"工程化思维"的高价值素材。'
                    '\n拓展方向四（变种问题）：挑战 LeetCode 416（分割等和子集——背包问题的直接变体）、'
                    '494（目标和）、322（零钱兑换——完全背包变体）。这三道题覆盖了背包问题的三个主要变种。'
                ),
            },
        ],
        'key_concepts': ['动态规划', '0/1背包', '状态定义', '状态转移方程', '记忆化搜索', '空间优化'],
        'learning_tips': [
            '先手算 n=3 的小规模 dp 表格，验证状态转移方程的正确性后再写代码',
            '对比自底向上 DP 和记忆化搜索的代码，理解两种思考方向的差异',
            '在本地运行一维 dp，故意将内层循环改为正向遍历，观察输出差异，加深理解',
        ],
        'recommended_usage': (
            '先理解状态定义和转移方程（第1步），在纸上手算验证后开始搭建项目骨架。'
            '按步骤实现三种版本的求解器，每步完成后用 n=3 的小规模数据验证输出。'
            '最后完成性能对比测试和一篇简要的项目总结。'
        ),
        'estimated_time': '60-90 分钟',
        'match_reason': '基于动态规划入门学习目标，生成了0/1背包完整项目案例，涵盖状态定义、转移方程、两种实现和空间优化。',
        'personalized_reason': '基于动态规划入门学习目标，生成了0/1背包完整项目案例，涵盖状态定义、转移方程、两种实现和空间优化。',
        'programming_language_used': lang,
    }


def _build_minimal_cards(gen_context: dict, allowed_types: list[str]) -> list[dict]:
    """Build exactly one card per allowed type — used when filter removes all cards."""
    topic = gen_context.get('topic', '')
    module = gen_context.get('module', '')
    lang = gen_context.get('normalized_language', 'Python')
    display = topic.strip()

    cards: list[dict] = []
    for i, rt in enumerate(allowed_types):
        sections = _build_type_sections(rt, module, topic, lang)
        cards.append({
            'id': f'res-min-{i + 1:03d}',
            'title': f'{display} — {rt}',
            'type': rt,
            'course': '数据结构与算法',
            'knowledge_point': display,
            'difficulty': gen_context.get('difficulty', '入门'),
            'language': lang,
            'summary': f'围绕"{display}"的{rt}学习资源，适配{module}模块。',
            'sections': sections,
            'key_concepts': [display],
            'learning_tips': [f'建议配合{display}的练习巩固理解'],
            'recommended_usage': f'按 section 顺序学习{display}的核心内容。',
            'estimated_time': '20-30分钟',
            'match_reason': f'基于{display}主题自动生成的最小{rt}卡。',
            'personalized_reason': f'基于{display}主题自动生成的最小{rt}卡。',
            'programming_language_used': lang,
        })
    return cards


def finalize_resource_cards(cards: list[dict], gen_context: dict) -> list[dict]:
    """
    Phase 3C-3: Post-process resource cards with validation, enrichment, and sanitization.
    1. Validate structural completeness (id, title, type, summary)
    2. Fix code language consistency
    3. Inject programming_language_used and personalized_reason
    4. Scan for forbidden content → force enrichment if found
    5. Validate content depth per type → enrich thin cards
    6. Validate semantic relevance → enrich irrelevant cards
    7. Strip section kinds not allowed for this resource type
    8. Remove empty/null sections
    9. Final scan for residual forbidden patterns
    """
    lang = gen_context.get('normalized_language', 'Python')
    module = gen_context.get('module', '')
    topic = gen_context.get('topic', '')

    _validate_and_fix_code_language(cards, lang)

    total_issues = 0
    enriched_count = 0

    def _scan_text(sections):
        return ' '.join(
            (s.get('content') or '') + ' ' + ' '.join(s.get('steps', []) or [])
            for s in (sections or []) if isinstance(s, dict)
        )

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

        sections = card.get('sections', []) or []
        all_text = _scan_text(sections)
        needs_enrich = False

        # ── Step 1: Scan for forbidden content ──
        for pat in _FORBIDDEN_CONTENT:
            if pat in all_text:
                logger.info(
                    "Forbidden content '%s' in '%s' (%s) — forcing topic-specific enrichment",
                    pat, title, rtype
                )
                needs_enrich = True
                break

        # ── Step 2: Validate content depth ──
        result = validate_resource_depth(card, gen_context)
        if not result['passed']:
            logger.info(
                "Depth validation failed for '%s' (%s): %s — triggering enrichment",
                title, rtype, '; '.join(result['issues'][:4])
            )
            total_issues += len(result['issues'])
            needs_enrich = True

        # ── Step 3: Validate semantic relevance ──
        rel_result = validate_resource_relevance(card, gen_context)
        if not rel_result['passed']:
            logger.info(
                "Relevance validation failed for '%s' (%s): %s — triggering enrichment",
                title, rtype, '; '.join(rel_result['issues'][:4])
            )
            total_issues += len(rel_result['issues'])
            needs_enrich = True

        # ── Step 4: Enrich if any check failed ──
        if needs_enrich:
            card = enrich_resource_card(card, gen_context, result.get('thin_kinds', []))
            enriched_count += 1

        # ── Step 5: Strip invalid section kinds ──
        allowed_kinds = _ALLOWED_KINDS_BY_TYPE.get(rtype)
        if allowed_kinds:
            sections = card.get('sections', []) or []
            kept = [s for s in sections if s.get('kind') in allowed_kinds]
            removed = len(sections) - len(kept)
            if removed:
                logger.info(
                    "Stripped %d invalid section kinds from '%s' (%s)",
                    removed, title, rtype
                )
            card['sections'] = kept

        # ── Step 6: Final forbidden scan on enriched content ──
        final_text = _scan_text(card.get('sections', []))
        for pat in _FORBIDDEN_CONTENT:
            if pat in final_text:
                logger.warning(
                    "CRITICAL: Forbidden pattern '%s' survived enrichment in '%s' (%s)",
                    pat, title, rtype
                )

        # ── Step 7: Clean empty/null sections ──
        sections = card.get('sections', [])
        if isinstance(sections, list):
            cleaned = [s for s in sections if isinstance(s, dict) and (s.get('content') or s.get('steps') or s.get('codeBlock') or s.get('items'))]
            card['sections'] = cleaned

        # ── Step 8: Hard override — topic-specific templates (Phase 14B-3) ──
        topic_key = _match_topic_key(topic)
        rtype = card.get('type', '')

        if _should_override_preorder_cpp(gen_context) and rtype == '代码示例':
            logger.info(
                "Hard override: replacing '%s' with build_preorder_cpp_code_card()",
                card.get('title', '')
            )
            card = build_preorder_cpp_code_card(gen_context)
        elif topic_key == 'quicksort_stability' and rtype == '易错点':
            logger.info(
                "Hard override: replacing '%s' with build_quicksort_stability_mistake_card()",
                card.get('title', '')
            )
            card = build_quicksort_stability_mistake_card(gen_context)
        elif topic_key == 'bfs_dfs' and rtype == '图解讲解':
            logger.info(
                "Hard override: replacing '%s' with build_bfs_dfs_visual_card()",
                card.get('title', '')
            )
            card = build_bfs_dfs_visual_card(gen_context)
        elif topic_key == 'bfs_dfs' and rtype == '分层练习':
            logger.info(
                "Hard override: replacing '%s' with build_bfs_dfs_practice_card()",
                card.get('title', '')
            )
            card = build_bfs_dfs_practice_card(gen_context)
        elif topic_key == 'dynamic_programming' and rtype == '项目案例':
            logger.info(
                "Hard override: replacing '%s' with build_dp_project_card()",
                card.get('title', '')
            )
            card = build_dp_project_card(gen_context)

        # ── Step 8b: Keyword spot-check for critical templates (Phase 14B-5) ──
        card_text = _scan_text(card.get('sections', []))
        if topic_key == 'bfs_dfs' and card.get('type') == '分层练习':
            missing = [kw for kw in ['基础题', '进阶题', '综合题'] if kw not in card_text]
            if missing:
                logger.info(
                    "Keyword check failed: bfs_dfs practice card missing %s — regenerating",
                    missing
                )
                card = build_bfs_dfs_practice_card(gen_context)
        elif topic_key == 'dynamic_programming' and card.get('type') == '项目案例':
            if '遍历顺序' not in card_text:
                logger.info(
                    "Keyword check failed: dp project card missing '遍历顺序' — regenerating"
                )
                card = build_dp_project_card(gen_context)

        valid_cards.append(card)

    # ── Step 9: Filter cards to ONLY selected resource types (Phase 14B-4) ──
    selected = gen_context.get('selected_resource_types')
    if selected is not None:
        # User explicitly requested specific types — filter strictly
        allowed = set()
        for t in selected:
            nt = normalize_resource_type(t)
            if nt:
                allowed.add(nt)
        before = len(valid_cards)
        valid_cards = [c for c in valid_cards if normalize_resource_type(c.get('type', '')) in allowed]
        removed = before - len(valid_cards)
        if removed:
            logger.info(
                "Resource type filter: removed %d cards, kept %d (allowed=%s)",
                removed, len(valid_cards), sorted(allowed)
            )

        # If filtering removed everything, generate minimal fallback cards
        if not valid_cards and allowed:
            logger.warning(
                "All cards filtered out (selected_types=%s) — generating minimal fallback per type",
                sorted(allowed)
            )
            valid_cards = _build_minimal_cards(gen_context, list(allowed))

    # ── Step 10: Cross-topic contamination check ──
    _check_cross_topic_contamination(valid_cards, gen_context)

    if total_issues > 0:
        logger.info(
            "Phase 3C-3: fixed %d issues across %d cards (total=%d cards processed)",
            total_issues, enriched_count, len(valid_cards)
        )

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
    topic: str = "",
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

    Topic priority (Phase 3C-3 fix):
    topic > quick_profile.topic > learning_topic > knowledge_point
    """
    from services.llm_service import get_llm, MockProvider

    # Topic resolution with strict priority
    qp = quick_profile or {}
    effective_topic = (
        (topic or '').strip()
        or (qp.get('topic') or '').strip()
        or (learning_topic or '').strip()
        or (knowledge_point or '').strip()
    )
    # Guard: if topic is still empty or corrupted, use knowledge_point as last resort
    if not effective_topic or effective_topic.isspace() or '?' in effective_topic:
        effective_topic = knowledge_point.strip()

    logger.info(
        "generate_resources: topic=%r lang=%s types=%s",
        effective_topic, language, resource_types
    )

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
        # Phase 14B-4: compute resource_types_used from actual final cards
        result['resource_types_used'] = sorted(set(
            c.get('type', '') for c in result['resource_cards'] if c.get('type')
        ))
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
    # Phase 14B-4: compute resource_types_used from actual final cards
    result['resource_types_used'] = sorted(set(
        c.get('type', '') for c in result['resource_cards'] if c.get('type')
    ))
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


def _get_library_context_for_topic(topic: str, resource_type: str = "") -> str:
    """Read resource library .md content files relevant to topic.

    Phase 14B-3: Uses precise topic keyword matching (not just substring).
    Filters by module, topic keywords, AND optional resource_type.
    """
    index = _load_index()
    if not index:
        return ""
    all_resources = index.get("resources", []) or []
    module = resolve_module_name(topic)

    def _topic_matches(res: dict) -> bool:
        """Check if resource is semantically relevant to the topic."""
        res_topic = (res.get("topic") or res.get("topicCode") or "").strip()
        res_module = res.get("courseCode") or res.get("course") or ""

        # Direct topic match
        if topic in res_topic or topic in res_module:
            return True

        # Module-level match with keyword overlap
        if module and module in res.get("course", ""):
            return True

        # Keyword overlap: extract key terms from topic
        keywords = [t for t in topic.replace(' ', '').split('和') if t]
        keywords = [k for k in keywords if len(k) >= 2]
        if keywords:
            hits = sum(1 for kw in keywords if kw in res_topic or kw in res.get("title", ""))
            if hits >= len(keywords) // 2 + 1:  # majority match
                return True

        return False

    matched = [
        r for r in all_resources
        if _topic_matches(r)
        and (not resource_type or r.get("type") == resource_type)
    ]
    if not matched:
        matched = [r for r in all_resources if _topic_matches(r)]  # fallback: ignore type

    if not matched:
        return ""
    parts = []
    for r in matched[:4]:
        content_path = r.get("contentPath") or r.get("path") or ""
        if not content_path:
            continue
        _, raw = _read_content_file(content_path)
        if raw:
            heading = r.get("title") or ""
            parts.append("=== " + heading + " ===\n" + raw[:2000])
    return "\n\n".join(parts)


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
