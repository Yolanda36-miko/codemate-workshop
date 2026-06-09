# CodeMate 数据库设计文档

## 1. 数据库设计目标

本数据库设计服务于 CodeMate 智学工坊项目，核心目标是：

- **用户画像管理**: 存储和管理学生的六维学习画像数据
- **课程与知识点管理**: 组织课程结构和知识点关系
- **资源与资源包管理**: 管理学习资源和个性化资源包
- **学习路径管理**: 支持个性化学习路径的生成和追踪
- **辅导评估管理**: 记录评估结果和答题详情
- **成长与徽章系统**: 追踪学习成长和成就徽章

核心数据流：**用户画像 → 资源生成 → 资源包 → 路径规划 → 辅导评估 → 成长记录和徽章**

---

## 2. 表结构总览

| 模块 | 数据表 |
|------|--------|
| 用户与画像 | `users`, `student_profiles`, `profile_conversations` |
| 课程与知识点 | `courses`, `course_relations`, `knowledge_points`, `knowledge_point_relations` |
| 资源与资源包 | `resources`, `user_resource_packages` |
| 学习路径 | `learning_paths`, `learning_path_nodes`, `path_node_resources` |
| 辅导评估 | `assessments`, `assessment_answers` |
| 成长与徽章 | `growth_records`, `badges`, `user_badges`, `growth_values` |

---

## 3. 表结构详细设计

### 3.1 users（用户表）

**用途**: 存储系统用户信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 用户主键 |
| username | String(50) | UNIQUE, NOT NULL | 用户名/本地用户标识 |
| display_name | String(100) | NULLABLE | 显示名称 |
| major | String(100) | NULLABLE | 专业 |
| grade | String(50) | NULLABLE | 年级 |
| avatar_text | String(10) | NULLABLE | 头像文字 |
| mode | String(20) | DEFAULT 'demo' | 用户模式 (local/demo/real) |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | DEFAULT NOW, ON UPDATE | 更新时间 |

### 3.2 student_profiles（学生画像表）

**用途**: 存储六维学习画像数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 画像主键 |
| user_id | Integer | FK → users.id, NOT NULL | 所属用户 |
| knowledge_base_score | Integer | NULLABLE | 知识基础分 |
| practice_ability_score | Integer | NULLABLE | 实践能力分 |
| cognitive_styles | Text | NULLABLE | 认知风格标签（JSON） |
| error_patterns | Text | NULLABLE | 易错点（JSON） |
| learning_goals | Text | NULLABLE | 学习目标（JSON） |
| resource_preferences | Text | NULLABLE | 资源偏好（JSON） |
| profile_summary | Text | NULLABLE | 画像摘要 |
| diagnosis_status | String(20) | NULLABLE | 诊断状态 (not_started/in_progress/completed) |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | DEFAULT NOW, ON UPDATE | 更新时间 |

### 3.3 profile_conversations（画像对话表）

**用途**: 存储画像诊断过程中的对话记录

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 对话主键 |
| user_id | Integer | FK → users.id, NOT NULL | 所属用户 |
| role | String(20) | NOT NULL | 角色 (user/assistant/system) |
| message | Text | NOT NULL | 消息内容 |
| extracted_fields | Text | NULLABLE | 本轮提取字段（JSON） |
| missing_fields | Text | NULLABLE | 仍缺失字段（JSON） |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

### 3.4 courses（课程表）

**用途**: 存储课程信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 课程主键 |
| course_code | String(50) | UNIQUE, NOT NULL | 课程编码 |
| name | String(100) | NOT NULL | 课程名称 |
| description | Text | NULLABLE | 课程描述 |
| stage | String(20) | NULLABLE | 推荐学习阶段 |
| positioning | String(50) | NULLABLE | 重点演示/课程群支撑 |
| keywords | Text | NULLABLE | 关键词（JSON） |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | DEFAULT NOW, ON UPDATE | 更新时间 |

### 3.5 course_relations（课程关系表）

**用途**: 存储课程间的依赖关系

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 关系主键 |
| from_course_id | Integer | FK → courses.id, NOT NULL | 源课程 |
| to_course_id | Integer | FK → courses.id, NOT NULL | 目标课程 |
| relation_type | String(20) | NOT NULL | 关系类型 (prerequisite/related/transition) |
| description | Text | NULLABLE | 关系描述 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

### 3.6 knowledge_points（知识点表）

**用途**: 存储课程知识点

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 知识点主键 |
| course_id | Integer | FK → courses.id, NOT NULL | 所属课程 |
| name | String(100) | NOT NULL | 知识点名称 |
| description | Text | NULLABLE | 知识点描述 |
| difficulty | String(20) | NULLABLE | 难度（基础/进阶/综合） |
| tags | Text | NULLABLE | 标签（JSON） |
| common_errors | Text | NULLABLE | 常见错误（JSON） |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | DEFAULT NOW, ON UPDATE | 更新时间 |

### 3.7 knowledge_point_relations（知识点关系表）

**用途**: 存储知识点间的依赖关系

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 关系主键 |
| from_kp_id | Integer | FK → knowledge_points.id, NOT NULL | 源知识点 |
| to_kp_id | Integer | FK → knowledge_points.id, NOT NULL | 目标知识点 |
| relation_type | String(20) | NOT NULL | 关系类型 (prerequisite/related) |
| description | Text | NULLABLE | 关系描述 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

### 3.8 resources（资源表）

**用途**: 存储学习资源

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 资源主键 |
| resource_id | String(50) | UNIQUE, NOT NULL | 外部资源标识 |
| title | String(200) | NOT NULL | 资源标题 |
| course_id | Integer | FK → courses.id | 所属课程 |
| knowledge_point_id | Integer | FK → knowledge_points.id | 所属知识点 |
| resource_type | String(50) | NOT NULL | 资源类型（六类资源之一） |
| difficulty | String(20) | NULLABLE | 难度 |
| language | String(20) | NULLABLE | 编程语言 |
| tags | Text | NULLABLE | 标签（JSON） |
| estimated_time | String(20) | NULLABLE | 预计时长 |
| summary | Text | NULLABLE | 资源摘要 |
| content_path | String(500) | NULLABLE | 资源正文路径 |
| source_type | String(20) | NOT NULL | 来源类型 (library/generated/demo/fallback) |
| source_resource_ids | Text | NULLABLE | 生成资源来源（JSON） |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | DEFAULT NOW, ON UPDATE | 更新时间 |

### 3.9 user_resource_packages（用户资源包表）

**用途**: 存储用户个性化资源包

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 资源包主键 |
| user_id | Integer | FK → users.id, NOT NULL | 所属用户 |
| resource_id | Integer | FK → resources.id | 关联资源 |
| custom_title | String(200) | NULLABLE | 自定义标题 |
| topic | String(100) | NULLABLE | 主题 |
| course_name | String(100) | NULLABLE | 课程名快照 |
| resource_type | String(50) | NULLABLE | 资源类型快照 |
| estimated_time | String(20) | NULLABLE | 预计时长 |
| purpose | String(50) | NULLABLE | 用途（课前预习/课后练习等） |
| priority | String(20) | NULLABLE | 优先级（必学/推荐/拓展） |
| note | Text | NULLABLE | 备注 |
| status | String(20) | DEFAULT 'saved' | 状态 (saved/learning/completed) |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | DEFAULT NOW, ON UPDATE | 更新时间 |

### 3.10 learning_paths（学习路径表）

**用途**: 存储个性化学习路径

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 路径主键 |
| user_id | Integer | FK → users.id, NOT NULL | 所属用户 |
| name | String(100) | NOT NULL | 路径名称 |
| goal | Text | NULLABLE | 学习目标 |
| source | String(20) | NOT NULL | 来源 (generated/demo/manual/fallback) |
| status | String(20) | NOT NULL | 状态 (draft/active/completed) |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | DEFAULT NOW, ON UPDATE | 更新时间 |

### 3.11 learning_path_nodes（学习路径节点表）

**用途**: 存储学习路径中的节点

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 节点主键 |
| path_id | Integer | FK → learning_paths.id, NOT NULL | 所属路径 |
| node_order | Integer | NOT NULL | 节点顺序 |
| title | String(200) | NOT NULL | 节点标题 |
| course_id | Integer | FK → courses.id | 关联课程 |
| knowledge_point_id | Integer | FK → knowledge_points.id | 关联知识点 |
| learning_goal | Text | NULLABLE | 学习目标 |
| estimated_time | String(20) | NULLABLE | 预计时长 |
| status | String(20) | NOT NULL | 状态 (pending/in_progress/completed) |
| growth_targets | Text | NULLABLE | 成长目标（JSON） |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | DEFAULT NOW, ON UPDATE | 更新时间 |

### 3.12 path_node_resources（路径节点资源表）

**用途**: 存储学习路径节点关联的资源

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 关联主键 |
| node_id | Integer | FK → learning_path_nodes.id, NOT NULL | 所属节点 |
| resource_id | Integer | FK → resources.id | 关联资源 |
| source | String(30) | NOT NULL | 来源 (user_package/system_recommended/generated) |
| is_from_user_package | Boolean | DEFAULT FALSE | 是否来自用户资源包 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

### 3.13 assessments（评估表）

**用途**: 存储评估记录

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 评估主键 |
| user_id | Integer | FK → users.id, NOT NULL | 所属用户 |
| topic | String(100) | NULLABLE | 评估主题 |
| question | Text | NULLABLE | 用户原始提问 |
| score | Integer | NULLABLE | 得分 |
| total_questions | Integer | NULLABLE | 题目总数 |
| correct_count | Integer | NULLABLE | 正确数 |
| wrong_points | Text | NULLABLE | 错误知识点（JSON） |
| growth_delta | Text | NULLABLE | 成长值变化（JSON） |
| badge_awarded | Text | NULLABLE | 获得徽章（JSON） |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

### 3.14 assessment_answers（评估答题表）

**用途**: 存储评估答题详情

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 答题主键 |
| assessment_id | Integer | FK → assessments.id, NOT NULL | 所属评估 |
| question_id | String(50) | NULLABLE | 题目编号 |
| question_text | Text | NULLABLE | 题干 |
| selected_answer | String(500) | NULLABLE | 用户答案 |
| correct_answer | String(500) | NULLABLE | 正确答案 |
| is_correct | Boolean | NULLABLE | 是否正确 |
| knowledge_point | String(100) | NULLABLE | 关联知识点 |
| feedback | Text | NULLABLE | 反馈 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

### 3.15 growth_records（成长记录表）

**用途**: 存储成长变化记录

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 记录主键 |
| user_id | Integer | FK → users.id, NOT NULL | 所属用户 |
| source_type | String(30) | NOT NULL | 来源类型 (diagnosis/path_node/assessment/resource_learning/manual) |
| source_id | Integer | NULLABLE | 来源记录ID |
| knowledge_base_delta | Integer | NULLABLE | 知识基础变化 |
| practice_ability_delta | Integer | NULLABLE | 实践能力变化 |
| reason | Text | NULLABLE | 变化原因 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

### 3.16 badges（徽章表）

**用途**: 存储徽章定义

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 徽章主键 |
| badge_code | String(50) | UNIQUE, NOT NULL | 徽章编码 |
| name | String(100) | NOT NULL | 徽章名称 |
| description | Text | NULLABLE | 徽章描述 |
| icon | String(50) | NULLABLE | 徽章图标 |
| condition_type | String(50) | NULLABLE | 获得条件类型 |
| condition_value | String(100) | NULLABLE | 获得条件值 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

### 3.17 user_badges（用户徽章表）

**用途**: 存储用户获得的徽章

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 记录主键 |
| user_id | Integer | FK → users.id, NOT NULL | 所属用户 |
| badge_id | Integer | FK → badges.id, NOT NULL | 关联徽章 |
| earned_at | DateTime | DEFAULT NOW | 获得时间 |
| source_type | String(30) | NULLABLE | 来源类型 |
| source_id | Integer | NULLABLE | 来源ID |

### 3.18 growth_values（成长值表）

**用途**: 存储用户当前成长值状态

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | 记录主键 |
| user_id | Integer | FK → users.id, NOT NULL | 所属用户 |
| total_points | Integer | DEFAULT 0 | 总成长值 |
| level | Integer | DEFAULT 1 | 等级 |
| last_updated_at | DateTime | DEFAULT NOW | 最后更新时间 |

---

## 4. 主键和外键说明

### 4.1 主键列表

| 表名 | 主键字段 |
|------|----------|
| users | id |
| student_profiles | id |
| profile_conversations | id |
| courses | id |
| course_relations | id |
| knowledge_points | id |
| knowledge_point_relations | id |
| resources | id |
| user_resource_packages | id |
| learning_paths | id |
| learning_path_nodes | id |
| path_node_resources | id |
| assessments | id |
| assessment_answers | id |
| growth_records | id |
| badges | id |
| user_badges | id |
| growth_values | id |

### 4.2 外键关系

| 表名 | 外键字段 | 关联表 | 关联字段 |
|------|----------|--------|----------|
| student_profiles | user_id | users | id |
| profile_conversations | user_id | users | id |
| course_relations | from_course_id | courses | id |
| course_relations | to_course_id | courses | id |
| knowledge_points | course_id | courses | id |
| knowledge_point_relations | from_kp_id | knowledge_points | id |
| knowledge_point_relations | to_kp_id | knowledge_points | id |
| resources | course_id | courses | id |
| resources | knowledge_point_id | knowledge_points | id |
| user_resource_packages | user_id | users | id |
| user_resource_packages | resource_id | resources | id |
| learning_paths | user_id | users | id |
| learning_path_nodes | path_id | learning_paths | id |
| learning_path_nodes | course_id | courses | id |
| learning_path_nodes | knowledge_point_id | knowledge_points | id |
| path_node_resources | node_id | learning_path_nodes | id |
| path_node_resources | resource_id | resources | id |
| assessments | user_id | users | id |
| assessment_answers | assessment_id | assessments | id |
| growth_records | user_id | users | id |
| user_badges | user_id | users | id |
| user_badges | badge_id | badges | id |
| growth_values | user_id | users | id |

---

## 5. 表关系说明

### 5.1 关系结构图

```
用户模块
users ──1:N──> student_profiles
users ──1:N──> profile_conversations

课程模块
courses ──1:N──> course_relations (from_course_id)
courses ──1:N──> course_relations (to_course_id)
courses ──1:N──> knowledge_points

知识点模块
knowledge_points ──1:N──> knowledge_point_relations (from_kp_id)
knowledge_points ──1:N──> knowledge_point_relations (to_kp_id)
knowledge_points ──1:N──> resources

资源模块
resources ──1:N──> user_resource_packages

学习路径模块
users ──1:N──> learning_paths
learning_paths ──1:N──> learning_path_nodes
learning_path_nodes ──1:N──> path_node_resources

评估模块
users ──1:N──> assessments
assessments ──1:N──> assessment_answers

成长模块
users ──1:N──> growth_records
users ──1:N──> user_badges
users ──1:N──> growth_values
badges ──1:N──> user_badges
```

---

## 6. Seed 数据说明

### 6.1 预置数据内容

| 数据类型 | 数量 | 说明 |
|----------|------|------|
| 用户 | 2 | demo_user（演示学生）、local_user（本地用户） |
| 课程 | 6 | 程序设计基础、数据结构与算法、计算机组成原理、操作系统、计算机网络、数据库系统 |
| 课程关系 | 1 | 程序设计基础 → 数据结构与算法（prerequisite） |
| 知识点 | 8 | 函数调用、数组边界、递归调用栈、基础调试、二叉树结构、二叉树遍历、递归思想、排序算法基础 |
| 知识点关系 | 2 | 函数调用→递归调用栈→二叉树遍历 |
| 徽章 | 6 | 函数调用入门、递归探索者、数组练习达人、二叉树探索者、代码实践新手、学习路径坚持者 |

### 6.2 数据幂等性

所有种子数据填充操作均支持幂等性，重复执行不会产生重复数据，系统会自动检测已存在的数据并跳过。

---

## 7. 数据库初始化命令

### 7.1 仅创建表

```bash
python backend/scripts/init_db.py
```

**说明**: 创建所有数据库表，如果表已存在则保留现有数据。

### 7.2 创建表并写入种子数据

```bash
python backend/scripts/init_db.py --seed
```

**说明**: 创建表后，调用 seed_db.py 写入基础数据。

### 7.3 重置数据库并写入种子数据

```bash
python backend/scripts/init_db.py --reset --seed
```

**说明**: 删除现有数据库文件，重新创建表并写入种子数据（危险操作）。

### 7.4 检查数据库数据

```bash
python backend/scripts/check_db.py
```

**说明**: 检查数据库中的关键数据量，用于验收验证。

---

## 8. 字段用途分类

### 8.1 前端展示字段

| 表名 | 字段名 | 用途说明 |
|------|--------|----------|
| users | display_name, avatar_text, mode | 用户信息展示 |
| student_profiles | knowledge_base_score, practice_ability_score, profile_summary, diagnosis_status | 画像数据展示 |
| courses | name, course_code, description, stage | 课程信息展示 |
| knowledge_points | name, description, difficulty | 知识点信息展示 |
| resources | title, resource_type, difficulty, estimated_time | 资源信息展示 |
| learning_paths | name, goal, status | 学习路径展示 |
| badges | name, description, icon | 徽章展示 |
| growth_values | total_points, level | 成长值展示 |

### 8.2 LLM 输入字段

| 表名 | 字段名 | 用途说明 |
|------|--------|----------|
| profile_conversations | message, extracted_fields, missing_fields | 画像诊断对话 |
| student_profiles | cognitive_styles, error_patterns, learning_goals, resource_preferences | 学习画像数据 |
| assessment_answers | question_text, selected_answer, feedback | 评估答题数据 |
| resources | summary, tags | 资源内容摘要 |

### 8.3 资源检索字段

| 表名 | 字段名 | 用途说明 |
|------|--------|----------|
| resources | tags, resource_type, difficulty, language, course_id, knowledge_point_id | 资源检索条件 |
| user_resource_packages | topic, purpose, priority, status | 资源包筛选 |

### 8.4 路径生成字段

| 表名 | 字段名 | 用途说明 |
|------|--------|----------|
| knowledge_points | difficulty, course_id | 知识点难度和归属 |
| knowledge_point_relations | relation_type, from_kp_id, to_kp_id | 知识点依赖关系 |
| courses | stage, course_code | 课程阶段和编码 |
| course_relations | relation_type | 课程依赖关系 |
| student_profiles | knowledge_base_score, practice_ability_score, learning_goals | 用户画像数据 |

### 8.5 成长反馈字段

| 表名 | 字段名 | 用途说明 |
|------|--------|----------|
| growth_records | knowledge_base_delta, practice_ability_delta, reason | 成长变化记录 |
| user_badges | earned_at, badge_id | 徽章获得记录 |
| assessments | score, growth_delta, badge_awarded | 评估结果 |
| growth_values | total_points, level | 当前成长状态 |

---

## 9. 本阶段暂不实现内容

根据 Phase 2 数据库建设技术手册要求，本阶段暂不实现以下内容：

- **前端改造**: 不改前端代码，保持现有 mock 数据和界面
- **LLM 集成**: 不接入真实 LLM Provider，不实现 LLM 相关业务逻辑
- **真实 API 改造**: 不修改现有 routers 和 service 层实现
- **登录注册**: 不实现真实用户登录注册功能，仅预留 demo/local 用户
- **Mock 数据删除**: 不删除现有 mock/data 文件

---

## 10. 技术栈说明

| 组件 | 技术 | 版本 |
|------|------|------|
| 数据库 | SQLite | 3.x |
| ORM | SQLAlchemy | 2.0+ |
| 数据验证 | Pydantic | 2.0+ |
| 后端框架 | FastAPI | 0.100+ |

---

## 11. 文件结构

```
backend/
├── database.py          # 数据库连接配置
├── models/
│   ├── __init__.py      # 模型导出
│   ├── user.py          # User 模型
│   ├── profile.py       # StudentProfile, ProfileConversation 模型
│   ├── course.py        # Course, CourseRelation 模型
│   ├── knowledge.py     # KnowledgePoint, KnowledgePointRelation 模型
│   ├── resource.py      # Resource, UserResourcePackage 模型
│   ├── path.py          # LearningPath, LearningPathNode, PathNodeResource 模型
│   ├── assessment.py    # Assessment, AssessmentAnswer 模型
│   └── growth.py        # GrowthRecord, Badge, UserBadge, GrowthValue 模型
├── schemas/
│   ├── __init__.py      # Schema 导出
│   ├── user.py          # User 相关 Schema
│   └── profile.py       # Profile 相关 Schema
└── scripts/
    ├── init_db.py       # 数据库初始化脚本
    ├── seed_db.py       # 种子数据填充脚本
    └── check_db.py      # 数据库检查脚本
```

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-06-09 | Phase 2 数据库设计文档 |
