# 资源库规范文档

## 1. 目录结构

```
backend/data/resource_library/
├── index.json                    # 资源元数据索引文件
├── programming_basics/           # 程序设计基础资源
│   ├── function_call/            # 函数调用主题
│   │   ├── function_call_explainer.md
│   │   ├── function_call_code_examples.md
│   │   └── function_call_exercises.json
│   ├── arrays/                   # 数组主题
│   ├── recursion/                # 递归主题
│   └── debugging/                # 调试主题
└── data_structures/              # 数据结构资源
    ├── binary_tree_traversal/    # 二叉树遍历主题
    ├── binary_tree_structure/    # 二叉树结构主题
    ├── recursion_thinking/       # 递归思想主题
    └── sorting/                  # 排序算法主题
```

## 2. index.json 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 资源唯一标识符，格式：{courseCode}_{topicCode}_{type}_{序号} |
| `title` | string | 是 | 资源标题 |
| `course` | string | 是 | 课程名称（如：程序设计基础、数据结构与算法） |
| `courseCode` | string | 是 | 课程代码（programming_basics / data_structures） |
| `topic` | string | 是 | 主题名称 |
| `topicCode` | string | 是 | 主题代码（小写，下划线分隔） |
| `type` | string | 是 | 资源类型（见第3节） |
| `difficulty` | string | 是 | 难度级别（基础 / 进阶） |
| `language` | string | 是 | 语言类型（Python / 通用） |
| `tags` | array | 是 | 标签列表，用于检索 |
| `estimatedTime` | string | 是 | 预计学习时长（如：15分钟） |
| `summary` | string | 是 | 资源摘要描述 |
| `contentPath` | string | 是 | 正文文件路径（相对路径） |
| `source` | string | 是 | 资源来源（local_resource_library） |
| `version` | string | 是 | 版本号（1.0） |
| `updatedAt` | string | 是 | 更新日期（YYYY-MM-DD） |

## 3. 资源类型说明

### 3.1 个性化讲解文档
- **用途**：对特定概念进行详细讲解，包含适用对象、学习目标、核心概念、分步骤讲解、代码示例、常见错误、自我检查、下一步建议

### 3.2 代码示例与注释
- **用途**：提供代码片段，包含详细注释说明，帮助学生理解代码逻辑

### 3.3 分层练习题
- **用途**：包含多种题型（选择题、代码输出题、代码填空题），帮助学生巩固知识点

### 3.4 知识点思维导图
- **用途**：以结构化方式展示知识点之间的关系，便于快速回顾

### 3.5 项目式学习案例
- **用途**：提供完整的项目案例，展示知识的实际应用

### 3.6 拓展阅读资料
- **用途**：推荐学习方向、关键词和教材章节，无虚假链接

## 4. 正文文件规范

### 4.1 Markdown 文件规范

#### 个性化讲解文档结构
```markdown
# 标题

## 适用对象
描述目标读者

## 学习目标
- 目标1
- 目标2

## 核心概念
讲解核心知识点

## 分步骤讲解
1. 步骤1
2. 步骤2

## 代码示例
```python
# 代码内容
```

## 常见错误
- 错误1
- 错误2

## 自我检查
1. 问题1
2. 问题2

## 下一步建议
推荐后续学习内容
```

#### 代码示例文档结构
```markdown
# 标题

## 示例1标题
```python
# 代码及注释
```

## 示例2标题
```python
# 代码及注释
```
```

#### 思维导图文档结构
```markdown
# 标题

## 一级主题
- 二级主题1
  - 三级主题
- 二级主题2
```

### 4.2 JSON 练习题文件规范

```json
{
  "resourceId": "唯一标识",
  "title": "练习题标题",
  "questions": [
    {
      "id": "q1",
      "type": "single_choice|code_output|code_fill",
      "difficulty": "基础|进阶",
      "knowledgePoint": "知识点",
      "question": "题目内容",
      "options": ["选项1", "选项2", "选项3", "选项4"],
      "answer": "正确答案",
      "explanation": "答案解释"
    }
  ]
}
```

**题型说明**：
- `single_choice`：单选题，必须提供 options 数组
- `code_output`：代码输出题，options 为空数组
- `code_fill`：代码填空题，options 为空数组

## 5. 质量标准与禁止内容

### 5.1 质量标准
- 内容准确无误，符合学科规范
- 语言清晰易懂，适合目标读者
- 代码示例可运行，注释清晰
- 结构完整，符合文档模板

### 5.2 禁止内容
- **禁止虚假链接**：所有链接必须有效，禁止编造链接
- **禁止编造用户**：禁止虚构学生姓名、案例场景等
- **禁止敏感内容**：禁止包含政治敏感、色情、暴力等内容
- **禁止抄袭**：确保内容原创，引用需注明来源

## 6. 维护规则

### 6.1 新增资源流程
1. 在对应主题目录下创建正文文件（.md 或 .json）
2. 在 `index.json` 的 `resources` 数组中添加资源元数据
3. 确保所有必填字段完整

### 6.2 验证检查
新增或修改资源后，必须运行验证脚本：

```bash
cd backend
python scripts/validate_resource_library.py
```

验证内容：
- index.json JSON 格式正确性
- 必填字段完整性
- contentPath 指向文件存在性

### 6.3 更新规范
- 资源内容更新时，同步更新 `updatedAt` 字段
- 版本升级时，更新 `version` 字段
- 保持资源 ID 稳定，不随意修改