# 二叉树前序遍历 C++ 代码示例

## 代码目标

本代码演示二叉树前序遍历的递归实现，展示如何按照"根-左-右"的顺序访问二叉树中的所有节点。

## 核心代码

```cpp
#include <iostream>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
};

void preorderTraversal(TreeNode* root) {
    if (root == nullptr) return;
    cout << root->val << " ";
    preorderTraversal(root->left);
    preorderTraversal(root->right);
}

int main() {
    TreeNode* root = new TreeNode(1);
    root->left = new TreeNode(2);
    root->right = new TreeNode(3);
    root->left->left = new TreeNode(4);
    root->right->right = new TreeNode(5);

    cout << "前序遍历结果：";
    preorderTraversal(root);
    cout << endl;

    return 0;
}
```

## 关键步骤解释

### 1. 二叉树节点定义

```cpp
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
};
```

- `val`：存储节点的值
- `left`：指向左子节点的指针
- `right`：指向右子节点的指针
- 构造函数：初始化节点值，并将左右子节点设为 `nullptr`

### 2. 递归遍历函数

```cpp
void preorderTraversal(TreeNode* root) {
    if (root == nullptr) return;
    cout << root->val << " ";
    preorderTraversal(root->left);
    preorderTraversal(root->right);
}
```

- **终止条件**：`if (root == nullptr) return;` — 当节点为空时，直接返回
- **访问根节点**：`cout << root->val << " ";` — 先输出当前节点的值
- **递归左子树**：`preorderTraversal(root->left);` — 递归遍历左子树
- **递归右子树**：`preorderTraversal(root->right);` — 递归遍历右子树

### 3. 主函数测试

```cpp
int main() {
    TreeNode* root = new TreeNode(1);
    root->left = new TreeNode(2);
    root->right = new TreeNode(3);
    root->left->left = new TreeNode(4);
    root->right->right = new TreeNode(5);
    ...
}
```

- 创建一棵二叉树，结构如下：

```
    1
   / \
  2   3
 /     \
4       5
```

## 输入输出示例

### 输入二叉树

```
    1
   / \
  2   3
 /     \
4       5
```

### 输出

```
前序遍历结果：1 2 4 3 5
```

### 访问顺序说明

1. 访问根节点 1
2. 进入左子树，访问根节点 2
3. 进入左子树，访问根节点 4
4. 4 的左右子树为空，返回 2
5. 2 的右子树为空，返回 1
6. 进入右子树，访问根节点 3
7. 3 的左子树为空，进入右子树，访问根节点 5
8. 5 的左右子树为空，返回 3，再返回 1，遍历结束

## 边界条件

### 空树处理

当 `root == nullptr` 时，函数直接返回，不执行任何操作。这是递归的终止条件。

### 叶子节点处理

叶子节点的 `left` 和 `right` 都为 `nullptr`，递归调用时会触发终止条件，自然结束。

### 单节点树

只有一个根节点的树，直接访问该节点后返回。

## 时间复杂度和空间复杂度

### 时间复杂度

**O(n)**，其中 n 是二叉树的节点数。每个节点恰好被访问一次。

### 空间复杂度

**平均 O(log n)**，**最坏 O(n)**。

- **平均情况**：对于平衡二叉树，递归调用栈的深度为树的高度，即 log n。
- **最坏情况**：对于完全倾斜的二叉树（退化为链表），递归调用栈的深度为 n。

## 改写练习

### 练习任务

请将上述递归版本的前序遍历改写为使用栈的非递归版本。

### 提示

1. 使用 `stack<TreeNode*>` 存储待访问的节点
2. 先将根节点入栈
3. 循环：弹出节点 → 访问该节点 → 将右子节点入栈 → 将左子节点入栈（注意顺序）

### 参考伪代码

```cpp
void preorderIterative(TreeNode* root) {
    if (root == nullptr) return;
    stack<TreeNode*> st;
    st.push(root);
    while (!st.empty()) {
        TreeNode* node = st.top();
        st.pop();
        cout << node->val << " ";
        if (node->right != nullptr) {
            st.push(node->right);
        }
        if (node->left != nullptr) {
            st.push(node->left);
        }
    }
}
```

### 答案验证

对于相同的输入二叉树，非递归版本应输出相同的结果：`1 2 4 3 5`。