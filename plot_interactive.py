import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# 读取数据
treasury_file = 'treasury_yields.csv'
exchange_file = 'exchange_rates.csv'

treasury_data = pd.read_csv(treasury_file, index_col=0, parse_dates=True)
exchange_data = pd.read_csv(exchange_file, index_col=0, parse_dates=True)

# 设置时间范围
time_ranges = {
    '近1个月': 30,
    '近3个月': 90,
    '近6个月': 180,
    '近1年': 365,
    '近3年': 1095
}

# 创建子图布局
fig = make_subplots(
    rows=4, cols=2,    # 修改为4行2列
    subplot_titles=('国债收益率曲线', '近1个月汇率变化',
                   '近3个月汇率变化', '近6个月汇率变化',
                   '近1年汇率变化', '近3年汇率变化'),
    vertical_spacing=0.1,
    horizontal_spacing=0.05
)

# 添加国债收益率数据
for col in treasury_data.columns:
    fig.add_trace(
        go.Scatter(
            x=treasury_data.index,
            y=treasury_data[col],
            name=col,
            line=dict(width=1),
            showlegend=True
        ),
        row=1, col=1
    )

# 获取当前日期
current_date = pd.Timestamp.now()

# 为每个时间范围添加汇率数据
for i, (period, days) in enumerate(time_ranges.items()):
    # 计算行列位置
    if i == 0:
        row, col = 2, 1
    elif i == 1:
        row, col = 2, 2
    elif i == 2:
        row, col = 3, 1
    elif i == 3:
        row, col = 3, 2
    else:
        row, col = 4, 1
    
    # 计算起始日期
    start_date = current_date - timedelta(days=days)
    period_data = exchange_data[exchange_data.index >= start_date].copy()
    
    # 计算相对变化
    if not period_data.empty:
        for column in period_data.columns:
            base_value = period_data[column].iloc[0]
            period_data[column] = (period_data[column] - base_value) / base_value * 100
    
        # 添加每个汇率的曲线
        for column in period_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=period_data.index,
                    y=period_data[column],
                    name=column,
                    line=dict(width=1),
                    showlegend=(i == 1)  # 只在第一个子图显示图例
                ),
                row=row, col=col
            )

# 添加重大事件标记
events = {
    '2008-09-15': '雷曼破产',
    '2020-03-23': '美联储无限QE',
    '2022-03-16': '加息周期启动'
}

# 在国债收益率图上添加事件标记
for date, label in events.items():
    fig.add_vline(
        x=date,
        line_dash="dash",
        line_color="red",
        opacity=0.5,
        row=1, col=1
    )
    fig.add_annotation(
        x=date,
        y=treasury_data.max().max(),
        text=label,
        showarrow=True,
        arrowhead=1,
        row=1, col=1
    )

# 更新布局
fig.update_layout(
    height=1200,
    width=1600,
    title_text="美国国债收益率与主要汇率走势分析",
    showlegend=True,
    hovermode='x unified',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    )
)

# 更新所有子图的Y轴标题
fig.update_yaxes(title_text="收益率 (%)", row=1, col=1)
for i in range(len(time_ranges)):
    row = (i // 2) + 2
    col = (i % 2) + 1
    fig.update_yaxes(title_text="相对变化 (%)", row=row, col=col)

# 更新所有子图的网格样式
fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

# 显示图表
fig.show()