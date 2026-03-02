# FRED API 国际债券数据调研

**记录日期**：2026-03-02

**调研目的**：了解 FRED API 是否提供欧债、日债的 2 年期和 3 个月期利率数据

---

## 结论

**FRED API 基本没有欧债、日债的 2 年期和 3 个月期利率数据。**

---

## FRED 的国际债券数据特点

### 1. OECD 数据系列（通过 FRED 获取）

OECD（经济合作与发展组织）通过 FRED 提供的政府债券收益率数据具有以下特点：

- **期限限制**：主要是 **10 年期长期政府债券收益率**
- **不提供**：2 年期、3 个月期等短期数据

#### 可用的数据系列代码

| 国家/地区 | 期限 | FRED 代码 | 说明 |
|----------|-----|----------|------|
| 美国 | 3 个月 | DGS3MO | FRED 自有数据 |
| 美国 | 2 年 | DGS2 | FRED 自有数据 |
| 美国 | 5 年 | DGS5 | FRED 自有数据 |
| 美国 | 10 年 | DGS10 | FRED 自有数据 |
| 美国 | 30 年 | DGS30 | FRED 自有数据 |
| **德国** | **10 年** | **IRLTLT01DEM156N** | OECD 数据 |
| **日本** | **10 年** | **IRLTLT01JPM156N** | OECD 数据 |
| 其他国家 | 10 年 | IRLTLT01 + 国家代码 + 156N | OECD 数据 |

#### OECD 数据系列命名规则

```
IRLTLT01 + 国家代码 + 156N
```

- **IRLTLT01**：长期利率（Long Term Interest Rates）标识
- **国家代码示例**：
  - DEM（德国）
  - JPM（日本）
  - FRA（法国）
  - GBR（英国）
  - 等

### 2. 美国国债数据（FRED 自有）

FRED 对美国本土的国债数据覆盖最完整：

| 期限 | FRED 代码 | 数据频率 | 起始日期 |
|-----|----------|---------|---------|
| 3 个月 | DGS3MO | 每日 | 1981-09-01 |
| 2 年 | DGS2 | 每日 | 1976-06-01 |
| 5 年 | DGS5 | 每日 | 1962-01-02 |
| 10 年 | DGS10 | 每日 | 1962-01-02 |
| 30 年 | DGS30 | 每日 | 1977-02-15 |

---

## 替代数据源推荐

如需获取欧债、日债的短期利率数据，可考虑以下数据源：

### 1. 欧洲央行（ECB）

- **覆盖范围**：欧元区各国政府债券
- **数据完整性**：提供完整的收益率曲线（包括 2 年期、3 个月期）
- **访问方式**：ECB Statistical Data Warehouse
- **费用**：免费
- **官网**：https://sdw.ecb.europa.eu/

### 2. Bank of Japan（日本央行）

- **覆盖范围**：日本国债（JGB）
- **数据完整性**：完整期限
- **访问方式**：Bank of Japan Statistics
- **费用**：免费
- **官网**：https://www.boj.or.jp/en/statistics/

### 3. Trading Economics

- **覆盖范围**：全球宏观经济数据
- **数据完整性**：多国政府债券收益率
- **访问方式**：API / 网页查询
- **费用**：部分免费，完整功能需付费
- **官网**：https://tradingeconomics.com/

### 4. investing.com

- **覆盖范围**：全球金融数据
- **数据完整性**：债券、股票、期货等
- **访问方式**：网页 / 爬虫
- **费用**：基础数据免费
- **官网**：https://www.investing.com/

### 5. 专业金融数据源（付费）

| 数据源 | 覆盖范围 | 特点 |
|--------|---------|------|
| Bloomberg | 全球 | 最全面、实时数据、价格昂贵 |
| Refinitiv (路透) | 全球 | 金融行业标准、API 完善 |
| FactSet | 全球 | 侧重机构投资者 |

---

## 实施建议

如果项目需要展示**美债、欧债、日债的多期限对比**：

### 方案 A：混合数据源（推荐）

| 债券类型 | 数据源 | 原因 |
|---------|--------|------|
| 美国国债 | FRED | 数据完整、免费、稳定 |
| 德国国债 | ECB | 完整期限、官方权威 |
| 日本国债 | Bank of Japan | 完整期限、官方权威 |

### 方案 B：统一商业数据源

使用 Trading Economics 或专业数据源统一获取所有数据：
- **优点**：接口统一、维护简单
- **缺点**：可能需要付费

---

## 技术实现参考

### 使用 fredapi 获取 OECD 数据

```python
from fredapi import Fred

fred = Fred(api_key='your_api_key')

# 获取德国 10 年期国债收益率
germany_10y = fred.get_series('IRLTLT01DEM156N')

# 获取日本 10 年期国债收益率
japan_10y = fred.get_series('IRLTLT01JPM156N')
```

### ECB 数据获取示例（伪代码）

```python
import requests

# ECB SDW API endpoint
url = "https://sdw-wsrest.ecb.europa.eu/service/data/..."

# 德国 2 年期国债收益率
params = {
    'series': 'IR_M2Y_DE_RT_EUR',
    'format': 'json'
}

response = requests.get(url, params=params)
```

---

## 相关资源

- [FRED 官网](https://fred.stlouisfed.org/)
- [FRED API 文档](https://fred.stlouisfed.org/docs/api/fred/)
- [OECD 数据](https://data.oecd.org/)
- [ECB Statistical Data Warehouse](https://sdw.ecb.europa.eu/)
- [Bank of Japan Statistics](https://www.boj.or.jp/en/statistics/)

---

## 更新记录

| 日期 | 更新内容 |
|-----|---------|
| 2026-03-02 | 创建文档，记录 FRED API 对国际债券数据的覆盖情况 |
