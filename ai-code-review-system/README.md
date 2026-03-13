# AI Code Review System

## Project Structure

```
ai-code-review-system/
├── backend/                 # Python Flask 后端
│   ├── api/                # REST API 路由
│   ├── models/             # 数据模型
│   ├── services/           # 业务逻辑服务
│   ├── tasks/              # Celery 异步任务
│   ├── datasets/           # 数据集处理
│   ├── utils/              # 工具函数
│   └── requirements.txt    # Python 依赖
│
├── frontend/               # Vue3 + TypeScript 前端
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   ├── views/         # 页面视图
│   │   ├── utils/         # 工具函数
│   │   ├── assets/        # 静态资源
│   │   └── websocket/    # WebSocket 客户端
│   └── package.json       # 前端依赖
│
└── docs/                   # 项目文档
```

## Technology Stack

### Backend
- Python 3.8+
- Flask 2.x - Web 框架
- PyTorch/TensorFlow - 深度学习模型
- Celery - 异步任务队列
- Redis - 消息队列存储
- SQLAlchemy - ORM

### Frontend
- Vue 3 + TypeScript
- Monaco Editor - 代码编辑器
- D3.js - 数据可视化
- Socket.io - WebSocket 实时通信
- Axios - HTTP 客户端

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Features

1. **Code Defect Detection** - AI-powered defect detection (≥85% accuracy)
2. **Smart Fix Suggestions** - Intelligent repair recommendations
3. **Team Collaboration** - Real-time collaboration via WebSocket
4. **Code Visualization** - Monaco Editor with syntax highlighting
5. **Defect Analysis** - D3.js visualization of analysis results
