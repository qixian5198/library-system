# 图书馆管理系统

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Vue](https://img.shields.io/badge/Vue-3-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

一个功能完整的图书馆管理 Web 应用系统，支持图书管理、读者管理、借书还书等核心功能。

## 功能特性

- 📚 **图书管理** - 图书的增删改查，支持搜索和分页
- 👥 **读者管理** - 读者信息维护
- 📖 **借阅管理** - 借书、还书、逾期提醒
- 📊 **统计面板** - 实时统计图书、读者、借阅数据
- 🔐 **用户认证** - JWT 身份验证，支持管理员和图书管理员

## 技术栈

| 技术 | 说明 |
|------|------|
| 后端 | Python + Flask + SQLAlchemy |
| 前端 | Vue 3 + Vite + Element Plus |
| 数据库 | PostgreSQL 15 |
| 部署 | Docker + Nginx |

## 项目结构

```
library-system/
├── docs/                    # 项目文档
│   └── PROJECT.md          # 详细项目文档
├── backend/                # Flask 后端
│   ├── app.py             # 主应用（API 接口）
│   ├── requirements.txt   # Python 依赖
│   └── Dockerfile         # 后端容器配置
├── frontend/              # Vue 3 前端
│   ├── src/
│   │   ├── api/           # API 接口封装
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── views/         # 页面组件
│   │   ├── App.vue        # 根组件
│   │   ├── main.js        # 入口文件
│   │   └── style.css      # 全局样式
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml     # Docker 编排配置
└── README.md             # 项目说明
```

## 快速开始

### 方式一：Docker 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/qixian5198/library-system.git
cd library-system

# 启动所有服务
docker-compose up -d

# 访问系统
# 前端：http://localhost
# 后端：http://localhost:5001
```

### 方式二：本地开发

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 图书管理员 | librarian | librarian123 |

## API 接口

### 认证
- `POST /api/auth/login` - 登录
- `GET /api/auth/me` - 获取当前用户

### 图书
- `GET /api/books` - 图书列表
- `GET /api/books/:id` - 图书详情
- `POST /api/books` - 添加图书
- `PUT /api/books/:id` - 更新图书
- `DELETE /api/books/:id` - 删除图书

### 读者
- `GET /api/readers` - 读者列表
- `POST /api/readers` - 添加读者
- `PUT /api/readers/:id` - 更新读者
- `DELETE /api/readers/:id` - 删除读者

### 借阅
- `GET /api/borrowings` - 借阅记录
- `POST /api/borrowings` - 借书
- `PUT /api/borrowings/:id/return` - 还书

### 统计
- `GET /api/stats` - 统计数据

## 数据库表结构

### books（图书表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| title | String | 书名 |
| author | String | 作者 |
| isbn | String | ISBN |
| publisher | String | 出版社 |
| category | String | 分类 |
| price | Float | 价格 |
| stock | Integer | 库存 |
| description | Text | 简介 |
| cover | String | 封面图 |

### readers（读者表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 姓名 |
| gender | String | 性别 |
| age | Integer | 年龄 |
| phone | String | 电话 |

### borrowings（借阅记录表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| book_id | Integer | 图书ID |
| reader_id | Integer | 读者ID |
| borrow_date | DateTime | 借阅日期 |
| due_date | DateTime | 应还日期 |
| return_date | DateTime | 实际归还日期 |
| status | String | 状态 |

### users（用户表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String | 用户名 |
| password_hash | String | 加密密码 |
| role | String | 角色 |

## 部署架构

```
                    ┌─────────────┐
                    │   Nginx     │
                    │  (端口 80)  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Vue     │ │ Flask    │ │ PostgreSQL
        │  (5173)  │ │ (5000)   │ │ (5432)   │
        └──────────┘ └──────────┘ └──────────┘
```

## 扩展开发

- 可添加图书分类管理
- 可添加图书预约功能
- 可添加逾期罚款功能
- 可添加图书评论功能
- 可集成邮件通知

## 许可证

MIT License

---

Made with ❤️ by 螃蟹 🦀
