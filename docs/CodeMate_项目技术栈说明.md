# CodeMate 项目技术栈说明

---

## 1. 技术栈总览

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | React | 18.3.1 |
| 类型系统 | TypeScript | 5.4.5 |
| 构建工具 | Vite | 5.3.1 |
| CSS 框架 | Tailwind CSS | 3.4.4 |
| 路由 | React Router DOM | 6.23.1 |
| 动画 | Framer Motion | 11.2.10 |
| 图标 | Lucide React | 0.395.0 |
| 后端框架 | FastAPI | ≥0.115.0 |
| 服务器 | Uvicorn | ≥0.30.0 |
| 数据校验 | Pydantic | ≥2.10.0 |
| ORM | SQLAlchemy | ≥2.0.0 |
| 数据库 | SQLite | — |
| LLM SDK | OpenAI SDK / Anthropic SDK | ≥1.0.0 / ≥0.40.0 |
| 模板引擎 | Jinja2 | ≥3.0.0 |
| 环境管理 | python-dotenv | ≥1.0.0 |

---

## 2. 系统架构概览

CodeMate 采用前后端分离的 B/S 架构，前端为单页应用（SPA），后端为 RESTful API 服务。

```
┌─────────────────────────────────────────────────┐
│  浏览器 (Browser)                                │
│  React 18 SPA  ·  TypeScript  ·  Tailwind CSS   │
│  localhost:5173                                  │
└────────────────┬────────────────────────────────┘
                 │  HTTP / JSON
                 │  /api/* → localhost:8000
                 ▼
┌─────────────────────────────────────────────────┐
│  FastAPI 后端 (Uvicorn)                          │
│  localhost:8000                                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐ │
│  │ Routers  │  │ Services │  │ LLM Provider  │ │
│  │ (7 模块) │→ │ (9 服务) │→ │ (4 种后端)     │ │
│  └──────────┘  └──────────┘  └───────────────┘ │
│  ┌──────────────────────────────────────────┐   │
│  │ SQLAlchemy ORM  →  SQLite (codemate.db)  │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

- **开发模式**：Vite 开发服务器（5173 端口）将 `/api` 请求代理到 Uvicorn（8000 端口）
- **数据库**：SQLite 单文件数据库，位于 `backend/codemate.db`
- **LLM 调用**：通过 Provider 抽象层统一对接 OpenAI / Anthropic / DeepSeek / Mock

---

## 3. 前端技术栈

### 3.1 React 18 + TypeScript 5.4

- 使用 React 18 并发特性与 Hooks 函数式组件
- TypeScript 严格模式（`strict: true`），编译目标 ES2020，JSX 模式 `react-jsx`
- 所有组件均为 `.tsx` 文件，类型定义集中在 `src/types/index.ts`

### 3.2 Vite 5 构建

- 使用 `@vitejs/plugin-react` 插件
- 开发服务器端口 5173，支持 HMR（热模块替换）
- 代理配置：`/api` 路径转发至 `http://localhost:8000`

```typescript
// vite.config.ts 核心配置
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } },
  },
})
```

### 3.3 Tailwind CSS 3.4

- 自定义主题色 `primary` 系列（紫罗兰色系，50–900）
- 字体栈：`Inter` + `Noto Sans SC`（中文）+ `system-ui`
- 自定义圆角（`xl` / `2xl` / `3xl`）、阴影（`card` / `card-hover` / `glow`）
- 自定义动画：`fade-in` / `slide-up` / `scale-in` / `pulse-slow`
- 扫描路径：`./index.html` 和 `./src/**/*.{js,ts,jsx,tsx}`

### 3.4 React Router DOM 6

SPA 路由结构（`src/App.tsx`）：

| 路径 | 页面组件 | 功能 |
|------|----------|------|
| `/` | `Dashboard` | 首页仪表盘 |
| `/profile` | `Profile` | 学习画像 |
| `/courses` | `CourseCenter` | 课程中心 |
| `/resources` | `ResourceGen` | 资源生成 |
| `/path` | `LearningPath` | 学习路径 |
| `/assessment` | `Assessment` | 智能评估 |

所有页面包裹在 `Layout` 组件内，`Layout` 包含 `Sidebar`（左侧导航）和 `RightPanel`（右侧面板）。

### 3.5 Framer Motion 11

用于组件动画：
- `AnimatePresence`：组件进出动画（如资源卡片展开/收起）
- `motion.div`：页面区块的淡入、上滑、缩放入场效果
- `AnimatedSection`：封装的通用动画容器组件

### 3.6 Lucide React

图标库，用于侧边栏导航图标、按钮图标、状态指示等。

---

## 4. 前端目录结构

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── postcss.config.js
└── src/
    ├── main.tsx                    # 入口：BrowserRouter + React.StrictMode
    ├── App.tsx                     # 路由定义（6 个 Route）
    ├── vite-env.d.ts
    ├── types/
    │   └── index.ts                # 全部 TypeScript 类型定义
    ├── config/
    │   ├── appConfig.ts            # 应用配置常量
    │   └── courseFocus.ts          # 数据结构课程集中配置
    ├── services/
    │   ├── api.ts                  # API 请求封装（含 Mock 切换）
    │   ├── profileInterview.ts     # 画像访谈对话逻辑
    │   └── personalizedPath.ts     # 个性化路径构建逻辑
    ├── mock/
    │   ├── profile.ts              # 画像 Mock 数据
    │   ├── courses.ts              # 课程 Mock 数据
    │   ├── resources.ts            # 资源生成 Mock（10 模块 × 4 语言动态生成）
    │   ├── path.ts                 # 学习路径 Mock 数据
    │   └── assessment.ts           # 评估 Mock 数据（关键词驱动）
    ├── utils/
    │   ├── pathUtils.ts            # 学习路径工具函数
    │   └── pathResources.ts        # 路径资源工具函数
    ├── components/
    │   ├── common/
    │   │   └── AnimatedSection.tsx  # 通用动画包装组件
    │   ├── layout/
    │   │   ├── Layout.tsx           # 整体布局（Sidebar + 内容区 + RightPanel）
    │   │   ├── Sidebar.tsx          # 左侧导航栏
    │   │   └── RightPanel.tsx       # 右侧信息面板
    │   ├── profile/
    │   │   ├── ChatPanel.tsx        # 画像访谈聊天面板
    │   │   ├── CodeBuddyAvatar.tsx  # 助手头像组件
    │   │   ├── DiagnosisQuiz.tsx    # 诊断问答组件
    │   │   ├── LearningProfileCard.tsx  # 学习画像卡片
    │   │   └── ProfileDraftPanel.tsx    # 画像草稿面板
    │   ├── courses/
    │   │   ├── CourseCard.tsx       # 课程卡片
    │   │   ├── CourseDetailPanel.tsx # 课程详情面板
    │   │   └── CourseMap.tsx        # 课程地图/路线
    │   ├── resources/
    │   │   ├── ResourceWorkbench.tsx     # 资源生成工作台
    │   │   ├── ResourceCard.tsx          # 资源卡片（支持展开/收起）
    │   │   ├── ResourceDetailPanel.tsx   # 资源详情面板
    │   │   ├── AgentGenerationStatus.tsx # 生成状态指示
    │   │   └── PathResourcePackage.tsx   # 路径资源包管理
    │   ├── path/
    │   │   ├── PathOverview.tsx          # 路径总览
    │   │   ├── PathTimeline.tsx          # 路径时间线
    │   │   ├── PathNodeDetail.tsx        # 路径节点详情
    │   │   ├── PathResourcePanel.tsx     # 路径资源面板
    │   │   └── PathResourceDetailModal.tsx # 路径资源详情弹窗
    │   └── assessment/
    │       ├── ChallengePanel.tsx        # 挑战面板
    │       ├── ChallengeCard.tsx         # 挑战卡片
    │       ├── TutorChatWindow.tsx       # 辅导聊天窗口
    │       ├── SuggestedQuestions.tsx    # 建议问题
    │       └── AssessmentResourceDetailModal.tsx # 评估资源详情弹窗
    └── pages/
        ├── Dashboard.tsx       # 首页仪表盘
        ├── Profile.tsx         # 学习画像页
        ├── CourseCenter.tsx    # 课程中心页
        ├── ResourceGen.tsx     # 资源生成页
        ├── LearningPath.tsx    # 学习路径页
        └── Assessment.tsx      # 智能评估页
```

---

## 5. 后端技术栈

### 5.1 FastAPI

- 基于 ASGI 的 Python Web 框架，使用 Uvicorn 作为服务器
- 自动生成 OpenAPI 文档（`/docs` 端点）
- Router 层负责路由和参数校验，Service 层负责业务逻辑
- 共 7 个 Router 模块，9 个 Service 模块

### 5.2 Pydantic 2.10

- 请求/响应数据模型定义（`schemas/` 目录）
- 类型校验、序列化、默认值填充
- 所有 API 的入参和出参均通过 Pydantic Schema 约束

### 5.3 SQLAlchemy 2.0 + SQLite

- ORM 模式，`Base = declarative_base()` 声明式基类
- SQLite 文件数据库，连接串 `sqlite:///./codemate.db`
- `check_same_thread=False` 适配 FastAPI 异步并发
- 16 个数据模型（`models/` 目录）：
  `User`, `StudentProfile`, `ProfileConversation`, `Course`, `CourseRelation`, `KnowledgePoint`, `KnowledgePointRelation`, `Resource`, `UserResourcePackage`, `LearningPath`, `LearningPathNode`, `PathNodeResource`, `Assessment`, `AssessmentAnswer`, `GrowthRecord`, `Badge`, `UserBadge`, `GrowthValue`

### 5.4 Jinja2 模板引擎

- 用于 LLM Prompt 模板渲染
- 5 个 Prompt 模板文件（`prompts/` 目录）：
  - `chat_profile.txt`：学习画像访谈对话
  - `generate_resources.txt`：学习资源生成
  - `generate_path.txt`：学习路径规划
  - `assess_answer.txt`：答题评估反馈
  - `tutor_response.txt`：辅导对话

---

## 6. 后端目录结构

```
backend/
├── main.py                         # FastAPI 应用入口、CORS 配置、路由注册
├── config.py                       # 配置类（环境变量映射，含 LLM 配置）
├── database.py                     # SQLAlchemy 引擎、会话、Base、init_db()
├── requirements.txt                # Python 依赖
├── .env.example                    # 环境变量示例
├── codemate.db                     # SQLite 数据库文件（运行时生成）
├── models/
│   ├── __init__.py                 # 模型聚合导出（供 init_db 导入）
│   ├── user.py                     # User 模型
│   ├── profile.py                  # StudentProfile, ProfileConversation
│   ├── course.py                   # Course, CourseRelation
│   ├── knowledge.py                # KnowledgePoint, KnowledgePointRelation
│   ├── resource.py                 # Resource, UserResourcePackage
│   ├── path.py                     # LearningPath, LearningPathNode, PathNodeResource
│   ├── assessment.py               # Assessment, AssessmentAnswer
│   └── growth.py                   # GrowthRecord, Badge, UserBadge, GrowthValue
├── schemas/
│   ├── __init__.py                 # Schema 聚合导出
│   ├── user.py, profile.py, course.py, knowledge.py
│   ├── resource.py, learning_path.py, assessment.py, growth.py
├── routers/
│   ├── __init__.py
│   ├── profile.py                  # /api/profile/*
│   ├── courses.py                  # /api/courses/*
│   ├── resources.py                # /api/resources/*
│   ├── path.py                     # /api/path/*
│   ├── assessment.py               # /api/assessment/*
│   └── tutor.py                    # /api/tutor/*
├── services/
│   ├── __init__.py
│   ├── profile_service.py          # 画像业务逻辑（对话、生成、CRUD）
│   ├── course_service.py           # 课程业务逻辑
│   ├── resource_service.py         # 资源生成核心逻辑（生成、后处理、包管理）
│   ├── path_service.py             # 学习路径业务逻辑
│   ├── assessment_service.py       # 评估业务逻辑
│   ├── diagnosis_service.py        # 诊断分析逻辑
│   ├── llm_service.py              # LLM Provider 抽象层（4 种后端）
│   ├── prompt_service.py           # Prompt 模板加载与渲染
│   └── code_service.py             # 代码示例生成服务
├── prompts/
│   ├── chat_profile.txt
│   ├── generate_resources.txt
│   ├── generate_path.txt
│   ├── assess_answer.txt
│   └── tutor_response.txt
├── data/
│   ├── courses.json                # 课程种子数据（10 个数据结构模块）
│   ├── default_profile.json        # 默认画像模板
│   ├── mock_responses.json         # Mock LLM 响应数据
│   └── resource_library/
│       ├── index.json              # 资源库元数据索引
│       └── data_structures/        # 14 个主题子目录，含 Markdown 资源文件
└── scripts/
    ├── __init__.py
    ├── init_db.py                  # 数据库初始化脚本
    ├── seed_db.py                  # 种子数据填充脚本
    ├── check_db.py                 # 数据库检查脚本
    └── validate_resource_library.py # 资源库校验脚本
```

---

## 7. 数据层与资源库

### 7.1 数据库设计

- **引擎**：SQLite 3，通过 SQLAlchemy ORM 操作
- **模型数量**：16 个 SQLAlchemy 模型
- **核心实体**：User → StudentProfile → ProfileConversation（画像链路）、Course → KnowledgePoint（课程体系）、Resource → UserResourcePackage（资源包）、LearningPath → LearningPathNode → PathNodeResource（学习路径）、Assessment → AssessmentAnswer（评估记录）、GrowthRecord → Badge → UserBadge → GrowthValue（成长体系）

### 7.2 资源库（Resource Library）

- **元数据索引**：`data/resource_library/index.json` 包含所有资源的元信息，关键字段包括 `id`、`title`、`topic`、`topicCode`、`type`、`resource_type`、`module`、`difficulty`、`language`、`tags`、`summary`、`contentPath`、`path`
- **存储结构**：`data_structures/` 下 14 个主题子目录，每个目录内存放 Markdown 格式的资源文件（讲解文档、图解说明、代码示例、易错点分析、练习题集、项目案例等）
- **主题覆盖**：二叉树遍历、递归调用栈、BFS 和 DFS 图遍历、快速排序与排序稳定性、二分查找边界、动态规划入门、散列表与哈希冲突、栈与队列应用、线性表与链表、复杂度分析、排序算法综合、树结构综合、图算法综合、综合项目实践
- **资源类型**：图解讲解、代码示例、易错点、分层练习、项目案例
- **检索方式**：资源生成时通过 `_search_library()` 根据 topic、module 和 tags 进行匹配，检索结果作为 generation_context 的一部分注入 LLM prompt 或 fallback 生成逻辑

### 7.3 Mock 数据体系

- `mock_responses.json`：后端 MockProvider 的预设响应数据
- 前端 `src/mock/`：5 个 Mock 模块分别覆盖画像、课程、资源、路径、评估全链路
- 通过 `VITE_USE_MOCK` 环境变量控制开关

---

## 8. LLM 技术栈

### 8.1 Provider 抽象层

`services/llm_service.py` 定义统一的 LLM 调用接口：

```
LLMProvider (ABC)
├── MockProvider        — 返回 mock_responses.json 预设数据
├── OpenAIProvider      — OpenAI 兼容 API（含 DeepSeek）
├── AnthropicProvider   — Anthropic Messages API
└── DeepSeekProvider    — DeepSeek API（OpenAI 兼容，继承 OpenAIProvider）
```

- **工厂函数** `get_llm()` 根据环境变量 `LLM_PROVIDER` 选择后端
- **懒加载**：SDK 在首次 `chat()` 调用时才导入，Mock 模式下不触发任何外部 SDK
- **自动降级**：API Key 缺失时自动回退到 MockProvider
- **重试机制**：可配置 `LLM_MAX_RETRIES`，默认包含重试逻辑

### 8.2 支持的 LLM 后端

| Provider | 环境变量 | 模型配置 |
|----------|---------|---------|
| OpenAI | `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` | 通过 `openai.OpenAI` SDK |
| Anthropic | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | 通过 `anthropic.Anthropic` SDK |
| DeepSeek | `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL` | OpenAI 兼容协议 |
| Mock | 无需配置 | 本地 JSON 文件 |

### 8.3 Prompt 管理

- 模板引擎：Jinja2
- 模板变量：课程信息、资源类型、学习画像、编程语言、知识点
- 输出格式：严格要求 JSON，附带 `safe_parse_json()` 三层解析策略（直接解析 → 代码块提取 → 括号配对提取）

---

## 9. 资源生成流程

资源生成是系统的核心业务流程，采用"资源库检索 + 用户画像融合 + LLM/mock 生成 + 动态 fallback + 后端结构化校验"的混合式机制。完整链路如下：

```
用户输入
  ├── course_id（课程）
  ├── learning_topic（学习主题）
  ├── resource_types（资源类型：图解讲解/代码示例/易错点/分层练习/项目案例）
  ├── language（编程语言：C/C++/Java/Python）
  └── quick_profile（快速画像：基础水平/学习目标/困难/偏好）

          ▼
┌─────────────────────────────────────────┐
│  Router: resources.py                   │
│  参数校验、字段兼容、默认值填充             │
└─────────────────────────────────────────┘
          ▼
┌─────────────────────────────────────────┐
│  Service: resource_service.py           │
│  1. 主题识别 → topic_key + module       │
│  2. 画像读取（学习目标/基础/困难/偏好）    │
│  3. 查询 resource_library 匹配资源       │
│  4. 构建 generation_context             │
│  5. 调用 prompt_service 渲染 Prompt      │
│  6. 调用 llm_service.chat_json()        │
│  7. LLM 失败 → 动态 fallback 兜底        │
│  8. finalize_resource_cards() 后处理     │
│     ├─ resource_types 严格过滤           │
│     ├─ 代码语言一致性校验与修正           │
│     ├─ 主题相关性检查（防交叉污染）        │
│     ├─ 内容厚度与质量校验                 │
│     ├─ 占位符/模板残留检测               │
│     ├─ 重点主题专用模板兜底               │
│     └─ 个性化描述注入                    │
│  9. 构建完整响应（含 verification 字段）   │
└─────────────────────────────────────────┘
          ▼
┌─────────────────────────────────────────┐
│  LLM Provider                           │
│  Mock: _build_full_fallback_cards()     │
│        动态生成（10 模块 × 5 类型 ×       │
│        4 语言 × 画像感知）                 │
│  Real: DeepSeek / OpenAI / Anthropic    │
└─────────────────────────────────────────┘
          ▼
      ResourceGenerateResponse
      {
        resource_cards: ResourceCard[],
        normalized_module: string,
        resource_types_used: string[],
        programming_language_used: string,
        personalization_source: string,
        personalization_summary: {...},
        generation_signature: string
      }
```

---

## 10. 结构化资源卡片

### 10.1 ResourceCard 数据结构

每个生成的资源卡片包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 卡片唯一标识 |
| `title` | string | 资源标题 |
| `type` | string | 资源类型 |
| `course` | string | 所属课程 |
| `knowledge_point` | string | 知识点 |
| `difficulty` | string | 难度等级 |
| `language` | string | 编程语言 |
| `summary` | string | 摘要简介 |
| `sections` | ResourceSection[] | 结构化内容片段 |
| `key_concepts` | string[] | 核心概念 |
| `learning_tips` | string[] | 学习建议 |
| `estimated_time` | string | 预计用时 |
| `personalized_reason` | string | 个性化推荐理由 |

### 10.2 Section 类型体系

`SectionKind` 共 10 种类型：

| Kind | 用途 | 渲染方式 |
|------|------|----------|
| `highlight` | 重点高亮 | 带图标色块 |
| `steps` | 步骤说明 | 编号列表 |
| `code` | 代码示例 | 语法高亮代码块 |
| `warning` | 易错点 | 警告色块 |
| `practice` | 练习题 | 练习卡片 |
| `compare` | 对比表格 | 双栏对比 |
| `task` | 任务描述 | 任务卡片 |
| `next_action` | 下一步建议 | 行动提示 |
| `text` | 普通文本 | 段落文本 |
| `divider` | 分隔线 | 水平分割 |

### 10.3 资源类型

5 种标准类型，每种有对应的内容生成模板：图解讲解、代码示例、易错点分析、分层练习、项目案例。

---

## 11. API 通信机制

### 11.1 请求封装

前端 `services/api.ts` 封装统一的请求函数：

```typescript
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`)
  return res.json()
}
```

### 11.2 Mock 切换机制

```typescript
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'
```

每个 API 函数首先检查 `USE_MOCK`，为 true 时返回前端 Mock 数据，为 false 时发起真实 HTTP 请求。默认开启 Mock，设置 `VITE_USE_MOCK=false` 则切换到真实后端。

### 11.3 API 端点清单

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/profile/chat` | 画像访谈对话 |
| POST | `/api/profile/generate` | 生成学习画像 |
| GET | `/api/profile/{user_id}` | 获取用户画像 |
| PUT | `/api/profile/{user_id}` | 更新用户画像 |
| GET | `/api/profile/{user_id}/conversations` | 获取对话历史 |
| POST | `/api/profile/{user_id}/conversations` | 追加对话记录 |
| GET | `/api/courses` | 课程列表 |
| GET | `/api/courses/{course_id}` | 课程详情 |
| POST | `/api/resources/generate` | 生成学习资源 |
| POST | `/api/resources/packages` | 保存资源到包 |
| GET | `/api/resources/packages/{user_id}` | 获取用户资源包 |
| DELETE | `/api/resources/packages/{package_id}` | 删除资源包项 |
| POST | `/api/path/generate` | 生成学习路径 |
| GET | `/api/assessment/questions` | 获取评估题目 |
| POST | `/api/assessment/submit` | 提交评估答案 |
| POST | `/api/tutor/chat` | 辅导对话 |

---

## 12. 环境变量配置

### 12.1 前端环境变量（`.env`）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `VITE_USE_MOCK` | 是否使用 Mock 模式 | `true` |
| `VITE_API_BASE_URL` | API 基础路径 | `/api` |

### 12.2 后端环境变量（`.env`）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_PROVIDER` | LLM 后端选择 | `mock` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | — |
| `OPENAI_BASE_URL` | OpenAI API 地址 | — |
| `OPENAI_MODEL` | OpenAI 模型名 | `gpt-4o` |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | — |
| `ANTHROPIC_MODEL` | Anthropic 模型名 | `claude-opus-4-7` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | — |
| `DEEPSEEK_BASE_URL` | DeepSeek API 地址 | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | DeepSeek 模型名 | `deepseek-chat` |
| `LLM_MAX_RETRIES` | LLM 请求最大重试次数 | `2` |
| `LLM_REQUEST_TIMEOUT` | LLM 请求超时（秒） | `60` |
| `DATABASE_URL` | 数据库连接串 | `sqlite:///./codemate.db` |
| `CORS_ORIGINS` | CORS 允许来源 | `http://localhost:5173` |

---

## 13. 开发与构建命令

### 13.1 前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器（端口 5173，含 HMR）
npm run dev

# TypeScript 类型检查
npx tsc -b

# 生产构建（tsc + vite build）
npm run build

# 预览生产构建
npm run preview
```

### 13.2 后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python scripts/init_db.py

# 填充种子数据
python scripts/seed_db.py

# 验证资源库
python scripts/validate_resource_library.py

# 启动后端服务（端口 8000）
uvicorn main:app --reload --port 8000
```

### 13.3 全栈开发流程

1. 启动后端：`cd backend && uvicorn main:app --reload --port 8000`
2. 启动前端：`cd frontend && npm run dev`
3. 前端自动将 `/api` 请求代理到后端 8000 端口
4. 默认使用 Mock 模式（前后端均可独立运行）
5. 切换到真实 LLM：在后端 `.env` 中配置 `LLM_PROVIDER` 和对应的 API Key

---

## 14. 技术协同关系

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│  React 18   │     │  FastAPI    │     │  LLM Provider   │
│  (UI 层)    │ ←→  │  (API 层)   │ ←→  │  (AI 推理层)     │
└─────────────┘     └─────────────┘     └─────────────────┘
       │                   │                      │
       ▼                   ▼                      ▼
  TypeScript          Pydantic              Jinja2
  (类型安全)           (数据校验)             (Prompt 模板)
       │                   │                      │
       ▼                   ▼                      ▼
  Tailwind CSS        SQLAlchemy            OpenAI SDK /
  (样式系统)           (ORM 层)              Anthropic SDK
                           │
                           ▼
                       SQLite
                       (持久化)
```

- **类型一致性**：前端 TypeScript 类型与后端 Pydantic Schema 一一对应，通过 JSON 序列化/反序列化自动映射
- **Mock 对称**：前后端各有一套 Mock 体系，可独立运行和调试
- **LLM 抽象**：通过 Provider 接口统一 4 种 LLM 后端的调用方式，业务代码无感知
- **Prompt 管理**：Jinja2 模板 + `prompt_service` 将 Prompt 与业务逻辑解耦

---

## 15. 总结

CodeMate 的技术选型遵循以下原则：

- **类型安全**：前端 TypeScript 严格模式 + 后端 Pydantic 强校验，消除运行时类型错误
- **渐进增强**：Mock 模式保证前后端可独立开发，真实 LLM 按需接入
- **关注分离**：Router → Service → Provider 三层解耦，每层职责明确
- **轻量部署**：SQLite 免安装数据库，Vite 零配置构建，降低环境搭建成本
- **可扩展性**：LLM Provider 工厂模式支持快速接入新的大模型后端，资源库目录结构支持按主题扩展内容

---

*本文档基于 CodeMate 项目实际代码文件生成，技术栈信息均源自 `package.json`、`requirements.txt`、`config.py`、`database.py`、`llm_service.py`、`vite.config.ts`、`tailwind.config.js` 等核心配置文件。*
