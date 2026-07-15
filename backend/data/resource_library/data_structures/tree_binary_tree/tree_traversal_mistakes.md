# 二叉树遍历易错点总结

## 常见错误

### 错误一：混淆遍历顺序

将前序、中序、后序的访问顺序混淆，导致访问根节点的语句放错位置。

### 错误二：遗漏空节点检查

在递归遍历函数中忘记检查节点是否为空（`root == nullptr`），导致访问空指针时程序崩溃。

### 错误三：忽略递归调用栈的空间开销

错误认为递归遍历的空间复杂度是 O(1)，忽略了递归调用栈占用的栈空间。

### 错误四：非递归实现时栈的入栈顺序错误

使用栈实现非递归遍历时，忘记栈的"后进先出"特性，导致左右子节点入栈顺序错误。

## 错误原因

### 错误一原因

对"根-左-右"、"左-根-右"、"左-右-根"三种顺序的理解停留在字面记忆，没有真正理解每种顺序的含义。

### 错误二原因

对递归终止条件理解不清晰，认为"叶子节点的子节点自然不会被访问"，但实际上递归调用会传入这些空指针。

### 错误三原因

只关注了算法的时间复杂度，忽略了递归调用栈的空间开销；或者对递归过程中系统栈的工作机制不了解。

### 错误四原因

对栈的"后进先出"特性理解不透彻，没有意识到需要先入栈右子节点，再入栈左子节点，才能保证左子节点先被访问。

## 正确理解

### 遍历顺序的本质

- **前序遍历**：**先访问根节点**，再递归左子树，最后递归右子树
- **中序遍历**：先递归左子树，**再访问根节点**，最后递归右子树
- **后序遍历**：先递归左子树，再递归右子树，**最后访问根节点**

记忆技巧：根节点的访问位置决定了遍历类型。

### 递归终止条件的必要性

递归函数必须有明确的终止条件。对于二叉树遍历，当传入的节点指针为 `nullptr` 时，说明已经遍历到叶子节点的外部，应该直接返回。

### 递归调用栈的空间开销

每次递归调用都会在系统栈上创建一个栈帧，存储函数参数、局部变量和返回地址。对于深度为 h 的二叉树，递归栈的空间复杂度为 O(h)。

### 非递归遍历的栈操作顺序

栈的特性是"后进先出"，因此：
- 前序遍历：先压右子节点，再压左子节点
- 这样弹出时会先处理左子节点，符合"根-左-右"的顺序

## 错误例子

### 错误一：混淆遍历顺序

**错误代码（意图前序，实际中序）：**

```cpp
void preorder(TreeNode* root) {
    if (root == nullptr) return;
    preorder(root->left);      // 先递归左子树
    cout << root->val << " ";  // 再访问根节点 ← 错误！这是中序遍历
    preorder(root->right);
}
```

对于二叉树：
```
    1
   / \
  2   3
```

**错误输出**（实际是中序）：`2 1 3`
**正确输出**（前序）：`1 2 3`

### 错误二：遗漏空节点检查

**错误代码：**

```cpp
void preorder(TreeNode* root) {
    cout << root->val << " ";  // 没有检查 root 是否为空
    preorder(root->left);
    preorder(root->right);
}
```

**后果**：当访问到叶子节点的子节点（`nullptr`）时，`root->val` 会导致空指针解引用，程序崩溃。

### 错误三：忽略递归调用栈的空间开销

**错误理解**："递归遍历只访问每个节点一次，所以空间复杂度是 O(1)。"

**实际情况**：递归调用会产生调用栈。对于完全倾斜的二叉树（链表），递归深度等于节点数 n，空间复杂度为 O(n)。

### 错误四：非递归实现时栈的入栈顺序错误

**错误代码（意图前序）：**

```cpp
void preorderIterative(TreeNode* root) {
    stack<TreeNode*> st;
    st.push(root);
    while (!st.empty()) {
        TreeNode* node = st.top();
        st.pop();
        cout << node->val << " ";
        if (node->left != nullptr) {
            st.push(node->left);   // 先压左子节点 ← 错误！
        }
        if (node->right != nullptr) {
            st.push(node->right);
        }
    }
}
```

对于二叉树：
```
    1
   / \
  2   3
```

**错误输出**：`1 3 2`（右子树先被访问）
**正确输出**：`1 2 3`（左子树先被访问）

## 正确做法

### 错误一正确做法

```cpp
void preorder(TreeNode* root) {
    if (root == nullptr) return;
    cout << root->val << " ";  // 先访问根节点
    preorder(root->left);
    preorder(root->right);
}
```

### 错误二正确做法

```cpp
void preorder(TreeNode* root) {
    if (root == nullptr) return;  // 必须检查空节点
    cout << root->val << " ";
    preorder(root->left);
    preorder(root->right);
}
```

### 错误三正确做法

正确认识空间复杂度：
- 时间复杂度：O(n)，每个节点访问一次
- 空间复杂度：O(h)，h 为树的高度
  - 平均情况（平衡树）：h = log n
  - 最坏情况（倾斜树）：h = n

### 错误四正确做法

```cpp
void preorderIterative(TreeNode* root) {
    stack<TreeNode*> st;
    st.push(root);
    while (!st.empty()) {
        TreeNode* node = st.top();
        st.pop();
        cout << node->val << " ";
        if (node->right != nullptr) {
            st.push(node->right);  // 先压右子节点
        }
        if (node->left != nullptr) {
            st.push(node->left);   // 后压左子节点
        }
    }
}
```

## 自查题

### 题目一

以下代码的遍历顺序是什么？

```cpp
void traversal(TreeNode* root) {
    if (root == nullptr) return;
    traversal(root->left);
    traversal(root->right);
    cout << root->val << " ";
}
```

**答案要点**：后序遍历（左-右-根）。访问根节点的语句在最后。

### 题目二

指出以下代码的错误：

```cpp
void inorder(TreeNode* root) {
    cout << root->val << " ";
    if (root->left != nullptr) inorder(root->left);
    if (root->right != nullptr) inorder(root->right);
}
```

**答案要点**：
1. 没有检查 `root == nullptr` 的情况
2. 访问根节点的语句位置错误，这实际是前序遍历，不是中序遍历

### 题目三

对于一棵有 n 个节点的完全二叉树，递归前序遍历的空间复杂度是多少？

**答案要点**：O(log n)。完全二叉树的高度为 log n（向下取整），递归栈深度等于树的高度。