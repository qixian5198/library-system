# 图书馆管理系统 - 项目文档

## 1. 项目概述

### 项目名称
Library Management System (图书馆管理系统)

### 项目目标
构建一个完整的图书馆管理 Web 应用，实现图书管理、读者管理、借书还书等核心功能。

### 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 后端 | Python + Flask | REST API |
| 前端 | Vue 3 + Vite | SPA 应用 |
| 数据库 | PostgreSQL 15 | 容器化部署 |
| 部署 | Docker + Nginx | 生产环境 |

---

## 2. 功能需求

### 2.1 图书管理
- [ ] 查看图书列表（分页、搜索）
- [ ] 添加新图书
- [ ] 编辑图书信息
- [ ] 删除图书
- [ ] 图书详情

**图书字段：**
- 书名 (title)
- 作者 (author)
- ISBN (isbn)
- 分类 (category)
- 出版日期 (publish_date)
- 库存数量 (stock)
- 简介 (description)

### 2.2 读者管理
- [ ] 查看读者列表
- [ ] 添加新读者
- [ ] 编辑读者信息
- [ ] 删除读者
- [ ] 读者详情

**读者字段：**
- 姓名 (name)
- 性别 (gender)
- 年龄 (age)
- 联系电话 (phone)
- 注册日期 (register_date)
- 借书数量 (borrowed_count)

### 2.3 借书还书
- [ ] 借书（选择图书、选择读者、记录借阅日期）
- [ ] 还书（自动计算是否逾期）
- [ ] 借阅记录查询
- [ ] 当前借阅状态查看

**借阅记录字段：**
- 图书ID (book_id)
- 读者ID (reader_id)
- 借阅日期 (borrow_date)
- 应还日期 (due_date)
- 实际归还日期 (return_date)
- 状态 (status: 借阅中/已归还/已逾期)

### 2.4 登录系统
- [ ] 管理员登录
- [ ] 密码加密存储
- [ ] JWT 身份验证

**用户字段：**
- 用户名 (username)
- 密码 (password_hash)
- 角色 (role: admin/librarian)

### 2.5 统计面板
- [ ] 总图书数量
- [ ] 今日借阅数量
- [ ] 逾期未还数量
- [ ] 在借数量

---

## 3. 数据库设计

### 表结构

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    books     │     │   readers    │     │  borrowings  │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ id           │     │ id           │     │ id           │
│ title        │     │ name         │     │ book_id      │
│ author       │     │ gender       │     │ reader_id    │
│ isbn         │     │ age          │     │ borrow_date  │
│ category     │     │ phone        │     │ due_date     │
│ publish_date │     │ register_date│     │ return_date  │
│ stock        │     │ borrowed_cnt │     │ status       │
│ description  │     └──────────────┘     └──────────────┘
└──────────────┘
       ↑               ┌──────────────┐
       │               │    users     │
       └───────────────│ id           │
                       │ username     │
                       │ password_hash│
                       │ role         │
                       └──────────────┘
```

---

## 4. API 设计

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login | 登录 |
| POST | /api/auth/logout | 登出 |

### 图书
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/books | 图书列表 |
| GET | /api/books/:id | 图书详情 |
| POST | /api/books | 添加图书 |
| PUT | /api/books/:id | 更新图书 |
| DELETE | /api/books/:id | 删除图书 |

### 读者
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/readers | 读者列表 |
| GET | /api/readers/:id | 读者详情 |
| POST | /api/readers | 添加读者 |
| PUT | /api/readers/:id | 更新读者 |
| DELETE | /api/readers/:id | 删除读者 |

### 借阅
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/borrowings | 借阅记录 |
| POST | /api/borrowings | 借书 |
| PUT | /api/borrowings/:id/return | 还书 |

### 统计
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/stats | 统计数据 |

---

## 5. 前端页面

| 页面 | 路由 | 说明 |
|------|------|------|
| 登录 | /login | 登录页面 |
| 首页 | / | 统计面板 + 快捷操作 |
| 图书管理 | /books | 图书列表 + 操作 |
| 读者管理 | /readers | 读者列表 + 操作 |
| 借阅管理 | /borrowings | 借阅记录 |
| 个人中心 | /profile | 个人信息 |

---

## 6. 部署架构

```
                    ┌─────────────┐
                    │   Nginx     │
                    │  (端口 80)  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Vue     │ │ Flask    │ │   PostgreSQL
        │  (5173)  │ │ (5000)   │ │ (5432)   │
        └──────────┘ └──────────┘ └──────────┘
```

---

## 7. 开发计划

### Phase 1: 后端基础
- [ ] Flask 项目初始化
- [ ] 数据库模型定义
- [ ] 图书 CRUD API

### Phase 2: 后端功能
- [ ] 读者 CRUD API
- [ ] 借阅管理 API
- [ ] 登录认证 API
- [ ] 统计 API

### Phase 3: 前端基础
- [ ] Vue 3 项目初始化
- [ ] 路由配置
- [ ] 登录页面

### Phase 4: 前端功能
- [ ] 图书管理页面
- [ ] 读者管理页面
- [ ] 借阅管理页面
- [ ] 统计面板

### Phase 5: 部署
- [ ] Docker 配置
- [ ] Nginx 配置
- [ ] 生产环境部署

---

## 8. 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 图书管理员 | librarian | librarian123 |

---

*文档版本: v1.0*  
*创建日期: 2026-05-07*
