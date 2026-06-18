# CodeMate 智学工坊

面向计算机专业课程群的个性化学习资源与学习路径规划智能体平台。

通过自然语言对话构建六维学习画像，生成个性化学习资源，规划 5 阶段学习路径，提供关键词感知的智能辅导与闯关评估。

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | React 18 + TypeScript + Tailwind CSS + Vite |
| 路由 | React Router v6 |
| 动画 | Framer Motion |
| 图标 | Lucide React |
| 后端 | Python FastAPI |
| 数据库 | SQLite（启动时自动建表） |
| LLM | 统一 Provider 接口，支持 mock / openai / anthropic |

## 项目目录结构

```
codemate-workshop/
├── README.md
├── .env.example                  # 根目录环境变量示例
├── start.sh                      # Linux/WSL/macOS 一键启动脚本
├── frontend/
│   ├── src/
│   │   ├── components/           # 可复用组件
│   │   │   ├── common/           # AnimatedSection 等通用组件
│   │   │   ├── layout/           # Sidebar, Layout, RightPanel
│   │   │   ├── assessment/       # 辅导评估组件
│   │   │   ├── courses/          # 课程卡片、详情、课程地图
│   │   │   ├── path/             # 路径时间轴、节点详情、资源面板
│   │   │   ├── profile/          # 画像对话、草稿、诊断题、画像卡片
│   │   │   └── resources/        # 资源工作台、资源卡片、资源包
│   │   ├── pages/                # 6 个页面路由
│   │   ├── services/             # API 调用层 + Mock 回退
│   │   ├── mock/                 # 前端 Mock 数据
│   │   ├── utils/                # 工具函数（localStorage 读写等）
│   │   ├── config/               # 应用配置
│   │   └── types/                # TypeScript 类型定义
│   ├── .env.example
│   ├── vite.config.ts
│   └── package.json
├── backend/
│   ├── main.py                   # FastAPI 入口，startup 自动 init_db
│   ├── config.py                 # 配置管理（读取环境变量）
│   ├── database.py               # SQLite 连接 + init_db()
│   ├── models/                   # SQLAlchemy 数据模型
│   ├── schemas/                  # Pydantic 请求/响应模型
│   ├── routers/                  # API 路由（6 模块）
│   ├── services/                 # 业务逻辑 + LLM 集成（7 模块）
│   ├── prompts/                  # LLM prompt 模板
│   ├── data/
│   │   └── resource_library/     # 本地课程资源库
│   ├── scripts/                  # 数据库初始化/种子/校验脚本
│   ├── .env.example
│   └── requirements.txt
└── docs/
    ├── database_schema.md        # 数据库设计文档
    └── resource_library_spec.md  # 资源库规范文档
```

## 环境准备

### 前端

- **Node.js** >= 18
- **npm** >= 9

```bash
cd frontend
cp .env.example .env    # 根据需要编辑 VITE_USE_MOCK
npm install
```

### 后端

- **Python** >= 3.10
- **pip**

```bash
cd backend
cp .env.example .env    # 根据需要编辑 LLM_PROVIDER
pip install -r requirements.txt
```

## 启动方式

### 方式一：前端 Mock 模式（无需后端）

适合比赛演示、离线开发、UI 调试。前端使用内置 Mock 数据，不发起任何网络请求。

```powershell
# PowerShell
cd frontend
$env:VITE_USE_MOCK="true"
npm run dev
```

访问 http://localhost:5173 即可浏览全部 6 个页面。

### 方式二：前后端联调

同时启动后端和前端，后端使用 Mock LLM Provider（无需 API Key）。

**1. 启动后端（PowerShell）：**

```powershell
cd backend
$env:LLM_PROVIDER="mock"
uvicorn main:app --reload --port 8000
```

**2. 启动前端（PowerShell）：**

```powershell
cd frontend
$env:VITE_USE_MOCK="false"
$env:VITE_API_BASE_URL="http://127.0.0.1:8000/api"
npm run dev
```

前端 Vite 开发服务器默认在 5173 端口启动，并配置了代理将 `/api` 请求转发到 `http://localhost:8000`。设置了 `VITE_API_BASE_URL` 后直连后端，不经过 Vite 代理。

**3. 生产构建：**

```bash
cd frontend
npm run build        # 产物在 dist/，需配合后端静态文件服务使用
```

### 方式三：一键启动脚本（Linux / WSL / macOS）

```bash
chmod +x start.sh
./start.sh           # 自动安装依赖并启动后端 + 前端
```

### 访问地址

| 路由 | 页面 | 说明 |
|------|------|------|
| `/` | 首页 Dashboard | 课程群概览、系统流程、多智能体展示 |
| `/profile` | 学习画像 | CodeBuddy 对话 + 六维画像卡片 |
| `/courses` | 课程中心 | 6 门课程卡片 + 课程详情 + 先修/关联关系 |
| `/resources` | 资源生成 | 资源生成工作台 + 6 类资源卡片 + 资源包管理 |
| `/path` | 学习路径 | 5 阶段学习路径时间轴 + 节点详情 + 资源匹配 |
| `/assessment` | 辅导评估 | 智能辅导对话 + 上下文闯关题 + 学习评估 |

## Demo Mode 与 Real Mode

### Mock 模式（演示 / 开发模式）

- **无需 API Key**，无需启动后端即可运行前端
- 前端 `VITE_USE_MOCK=true`：前端使用 `src/mock/` 下的本地 Mock 数据
- 后端 `LLM_PROVIDER=mock`：后端各 service 返回预定义的规则化数据
- 画像对话、资源生成、学习路径、辅导评估均可完整走通
- Mock 回复基于关键词规则匹配，覆盖面有限，不如真实 LLM 自然
- 正常用户流程不默认显示演示学生数据，所有 student 字段使用中性占位值

### Real Mode（生产模式）

- 需要配置 LLM API Key（OpenAI 或 Anthropic）
- 前端 `VITE_USE_MOCK=false`，直连后端 API
- 后端 `LLM_PROVIDER=openai` 或 `LLM_PROVIDER=anthropic`
- 画像对话、资源生成等场景将调用真实 LLM，回复更自然、覆盖面更广
- 资源生成优先基于本地资源库，LLM 负责组织改写和个性化

## LLM 配置

后端通过 `config.py` 读取以下环境变量（可在 `backend/.env` 中设置）：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_PROVIDER` | LLM 提供商：`mock` / `openai` / `anthropic` | `mock` |
| `OPENAI_API_KEY` | OpenAI API Key（provider=openai 时必填） | — |
| `OPENAI_MODEL` | OpenAI 模型名 | `gpt-4o-mini` |
| `OPENAI_BASE_URL` | OpenAI 自定义 Base URL（可选，用于代理或兼容 API） | — |
| `ANTHROPIC_API_KEY` | Anthropic API Key（provider=anthropic 时必填） | — |
| `ANTHROPIC_MODEL` | Anthropic 模型名 | `claude-haiku-4-5-20251001` |
| `LLM_MAX_RETRIES` | LLM 请求最大重试次数 | `2` |
| `LLM_REQUEST_TIMEOUT` | LLM 请求超时秒数 | `60` |

**快速配置示例（OpenAI）：**

```powershell
# backend/.env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

## 数据库说明

### 自动建表

后端启动时自动执行 `init_db()`，创建所有表（通过 SQLAlchemy `Base.metadata.create_all`）。无需手动运行建表脚本。

### 手动初始化

如需手动管理数据库，可使用以下脚本：

```bash
cd backend
python -m scripts.init_db      # 手动建表
python -m scripts.seed_db      # 填充种子数据（演示用户、课程、徽章等）
python -m scripts.check_db     # 检查数据库状态
```

### 数据库文件

SQLite 数据库文件默认路径：`backend/codemate.db`。

### 重置数据库

```bash
cd backend
rm codemate.db                  # 删除数据库文件
# 重新启动后端，自动重建空表
uvicorn main:app --reload --port 8000
```

在 Windows PowerShell 中：

```powershell
cd backend
Remove-Item codemate.db
```

### 数据库表结构

| 表名 | 说明 |
|------|------|
| `users` | 用户表 |
| `student_profiles` | 学生画像表（知识基础分、实践能力分、认知风格等） |
| `profile_conversations` | 画像对话记录表 |
| `courses` | 课程表 |
| `course_relations` | 课程先修/关联关系表 |
| `knowledge_points` | 知识点表 |
| `knowledge_point_relations` | 知识点前后置关系表 |
| `resources` | 学习资源表 |
| `user_resource_packages` | 用户资源包表 |
| `learning_paths` | 学习路径表 |
| `learning_path_nodes` | 学习路径节点表 |
| `path_node_resources` | 路径节点关联资源表 |
| `assessments` | 评估表 |
| `assessment_answers` | 评估答题记录表 |
| `growth_records` | 成长记录表 |
| `growth_values` | 成长值表 |
| `badges` | 徽章表 |
| `user_badges` | 用户徽章表 |

详细设计见 [`docs/database_schema.md`](docs/database_schema.md)。

## 资源库说明

### 本地资源库结构

资源库位于 `backend/data/resource_library/`，包含 2 门课程、9 个知识主题的 20+ 份学习资源：

```
backend/data/resource_library/
├── index.json                    # 资源元数据索引
├── programming_basics/           # 程序设计基础
│   ├── function_call/            # 函数调用
│   ├── arrays/                   # 数组边界
│   ├── recursion/                # 递归调用栈
│   └── debugging/                # 基础调试
└── data_structures/              # 数据结构与算法
    ├── binary_tree_traversal/    # 二叉树遍历
    ├── binary_tree_structure/    # 二叉树结构
    ├── recursion_thinking/       # 递归思想
    └── sorting/                  # 排序算法
```

### 资源类型

每类资源均为 Markdown 或 JSON 格式的本地文件：

- 个性化讲解文档（`.md`）
- 知识点思维导图（`.md`）
- 代码示例与注释（`.md`）
- 分层练习题（`.json`）
- 项目式学习案例（`.md`）
- 拓展阅读资料（`.md`）

### 索引文件

`index.json` 包含所有资源的元数据（id、标题、课程、知识点、类型、难度、标签、内容路径等），后端 `resource_service` 通过读取该索引文件检索和匹配资源。

### 资源生成原则

- 资源生成优先基于本地资源库内容
- LLM 只负责组织、改写和个性化，不应编造资源来源
- `index.json` 中的 `contentPath` 字段指向实际可读取的 Markdown 或 JSON 文件

详细规范见 [`docs/resource_library_spec.md`](docs/resource_library_spec.md)。

## API 接口

### Profile（画像）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/profile/chat` | 画像多轮对话 |
| `POST` | `/api/profile/generate` | 生成完整六维画像 |
| `GET` | `/api/profile/{user_id}` | 获取用户画像 |
| `PUT` | `/api/profile/{user_id}` | 更新用户画像 |
| `GET` | `/api/profile/{user_id}/conversations` | 获取对话历史 |
| `POST` | `/api/profile/{user_id}/conversations` | 添加对话记录 |

### Courses（课程）

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/courses` | 课程列表 |
| `GET` | `/api/courses/{course_code}` | 课程详情 |

### Knowledge Points（知识点）

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/knowledge-points` | 知识点列表 |
| `GET` | `/api/knowledge-points/{kp_id}` | 知识点详情 |

### Resources（资源）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/resources/generate` | 生成个性化资源 |
| `GET` | `/api/resources/library` | 资源库列表 |
| `GET` | `/api/resources/library/stats` | 资源库统计 |
| `GET` | `/api/resources/library/{resource_id}` | 资源库资源详情 |
| `GET` | `/api/resources/packages/{user_id}` | 获取用户资源包 |
| `POST` | `/api/resources/packages` | 添加资源到资源包 |
| `PUT` | `/api/resources/packages/{package_id}` | 更新资源包项 |
| `DELETE` | `/api/resources/packages/{package_id}` | 删除资源包项 |

### Path（学习路径）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/path/generate` | 生成个性化学习路径 |
| `GET` | `/api/paths/{user_id}` | 获取用户学习路径列表 |
| `POST` | `/api/paths` | 创建学习路径 |
| `GET` | `/api/paths/{path_id}` | 获取路径详情 |
| `PUT` | `/api/paths/{path_id}` | 更新学习路径 |
| `POST` | `/api/paths/{path_id}/nodes` | 添加路径节点 |
| `PUT` | `/api/paths/nodes/{node_id}` | 更新路径节点状态 |
| `POST` | `/api/paths/nodes/{node_id}/resources` | 关联资源到节点 |

### Tutor & Assessment（辅导与评估）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/tutor/chat` | 智能辅导对话 |
| `GET` | `/api/assessment/questions` | 获取诊断题 |
| `POST` | `/api/assessment/submit` | 提交评估答案 |
| `POST` | `/api/assessment/records` | 保存评估记录 |
| `GET` | `/api/assessment/growth/{user_id}` | 获取成长值记录 |

### 通用

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/health` | 健康检查（含 LLM Provider 状态） |

## 完整手动验收流程

按以下步骤验证系统核心流程可走通：

1. **画像页** — 打开 http://localhost:5173/profile ，在聊天框输入学习情况（如 "我在学数据结构和C语言，递归和指针不太懂"），完成多轮对话，进入诊断题，提交后生成学习画像
2. **课程中心** — 打开 http://localhost:5173/courses ，查看 6 门课程卡片。如果已完成画像，页面顶部会显示基于画像的课程推荐。点击课程查看详情
3. **资源生成** — 打开 http://localhost:5173/resources ，配置课程、学习主题、难度和语言，点击生成，查看生成的资源卡片
4. **资源包** — 对任意资源卡片点击"加入资源包"，在右侧资源包面板确认资源已添加
5. **学习路径** — 打开 http://localhost:5173/path ，查看 5 阶段学习路径时间轴。如已完成画像，显示个性化路径；否则显示通用参考路径。右侧可查看节点详情、匹配资源
6. **辅导评估** — 打开 http://localhost:5173/assessment ，输入问题（如 "递归和迭代有什么区别"），查看 CodeBuddy 的分步讲解和推荐资源。闯关题会根据提问内容动态生成
7. **检查 Console** — 打开浏览器开发者工具 Console，确认无红色错误（`F12` → Console 标签）

## 常见问题 FAQ

### 后端 8000 端口被占用怎么办

```powershell
# 查找占用端口的进程
netstat -ano | findstr :8000
# 终止该进程（替换 PID）
taskkill /PID <PID> /F
```

或者更换端口启动：

```powershell
uvicorn main:app --reload --port 8001
```

如果更换后端端口，需要同步更新前端的 `VITE_API_BASE_URL`。

### 前端端口不是 5173 怎么办

Vite 默认使用 5173，如被占用会自动尝试下一个端口（5174 等）。也可以指定端口：

```powershell
npm run dev -- --port 3000
```

### API 请求失败怎么办

1. 确认后端已启动：访问 http://localhost:8000/api/health 应返回 JSON
2. 确认前端环境变量：`VITE_USE_MOCK=false` 且 `VITE_API_BASE_URL` 指向正确的后端地址
3. 检查浏览器 Console（F12）中的具体错误信息
4. 如果后端报 CORS 错误，检查 `CORS_ORIGINS` 环境变量是否包含前端地址
5. 如仍无法解决，可以使用 Mock 模式（`VITE_USE_MOCK=true`）先独立运行前端

### 没有 API Key 能不能运行

**可以。** Mock 模式下系统完全可用：

- 前端 `VITE_USE_MOCK=true`：独立运行，无需后端
- 后端 `LLM_PROVIDER=mock`：使用内置规则化数据，无需任何 LLM API Key
- 画像对话、资源生成、学习路径、辅导评估 4 大流程均可完整走通

### 为什么 Mock 模式回复不够智能

Mock 模式基于关键词规则匹配，回复内容是预定义的模板。它适合：

- 验证功能流程是否走通
- UI 开发和调试
- 离线演示

如需更自然、覆盖面更广的回复，请配置 `LLM_PROVIDER=openai` 或 `LLM_PROVIDER=anthropic` 并填入有效的 API Key。

### 页面出现旧数据怎么办

1. 画像/路径数据部分存储在浏览器 localStorage 中。清除方法：打开 DevTools（F12）→ Application → Local Storage → 清除对应项
2. 资源包数据由后端 API 管理，重启后端后数据不丢失（SQLite 持久化）。如需清除：删除 `backend/codemate.db` 后重启
3. 前端 Mock 模式下所有数据来自内存，刷新页面即重置

### Windows PowerShell 如何设置环境变量

**临时设置（仅当前会话）：**

```powershell
$env:LLM_PROVIDER="mock"
$env:VITE_USE_MOCK="true"
```

**永久设置：**

```powershell
[Environment]::SetEnvironmentVariable("LLM_PROVIDER", "mock", "User")
```

**推荐方式：** 在项目目录下创建 `.env` 文件（从 `.env.example` 复制），`python-dotenv` 和 Vite 会自动加载。

### 前端 package.json 中的脚本有哪些

| 命令 | 说明 |
|------|------|
| `npm run dev` | 启动 Vite 开发服务器（热更新） |
| `npm run build` | TypeScript 类型检查 + Vite 生产构建 |
| `npm run preview` | 预览生产构建产物 |
