# ChatMind - 聊天分析与回复助手

基于 AI 的聊天记录分析与智能回复生成工具，支持粘贴聊天记录、分析对话内容并生成智能回复。

## 技术栈

**后端**: Python 3.11 · FastAPI · SQLAlchemy 2.0 · LangChain + DeepSeek · JWT 认证

**前端**: React 19 · TypeScript · Vite · Tailwind CSS · Recharts

## 项目结构

```
chatmind/
├── backend/
│   └── app/
│       ├── main.py        # FastAPI 入口，挂载前端静态文件
│       ├── config.py      # 配置项（读取 .env）
│       ├── database.py    # 数据库初始化
│       ├── api/           # 路由：auth / user / records / analysis / reply
│       ├── models/        # SQLAlchemy 模型
│       ├── schemas/       # Pydantic 模式
│       └── services/      # 业务逻辑
├── frontend/
│   └── src/
│       ├── pages/         # 页面组件
│       ├── components/    # 通用组件
│       └── context/       # React Context
├── Dockerfile
└── zeabur.json
```

## 环境变量

在 `backend/` 目录下创建 `.env` 文件：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key   # 必填
JWT_SECRET_KEY=change-this-in-production  # 生产环境必须修改
DATABASE_URL=sqlite+aiosqlite:///./chatmind.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
PORT=8000
```

## 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端（新终端）
cd frontend
npm install
npm run dev   # http://localhost:5173
```

## Docker 部署

```bash
docker build -t chatmind .
docker run -p 8000:8000 -e DEEPSEEK_API_KEY=your_key chatmind
```

访问 `http://localhost:8000`

## Zeabur 部署

项目已配置 `zeabur.json`，直接连接仓库即可一键部署，需在 Zeabur 控制台设置 `DEEPSEEK_API_KEY` 环境变量。

## API 接口

| 路径 | 说明 |
|------|------|
| `POST /api/auth/register` | 注册 |
| `POST /api/auth/login` | 登录，返回 JWT |
| `GET /api/records` | 获取聊天记录列表 |
| `POST /api/records` | 上传聊天记录 |
| `POST /api/analysis` | AI 分析聊天记录 |
| `POST /api/reply` | AI 生成回复建议 |
| `GET /api/health` | 健康检查 |
