# Wang Mingkai Portfolio Website Package

## 包含文件说明

### 核心应用文件
- `app.py` - Flask应用配置和初始化
- `main.py` - 应用程序入口点
- `routes.py` - URL路由和视图逻辑
- `dashboard.py` - 嵌入式Dash仪表板

### 模板文件 (templates/)
- `base.html` - 基础模板，包含导航和通用元素
- `index.html` - 主页项目展示
- `project_detail.html` - 项目详情页面
- `about.html` - 关于页面，包含简历和成绩单下载

### 静态资源 (static/)
- `downloads/` - 项目文件、数据集和代码示例
- `images/` - 项目截图和预览图片
- `css/` - 自定义样式文件
- `js/` - JavaScript交互脚本

### 数据文件 (data/)
- `projects.json` - 项目元数据和配置
- 其他数据文件

### 配置文件
- `pyproject.toml` - Python依赖管理
- `render_requirements.txt` - Render部署依赖
- `replit.md` - 项目架构和用户偏好文档
- `README.md` - 项目说明文档

## 当前项目组合包含

### 专业项目
1. **End-to-End Project of JSON Scripts + SQL** - 金融合规系统
2. **Paris 2024 Olympics Analytics Dashboard** - 奥运数据分析

### 学术项目
1. **Gender Discrimination Lawsuit Statistical Analysis** - 法律统计分析
2. **Machine Learning for Financial Risk Assessment** - 金融风险机器学习

### AI项目
1. **Financial Chatbot Services** - 金融AI聊天机器人

## 部署说明
- 使用Flask + Gunicorn
- 支持Replit和Render平台
- Bootstrap 5响应式设计
- 集成Dash数据可视化

## 技术栈
- Python Flask
- Plotly/Dash
- Bootstrap 5
- PostgreSQL支持
- JSON数据存储