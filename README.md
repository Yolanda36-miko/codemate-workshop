# CodeMate 智学工坊

面向计算机科学与技术专业课程群的个性化学习资源生成与学习路径规划智能体系统。

通过 Q 版数字人 **CodeBuddy** 的多轮自然语言对话，构建六维学习画像，生成个性化学习资源，规划学习路径，并提供辅导评估。

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | React 18 + TypeScript + Tailwind CSS + Vite |
| 路由 | React Router v6 |
| 动画 | Framer Motion |
| 图标 | Lucide React |
| 后端 | Python FastAPI |
| 数据库 | SQLite |
| LLM | 统一 Provider 接口，默认 Mock 模式 |

## 快速启动

### 前提条件

- Node.js >= 18
- Python >= 3.10（仅联调模式需要）
- pip（仅联调模式需要）

### 方式一：前端 Mock 独立演示（推荐用于比赛演示）

无需启动后端，前端使用内置 Mock 数据独立运行，保证演示稳定。

```bash
cd frontend
cp .env.example .env        # 默认 VITE_USE_MOCK=true
npm install
npm run dev
```

访问 http://localhost:5173 即可浏览全部 6 个页面。

### 方式二：前后端联调

同时启动后端和前端，前端通过 Vite 代理调用后端 API。

**1. 启动后端：**

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**2. 配置前端环境变量：**

```bash
cd frontend
cp .env.example .env
# 编辑 .env，设置 VITE_USE_MOCK=false
```

**3. 启动前端：**

```bash
cd frontend
npm install
npm run dev          # Vite 自动将 /api 请求代理到 localhost:8000
```

或者构建生产版本：

```bash
npm run build        # 产物在 dist/，需配合后端静态文件服务使用
```

### 一键启动 (Linux / WSL / macOS)

```bash
chmod +x start.sh
./start.sh           # 自动启动后端 + 前端（Mock 模式需手动改 .env）
```

### Mock 模式说明

Mock 模式通过环境变量 `VITE_USE_MOCK` 控制。在 `frontend/.env` 中设置：

- `VITE_USE_MOCK=true`（默认）：前端使用 `src/mock/` 目录下的本地 Mock 数据，**不发起任何网络请求**，无需后端。适合比赛演示、离线开发和 UI 调试。
- `VITE_USE_MOCK=false`：前端通过 Vite 代理（`/api` → `http://localhost:8000`）调用后端 API。后端 7 个 service 模块在 `LLM_PROVIDER=mock` 时同样返回预定义数据，无需配置任何 LLM API Key。

两种模式的数据内容完全一致（都是李同学的默认画像、6 门课程、示例资源等），区别仅在前端读取来源。

## 项目结构

```
codemate-workshop/
├── README.md
├── .env.example
├── start.sh
├── frontend/
│   ├── src/
│   │   ├── components/layout/   # Sidebar, Layout
│   │   ├── pages/               # 6 个页面
│   │   ├── services/api.ts      # API 调用 + Mock 回退
│   │   ├── mock/                # 前端 Mock 数据
│   │   └── types/               # TypeScript 类型
│   └── ...
├── backend/
│   ├── main.py                  # FastAPI 入口
│   ├── config.py                # 配置
│   ├── database.py              # SQLite
│   ├── routers/                 # API 路由 (6 模块)
│   ├── services/                # 智能体服务 (7 模块)
│   └── data/                    # JSON 知识库 + Mock 数据
└── docs/
    └── CodeMate_智学工坊_Claude_Code开发说明Prompt.txt
```

## 页面

| 路由 | 页面 | 说明 |
|------|------|------|
| `/` | 首页 Dashboard | 课程群概览、系统流程、多智能体展示、演示场景 |
| `/profile` | 学习画像 | CodeBuddy 对话区 + 六维画像卡片 |
| `/courses` | 课程中心 | 6 门课程卡片 + 课程详情 + 先修/关联关系 |
| `/resources` | 资源生成 | 资源生成工作台 + 6 类资源卡片 |
| `/path` | 学习路径 | 7 节点时间轴学习路径 |
| `/assessment` | 辅导评估 | 辅导问答 + 诊断题 + 成长反馈 |

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| POST | `/api/profile/chat` | 画像多轮对话 |
| POST | `/api/profile/generate` | 生成完整画像 |
| GET | `/api/courses` | 课程列表 |
| GET | `/api/courses/{id}` | 课程详情 |
| POST | `/api/resources/generate` | 生成资源 |
| POST | `/api/path/generate` | 生成学习路径 |
| POST | `/api/tutor/chat` | 辅导问答 |
| GET | `/api/assessment/questions` | 获取诊断题 |
| POST | `/api/assessment/submit` | 提交评估 |

## 开发阶段

- [x] 阶段 1：项目骨架搭建（左侧导航 + 6 页面路由 + Mock 数据联通）
- [x] 阶段 2：数据库与数据模型建设（SQLAlchemy 模型、Pydantic schemas、种子数据）
- [ ] 阶段 3：首页与整体 UI 风格
- [ ] 阶段 4：CodeBuddy 学习画像页
- [ ] 阶段 5：课程中心页
- [ ] 阶段 6：资源生成页
- [ ] 阶段 7：学习路径页
- [ ] 阶段 8：辅导评估页与演示优化

## 数据库

### 数据库初始化

Phase 2 已完成数据库基础建设，包括 SQLAlchemy 数据模型、Pydantic schemas 和种子数据。

**1. 初始化数据库表：**

```bash
cd backend
python -m scripts.init_db
```

**2. 填充种子数据：**

```bash
cd backend
python -m scripts.seed_db
```

种子数据包括：
- 5 门课程（Python 编程基础、数据结构与算法、Web 开发入门、数据库原理与应用、面向对象程序设计）
- 10 个知识点（每门课程 2-3 个核心知识点）
- 8 个徽章（初学者、进阶学习者、学习大师、勤奋学习者等）
- 演示用户（demo_user, local_user）
- 学生画像和成长值记录

**3. 检查数据库状态：**

```bash
cd backend
python -m scripts.check_db
```

**4. 数据库文档：**

详细数据库设计文档见 [`docs/database_schema.md`](docs/database_schema.md)

### 数据库表结构

当前系统包含以下核心表：

| 表名 | 说明 |
|------|------|
| users | 用户表 |
| student_profiles | 学生画像表 |
| courses | 课程表 |
| knowledge_points | 知识点表 |
| resources | 学习资源表 |
| resource_packages | 资源包表 |
| learning_paths | 学习路径表 |
| path_nodes | 学习路径节点表 |
| assessments | 评估表 |
| assessment_records | 评估记录表 |
| growth_values | 成长值表 |
| badges | 徽章表 |
| user_badges | 用户徽章表 |

### 开发分支

- **基础分支**: `real-system-upgrade`
- **数据库工作分支**: `phase2-database-schema`
