# 技术设计文档 (TDD)

## 项目概述

**项目名称**：Financial Dashboard（金融数据可视化仪表板）

**版本**：v1.0.0

**最后更新**：2025-11-26

**架构类型**：前后端分离架构

---

## 系统架构

### 1. 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              前端服务 (fastapi_dashboard_main.py)            │
│                       端口: 8090                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI 主应用                                      │  │
│  │  - 静态文件服务 (/static)                            │  │
│  │  - 根路径重定向 (/ → /static/index.html)             │  │
│  │  - API 路由挂载 (/api → backend app)                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ API 挂载
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          后端 API 服务 (fastapi_dashboard_backend.py)        │
│                       端口: 8091                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI API 应用                                    │  │
│  │  - GET /api/chart-data (图表数据)                    │  │
│  │  - GET /api/health (健康检查)                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ 文件读取
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                        数据存储层                             │
│  ┌────────────────────┐  ┌────────────────────┐             │
│  │   data/ 目录        │  │   event.txt        │             │
│  │  - exchange_rates  │  │  (重大事件)         │             │
│  │  - treasury_yields │  └────────────────────┘             │
│  │  - treasury_debt   │                                     │
│  │  - tga_hibor_data  │                                     │
│  └────────────────────┘                                     │
└─────────────────────────────────────────────────────────────┘
```

### 2. 前后端分离设计

#### 2.1 前端服务 (端口 8090)
- **文件**：`fastapi_dashboard_main.py`
- **职责**：
  - 提供静态文件服务（HTML、CSS、JS）
  - 根路径重定向到前端页面
  - 挂载后端 API 路由

#### 2.2 后端 API 服务 (端口 8091)
- **文件**：`fastapi_dashboard_backend.py`
- **职责**：
  - 处理数据获取和处理逻辑
  - 生成图表数据
  - 提供 RESTful API 接口

#### 2.3 优势
- **独立部署**：前后端可独立部署和扩展
- **技术解耦**：前端和后端使用独立技术栈
- **API 复用**：API 可供其他客户端调用
- **开发效率**：前后端可并行开发

---

## 技术栈

### 1. 后端技术
| 技术 | 版本 | 用途 |
|-----|------|-----|
| Python | 3.13+ | 主要开发语言 |
| FastAPI | 0.121.3 | Web 框架 |
| Uvicorn | 0.38.0 | ASGI 服务器 |
| Pandas | 2.3.3 | 数据处理 |
| Plotly | 6.4.0 | 图表生成 |

### 2. 前端技术
| 技术 | 版本 | 用途 |
|-----|------|-----|
| HTML5 | - | 页面结构 |
| JavaScript | ES6+ | 交互逻辑 |
| Plotly.js | 最新版 | 图表渲染 |

### 3. 数据源
| 数据来源 | 用途 | 获取方式 |
|---------|-----|---------|
| FRED | 美国经济数据 | fredapi |
| Yahoo Finance | 汇率数据 | yfinance |

---

## 核心模块设计

### 1. 图表生成模块

#### 1.1 函数签名
```python
def create_financial_chart() -> go.Figure
```

#### 1.2 处理流程
```
┌──────────────────────────────────────────────────────────┐
│                    create_financial_chart                 │
└──────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   ┌───────────┐    ┌───────────┐    ┌───────────┐
   │ 读取汇率   │    │ 读取美债   │    │ 读取TGA   │
   │   数据     │    │   数据     │    │  HIBOR    │
   └───────────┘    └───────────┘    └───────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           ▼
                   ┌───────────────┐
                   │  数据预处理    │
                   │  - 缺失值处理  │
                   │  - 时间对齐    │
                   │  - 数据合并    │
                   └───────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │  创建子图     │
                   │  - 4个图表    │
                   │  - 双Y轴配置  │
                   └───────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │  添加数据系列 │
                   │  - 6个时间范围│
                   │  - 多条曲线    │
                   └───────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │  配置交互     │
                   │  - 时间切换    │
                   │  - 重置视图    │
                   └───────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │  更新布局样式 │
                   └───────────────┘
                           │
                           ▼
                      返回 Figure
```

#### 1.3 数据处理逻辑
```python
# 1. 读取数据
exchange_data = pd.read_csv('data/exchange_rates.csv', index_col=0, parse_dates=True)

# 2. 生成完整时间索引（工作日）
full_index = pd.date_range(start=start_date, end=end_date, freq='B')

# 3. 重新索引并插值
data = data.reindex(full_index)
data = data.interpolate(method='time')
data = data.ffill().bfill()

# 4. 计算相对变化（仅汇率）
relative_change = (data - base_value) / base_value * 100
```

#### 1.4 图表配置
- **子图数量**：4 个（垂直排列）
- **共享 X 轴**：所有子图共享时间轴
- **双 Y 轴**：第 3、4 个子图使用双 Y 轴
- **时间范围**：6 个（1个月、3个月、6个月、1年、3年、全部）

### 2. API 端点设计

#### 2.1 GET /api/chart-data
**功能**：获取图表数据

**请求**：
```http
GET /api/chart-data
```

**响应**：
```json
{
  "data": [
    {
      "x": ["2023-01-01", "2023-01-02", ...],
      "y": [100.5, 101.2, ...],
      "name": "USD/CNY",
      "visible": true,
      ...
    },
    ...
  ],
  "layout": {
    "height": 1200,
    "width": 1400,
    "hovermode": "x unified",
    ...
  },
  "metadata": {
    "generated_at": "2025-11-26T10:30:00"
  }
}
```

**错误响应**：
```json
{
  "error": "生成图表数据失败: 详细错误信息"
}
```

#### 2.2 GET /api/health
**功能**：健康检查

**请求**：
```http
GET /api/health
```

**响应**：
```json
{
  "status": "healthy",
  "message": "Financial Dashboard API is running",
  "timestamp": "2025-11-26T10:30:00"
}
```

### 3. 前端模块设计

#### 3.1 文件结构
```
static/
├── index.html       # 主页面
└── plotly.min.js    # Plotly 库
```

#### 3.2 主要函数
```javascript
async function loadChart() {
    // 1. 检查 Plotly 是否加载
    if (typeof Plotly === 'undefined') {
        // 错误处理
        return;
    }

    // 2. 调用 API 获取数据
    const response = await fetch('/api/chart-data');
    const data = await response.json();

    // 3. 渲染图表
    if (response.ok) {
        Plotly.newPlot(container, data.data, data.layout);
        // 更新时间戳
    }
}
```

---

## 目录结构

```
FinancialDashboard/
├── data/                           # 数据文件目录
│   ├── exchange_rates.csv          # 汇率数据
│   ├── treasury_yields.csv         # 美债收益率数据
│   ├── treasury_debt_gdp.csv       # 美债和GDP数据
│   └── tga_hibor_data.csv          # TGA和HIBOR数据
│
├── static/                         # 静态文件目录
│   ├── index.html                  # 前端主页面
│   └── plotly.min.js               # Plotly 库
│
├── docs/                           # 文档目录
│   ├── 产品需求文档(PRD).md
│   ├── 技术设计文档(TDD).md
│   ├── API接口文档.md
│   ├── 数据字典.md
│   └── 文档索引.md
│
├── discuss/                        # 讨论文档目录
│
├── logs/                           # 日志目录（运行时生成）
│   └── financial_dashboard.log     # 应用日志
│
├── fastapi_dashboard_main.py       # 前端服务主入口
├── fastapi_dashboard_backend.py    # 后端 API 服务
├── exchangeRate_data.py            # 汇率数据获取脚本
├── tgaHibor_data.py                # TGA和HIBOR数据获取脚本
├── usTreasuryBond_data.py          # 美债收益率数据获取脚本
├── usTreasuryDebt_data.py          # 美债和GDP数据获取脚本
├── plot_interactive_tab.py         # 绘图工具模块
├── event.txt                       # 重大事件文件
├── requirements.txt                # Python 依赖
├── README.md                       # 项目说明
└── .gitignore                      # Git 忽略配置
```

---

## 部署架构

### 1. 开发环境
```bash
# 前端服务（端口 8090）
python fastapi_dashboard_main.py

# 后端服务（端口 8091）
python fastapi_dashboard_backend.py
```

### 2. 生产环境
```bash
# 前端服务
uvicorn fastapi_dashboard_main:app --host 0.0.0.0 --port 8090

# 后端服务
uvicorn fastapi_dashboard_backend:app --host 0.0.0.0 --port 8091
```

### 3. 使用 Uvicorn 特性
- **热重载**：开发模式使用 `--reload` 参数
- **多进程**：生产环境可使用 `--workers` 参数
- **日志**：自动记录访问日志和错误日志

---

## 数据流设计

### 1. 图表数据流
```
┌──────────────┐
│ CSV 数据文件  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Pandas 读取  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 数据预处理   │
│ - 缺失值处理 │
│ - 时间对齐   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Plotly 生成  │
│   Figure     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 转换为 JSON  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ API 返回     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 前端接收     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Plotly.js    │
│   渲染图表   │
└──────────────┘
```

---

## 错误处理

### 1. 数据文件缺失
```python
try:
    data = pd.read_csv(file_path)
except FileNotFoundError:
    logger.error(f"文件未找到: {file_path}")
    raise
except Exception as e:
    logger.error(f"读取文件失败: {str(e)}")
    raise
```

### 2. API 错误响应
```python
try:
    chart_data = generate_chart()
    return JSONResponse(content=chart_data)
except Exception as e:
    logger.error(f"生成图表失败: {str(e)}", exc_info=True)
    return JSONResponse(
        content={"error": f"生成图表数据失败: {str(e)}"},
        status_code=500
    )
```

### 3. 前端错误处理
```javascript
try {
    const response = await fetch('/api/chart-data');
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    // 处理数据
} catch (error) {
    container.innerHTML = `<div class="error">加载数据失败: ${error.message}</div>`;
}
```

---

## 日志设计

### 1. 日志配置
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_dashboard.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
```

### 2. 日志级别
- **INFO**：正常操作记录（数据读取、图表生成）
- **WARNING**：警告信息（事件文件未找到）
- **ERROR**：错误信息（文件读取失败、生成失败）

### 3. 日志文件
- **位置**：`logs/financial_dashboard.log`
- **编码**：UTF-8
- **轮转**：可配置日志轮转策略

---

## 性能优化

### 1. 数据处理优化
- 使用 Pandas 向量化操作
- 预处理数据并缓存（可选）
- 按需加载时间范围数据

### 2. API 优化
- 使用 JSON 序列化优化
- 启用 HTTP 压缩（gzip）
- 添加缓存头（可选）

### 3. 前端优化
- 使用本地 Plotly.js 文件
- 按需加载数据
- 延迟渲染大图表

---

## 技术实现更新

### 2025-11-26 v1.0.0 - 前后端分离架构
- **变更内容**：
  - 将单体应用拆分为前端服务和后端 API 服务
  - 新增 `fastapi_dashboard_main.py`（前端服务）
  - 新增 `fastapi_dashboard_backend.py`（后端 API）
  - 新增 `static/index.html`（前端页面）
- **技术方案**：
  - 前端：FastAPI StaticFiles + HTML/JavaScript
  - 后端：FastAPI + Plotly 生成 JSON 数据
  - 通信：RESTful API（JSON 格式）
- **代码位置**：
  - 前端：`fastapi_dashboard_main.py`, `static/index.html`
  - 后端：`fastapi_dashboard_backend.py`
- **依赖关系**：
  - 前端依赖后端 API
  - 后端独立运行

### 2025-11-20 v0.2.0 - 增加 FastAPI 方式
- **变更内容**：
  - 引入 FastAPI 框架
  - 支持 Web 服务方式访问
- **技术方案**：
  - 使用 FastAPI 替代传统脚本
  - Uvicorn 作为 ASGI 服务器

### 2025-11-20 v0.1.0 - 项目初始化
- **变更内容**：
  - 数据获取模块（exchangeRate_data.py, tgaHibor_data.py 等）
  - Plotly 可视化
- **技术方案**：
  - Pandas 数据处理
  - Plotly 图表生成
