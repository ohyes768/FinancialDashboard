# API 接口文档

## 概述

**服务名称**：Financial Dashboard API

**版本**：v1.0.0

**最后更新**：2025-11-26

**Base URL**：`http://localhost:8091/api`

**协议**：HTTP/HTTPS

**数据格式**：JSON

---

## 接口列表

| 方法 | 端点 | 描述 |
|-----|------|-----|
| GET | /chart-data | 获取图表数据 |
| GET | /health | 健康检查 |

---

## 接口详情

### 1. 获取图表数据

#### 基本信息
- **端点**：`GET /api/chart-data`
- **描述**：获取用于渲染金融数据可视化的完整图表数据
- **认证**：无需认证

#### 请求参数
无请求参数

#### 请求示例
```bash
curl -X GET "http://localhost:8091/api/chart-data"
```

```javascript
fetch('/api/chart-data')
  .then(response => response.json())
  .then(data => console.log(data));
```

#### 响应格式

**成功响应**（200 OK）：
```json
{
  "data": [
    {
      "x": ["2023-01-01", "2023-01-02", "2023-01-03", ...],
      "y": [100.0, 100.5, 101.2, ...],
      "name": "USD/CNY",
      "mode": "lines",
      "line": {"width": 1.5, "color": "#1f77b4"},
      "type": "scatter",
      "visible": true,
      "legendgroup": "exchange",
      "showlegend": true,
      "legendgrouptitle_text": "汇率"
    },
    {
      "x": ["2023-01-01", "2023-01-02", "2023-01-03", ...],
      "y": [4.5, 4.6, 4.7, ...],
      "name": "2年期",
      "mode": "lines",
      "line": {"width": 1.5},
      "type": "scatter",
      "visible": true,
      "legendgroup": "treasury",
      "showlegend": true,
      "legendgrouptitle_text": "美债"
    },
    {
      "x": ["2023-01-01", "2023-01-02", "2023-01-03", ...],
      "y": [35.0, 35.1, 35.2, ...],
      "name": "美债规模",
      "mode": "lines",
      "line": {"width": 1.5, "color": "blue"},
      "type": "scatter",
      "visible": true,
      "legendgroup": "debt",
      "showlegend": true,
      "legendgrouptitle_text": "美债规模"
    },
    {
      "x": ["2023-01-01", "2023-01-02", "2023-01-03", ...],
      "y": [27.5, 27.6, 27.7, ...],
      "name": "GDP规模",
      "mode": "lines",
      "line": {"width": 1.5, "color": "green"},
      "type": "scatter",
      "visible": true,
      "legendgroup": "gdp",
      "showlegend": true,
      "legendgrouptitle_text": "GDP规模"
    },
    {
      "x": ["2023-01-01", "2023-01-02", "2023-01-03", ...],
      "y": [127.0, 127.5, 128.0, ...],
      "name": "债务占GDP比重",
      "mode": "lines",
      "line": {"width": 1.5, "color": "red"},
      "type": "scatter",
      "visible": true,
      "legendgroup": "debt_ratio",
      "showlegend": true,
      "legendgrouptitle_text": "债务占比"
    },
    {
      "x": ["2023-01-01", "2023-01-02", "2023-01-03", ...],
      "y": [0.8, 0.85, 0.9, ...],
      "name": "TGA账户余额",
      "mode": "lines",
      "line": {"width": 1.5, "color": "purple"},
      "type": "scatter",
      "visible": true,
      "legendgroup": "tga",
      "showlegend": true,
      "legendgrouptitle_text": "TGA账户"
    },
    {
      "x": ["2023-01-01", "2023-01-02", "2023-01-03", ...],
      "y": [5.5, 5.6, 5.7, ...],
      "name": "HIBOR",
      "mode": "lines",
      "line": {"width": 1.5, "color": "orange"},
      "type": "scatter",
      "visible": true,
      "legendgroup": "hibor",
      "showlegend": true,
      "legendgrouptitle_text": "HIBOR"
    }
  ],
  "layout": {
    "height": 1200,
    "width": 1400,
    "hovermode": "x unified",
    "showlegend": false,
    "legend": {
      "orientation": "v",
      "yanchor": "top",
      "y": 0.45,
      "xanchor": "left",
      "x": 0.02,
      "traceorder": "grouped",
      "groupclick": "toggleitem",
      "bgcolor": "rgba(255,255,255,0.8)",
      "bordercolor": "LightGray",
      "borderwidth": 1
    },
    "margin": {
      "l": 50,
      "r": 250,
      "t": 120,
      "b": 50
    },
    "hoverdistance": 50,
    "spikedistance": -1,
    "paper_bgcolor": "white",
    "dragmode": "zoom",
    "modebar": {
      "activecolor": "#1f77b4",
      "orientation": "v",
      "bgcolor": "rgba(255,255,255,0.8)"
    },
    "updatemenus": [
      {
        "type": "buttons",
        "direction": "right",
        "x": 0.65,
        "y": 1.15,
        "showactive": true,
        "active": 4,
        "buttons": [
          {
            "label": "近1个月",
            "method": "update",
            "args": [[...], {"title": "市场数据相对变化走势（近1个月）"}]
          },
          {
            "label": "近3个月",
            "method": "update",
            "args": [[...], {"title": "市场数据相对变化走势（近3个月）"}]
          },
          {
            "label": "近6个月",
            "method": "update",
            "args": [[...], {"title": "市场数据相对变化走势（近6个月）"}]
          },
          {
            "label": "近1年",
            "method": "update",
            "args": [[...], {"title": "市场数据相对变化走势（近1年）"}]
          },
          {
            "label": "近3年",
            "method": "update",
            "args": [[...], {"title": "市场数据相对变化走势（近3年）"}]
          },
          {
            "label": "全部",
            "method": "update",
            "args": [[...], {"title": "市场数据相对变化走势（全部）"}]
          }
        ]
      }
    ],
    "grid": {
      "rows": 4,
      "columns": 1,
      "pattern": "independent"
    },
    "xaxis": {
      "title": "",
      "showgrid": true,
      "gridwidth": 1,
      "gridcolor": "LightGray",
      "showspikes": true,
      "spikesnap": "cursor",
      "spikemode": "across+marker",
      "spikethickness": 2,
      "spikecolor": "rgba(0,0,0,0.5)",
      "spikedash": "dash",
      "showline": true,
      "showticklabels": true,
      "fixedrange": false
    },
    "yaxis": {
      "title": {"text": "相对变化 (%)"},
      "showgrid": true,
      "gridwidth": 1,
      "gridcolor": "LightGray",
      "showspikes": false,
      "showline": true,
      "showticklabels": true,
      "fixedrange": true
    },
    "xaxis2": {
      "title": "",
      "showgrid": true,
      "gridwidth": 1,
      "gridcolor": "LightGray",
      "showspikes": true,
      "spikesnap": "cursor",
      "spikemode": "across+marker",
      "spikethickness": 2,
      "spikecolor": "rgba(0,0,0,0.5)",
      "spikedash": "dash",
      "showline": true,
      "showticklabels": true,
      "fixedrange": false
    },
    "yaxis2": {
      "title": {"text": "收益率 (%)"},
      "showgrid": true,
      "gridwidth": 1,
      "gridcolor": "LightGray",
      "showspikes": false,
      "showline": true,
      "showticklabels": true,
      "fixedrange": true
    },
    "xaxis3": {
      "title": "",
      "showgrid": true,
      "gridwidth": 1,
      "gridcolor": "LightGray",
      "showspikes": true,
      "spikesnap": "cursor",
      "spikemode": "across+marker",
      "spikethickness": 2,
      "spikecolor": "rgba(0,0,0,0.5)",
      "spikedash": "dash",
      "showline": true,
      "showticklabels": true,
      "fixedrange": false
    },
    "yaxis3": {
      "title": {"text": "规模（万亿美元）"},
      "showgrid": true,
      "gridwidth": 1,
      "gridcolor": "LightGray",
      "showspikes": false,
      "showline": true,
      "showticklabels": true,
      "fixedrange": true,
      "secondary": false
    },
    "yaxis4": {
      "title": {"text": "占GDP比重 (%)"},
      "showgrid": false,
      "showline": true,
      "showticklabels": true,
      "fixedrange": true,
      "overlaying": "y",
      "secondary": true
    },
    "xaxis4": {
      "title": "",
      "showgrid": true,
      "gridwidth": 1,
      "gridcolor": "LightGray",
      "showspikes": true,
      "spikesnap": "cursor",
      "spikemode": "across+marker",
      "spikethickness": 2,
      "spikecolor": "rgba(0,0,0,0.5)",
      "spikedash": "dash",
      "showline": true,
      "showticklabels": true,
      "fixedrange": false
    },
    "yaxis5": {
      "title": {"text": "TGA账户余额（万亿美元）"},
      "showgrid": true,
      "gridwidth": 1,
      "gridcolor": "LightGray",
      "showspikes": false,
      "showline": true,
      "showticklabels": true,
      "fixedrange": true,
      "secondary": false
    },
    "yaxis6": {
      "title": {"text": "HIBOR (%)"},
      "showgrid": false,
      "showline": true,
      "showticklabels": true,
      "fixedrange": true,
      "overlaying": "y5",
      "secondary": true
    },
    "annotations": [
      {
        "x": 0.95,
        "y": 0.8,
        "xref": "paper",
        "yref": "paper",
        "text": "<b>重大事件</b><br><br>2023-01-01: 事件描述1<br>2023-06-01: 事件描述2",
        "showarrow": false,
        "font": {"size": 11},
        "align": "left",
        "bgcolor": "rgba(255,255,255,0.8)",
        "bordercolor": "LightGray",
        "borderwidth": 1,
        "xanchor": "left",
        "yanchor": "middle",
        "width": 280
      }
    ]
  },
  "metadata": {
    "generated_at": "2025-11-26T10:30:00.123456"
  }
}
```

**响应字段说明**：

| 字段 | 类型 | 描述 |
|-----|------|-----|
| data | array | 图表数据系列数组 |
| layout | object | 图表布局配置 |
| metadata | object | 元数据信息 |

**data 数组中每个对象的字段**：

| 字段 | 类型 | 描述 |
|-----|------|-----|
| x | array | X 轴数据（日期数组） |
| y | array | Y 轴数据（数值数组） |
| name | string | 数据系列名称 |
| mode | string | 图表模式（lines/scatter等） |
| line | object | 线条样式配置 |
| type | string | 图表类型 |
| visible | boolean | 是否可见 |
| legendgroup | string | 图例分组 |
| showlegend | boolean | 是否显示图例 |
| legendgrouptitle_text | string | 图例分组标题 |

#### 错误响应

**500 Internal Server Error**：
```json
{
  "error": "生成图表数据失败: 文件未找到 data/exchange_rates.csv"
}
```

---

### 2. 健康检查

#### 基本信息
- **端点**：`GET /api/health`
- **描述**：检查 API 服务是否正常运行
- **认证**：无需认证

#### 请求参数
无请求参数

#### 请求示例
```bash
curl -X GET "http://localhost:8091/api/health"
```

```javascript
fetch('/api/health')
  .then(response => response.json())
  .then(data => console.log(data));
```

#### 响应格式

**成功响应**（200 OK）：
```json
{
  "status": "healthy",
  "message": "Financial Dashboard API is running",
  "timestamp": "2025-11-26T10:30:00.123456"
}
```

**响应字段说明**：

| 字段 | 类型 | 描述 |
|-----|------|-----|
| status | string | 服务状态（healthy/unhealthy） |
| message | string | 状态消息 |
| timestamp | string | 时间戳（ISO 8601 格式） |

---

## 数据系列说明

### 图表1：汇率相对变化走势
**数据系列**：
- USD/CNY - 美元兑人民币
- USD/EUR - 美元兑欧元
- USD/JPY - 美元兑日元
- USD/GBP - 美元兑英镑

**Y 轴单位**：相对变化 (%)

### 图表2：美债收益率走势
**数据系列**：
- 2年期 - 2年期美国国债收益率
- 5年期 - 5年期美国国债收益率
- 10年期 - 10年期美国国债收益率
- 30年期 - 30年期美国国债收益率

**Y 轴单位**：收益率 (%)

### 图表3：美债规模、GDP规模及占比走势
**数据系列**：
- 美债规模 - 美国国债总规模（左Y轴）
- GDP规模 - 美国GDP总量（左Y轴）
- 债务占GDP比重 - 债务占GDP百分比（右Y轴）

**左Y轴单位**：万亿美元
**右Y轴单位**：百分比 (%)

### 图表4：TGA账户余额与HIBOR走势
**数据系列**：
- TGA账户余额 - 美国财政部一般账户余额（左Y轴）
- HIBOR - 香港银行同业拆息（右Y轴）

**左Y轴单位**：万亿美元
**右Y轴单位**：百分比 (%)

---

## 时间范围说明

| 范围 | 天数 | 描述 |
|-----|------|-----|
| 近1个月 | 30 | 最近30个自然日 |
| 近3个月 | 90 | 最近90个自然日 |
| 近6个月 | 180 | 最近180个自然日 |
| 近1年 | 365 | 最近365个自然日 |
| 近3年 | 1095 | 最近1095个自然日（默认显示） |
| 全部 | null | 全部可用数据 |

---

## API 变更记录

### 2025-11-26 v1.0.0 - 前后端分离
- **变更类型**：新增
- **新增端点**：
  - GET /api/chart-data - 获取图表数据
  - GET /api/health - 健康检查
- **变更内容**：
  - 将图表生成逻辑从直接渲染转为 API 返回 JSON
  - 支持前端通过 JavaScript 动态渲染图表
  - 响应格式兼容 Plotly.js

---

## 错误码说明

| HTTP 状态码 | 描述 | 处理建议 |
|------------|-----|---------|
| 200 | 请求成功 | 正常处理响应数据 |
| 500 | 服务器内部错误 | 检查服务器日志，确认数据文件存在 |

---

## 使用示例

### 完整的前端调用示例

```html
<!DOCTYPE html>
<html>
<head>
    <title>Financial Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div id="chart"></div>

    <script>
        async function loadChart() {
            try {
                const response = await fetch('/api/chart-data');
                const data = await response.json();

                if (response.ok) {
                    Plotly.newPlot('chart', data.data, data.layout);
                    console.log('Chart loaded successfully');
                } else {
                    console.error('Error:', data.error);
                }
            } catch (error) {
                console.error('Failed to load chart:', error);
            }
        }

        loadChart();
    </script>
</body>
</html>
```

---

## 注意事项

1. **跨域问题**：前后端在同一域下部署时无跨域问题
2. **数据更新**：每次调用都会重新生成图表数据
3. **性能考虑**：建议前端缓存响应数据，避免频繁请求
4. **错误处理**：前端应正确处理网络错误和 API 错误
