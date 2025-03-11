import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# 读取汇率数据
exchange_file = 'exchange_rates.csv'
exchange_data = pd.read_csv(exchange_file, index_col=0, parse_dates=True)

# 读取美债收益率数据
treasury_file = 'treasury_yields.csv'
treasury_data = pd.read_csv(treasury_file, index_col=0, parse_dates=True)

# 处理汇率数据缺失值
full_index = pd.date_range(start=exchange_data.index.min(), end=exchange_data.index.max(), freq='B')
exchange_data = exchange_data.reindex(full_index)
exchange_data = exchange_data.interpolate(method='time')
exchange_data = exchange_data.fillna(method='ffill').fillna(method='bfill')

# 处理美债数据缺失值
treasury_data = treasury_data.reindex(full_index)
treasury_data = treasury_data.interpolate(method='time')
treasury_data = treasury_data.fillna(method='ffill').fillna(method='bfill')

# 读取美债和GDP数据
debt_gdp_file = 'treasury_and_gdp.csv'
debt_gdp_data = pd.read_csv(debt_gdp_file, index_col=0, parse_dates=True)

# 处理美债数据缺失值
debt_gdp_data = debt_gdp_data.reindex(full_index)
debt_gdp_data = debt_gdp_data.interpolate(method='time')
debt_gdp_data = debt_gdp_data.fillna(method='ffill').fillna(method='bfill')

# 合并所有数据
data = pd.concat([exchange_data, treasury_data, debt_gdp_data], axis=1)

# 创建带有三个子图的基础图形
fig = make_subplots(
    rows=3, cols=1,
    subplot_titles=('汇率相对变化走势', '美债收益率走势', '美债规模及占比走势'),
    vertical_spacing=0.08,
    shared_xaxes=True,
    specs=[[{"secondary_y": False}],
           [{"secondary_y": False}],
           [{"secondary_y": True}]]
)

# 设置时间范围选项
time_ranges = {
    '近1个月': 30,
    '近3个月': 90,
    '近6个月': 180,
    '近1年': 365,
    '近3年': 1095,
    '全部': None
}

# 获取当前日期
current_date = pd.Timestamp.now()

# 为每个时间范围创建数据
for period, days in time_ranges.items():
    if days is None:
        period_data = data.copy()
    else:
        start_date = current_date - timedelta(days=days)
        period_data = data[data.index >= start_date].copy()
    
    # 计算相对变化
    if not period_data.empty:
        # 处理汇率数据
        for column in exchange_data.columns:
            base_value = period_data[column].iloc[0]
            relative_change = (period_data[column] - base_value) / base_value * 100
            
            # 添加汇率曲线到第一个子图
            fig.add_trace(
                go.Scatter(
                    x=period_data.index,
                    y=relative_change,
                    name=f"{column}",
                    line=dict(width=1.5),
                    visible=(period == '全部'),
                    legendgroup='exchange',
                    showlegend=(period == '全部'),
                    legendgrouptitle_text="汇率"
                ),
                row=1, col=1
            )
        
        # 处理美债数据 - 直接使用实际值
        for column in treasury_data.columns:
            # 添加美债曲线到第二个子图
            fig.add_trace(
                go.Scatter(
                    x=period_data.index,
                    y=period_data[column],
                    name=f"{column}",
                    line=dict(width=1.5),
                    visible=(period == '全部'),
                    legendgroup='treasury',
                    showlegend=(period == '全部'),
                    legendgrouptitle_text="美债"
                ),
                row=2, col=1
            )

    # 在循环中添加第三个子图的数据
    if not period_data.empty:
        # 添加美债规模曲线到第三个子图（左Y轴）
        fig.add_trace(
            go.Scatter(
                x=period_data.index,
                y=period_data['国债'],
                name='美债规模',
                line=dict(width=1.5, color='blue'),
                visible=(period == '全部'),
                legendgroup='debt',
                showlegend=(period == '全部'),
                legendgrouptitle_text="美债规模"
            ),
            row=3, col=1, secondary_y=False
        )
        
        # 添加债务占比曲线到第三个子图（右Y轴）
        fig.add_trace(
            go.Scatter(
                x=period_data.index,
                y=period_data['债务占比'],
                name='债务占GDP比重',
                line=dict(width=1.5, color='red'),
                visible=(period == '全部'),
                legendgroup='debt_ratio',
                showlegend=(period == '全部'),
                legendgrouptitle_text="债务占比"
            ),
            row=3, col=1, secondary_y=True
        )

# 更新按钮配置
buttons = []
exchange_trace_count = len(exchange_data.columns)
treasury_trace_count = len(treasury_data.columns)
debt_trace_count = 2  # 美债规模和占比两条线
total_trace_count = exchange_trace_count + treasury_trace_count + debt_trace_count

for i, period in enumerate(time_ranges.keys()):
    visible = [False] * (len(time_ranges) * total_trace_count)
    for j in range(total_trace_count):
        visible[i * total_trace_count + j] = True
    
    buttons.append(
        dict(
            label=period,
            method="update",
            args=[
                {"visible": visible},
                {"title": f"市场数据相对变化走势（{period}）"}
            ]
        )
    )

# 添加按钮菜单
fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            direction="right",
            x=0.65,  # 调整按钮位置
            y=1.12,
            showactive=True,
            buttons=buttons
        ),
        dict(
            type="buttons",
            direction="right",
            x=0.85,  # 调整按钮位置
            y=1.12,
            showactive=False,
            buttons=[
                dict(
                    args=[{'xaxis.autorange': True, 'yaxis.autorange': True,
                          'xaxis2.autorange': True, 'yaxis2.autorange': True,
                          'xaxis3.autorange': True, 'yaxis3.autorange': True,
                          'yaxis4.autorange': True}],  # 添加第三个子图的轴
                    label="恢复默认视图",
                    method="relayout"
                )
            ]
        )
    ]
)

# 更新布局
fig.update_layout(
    height=1000,  # 增加整体高度
    width=1200,
    hovermode='x unified',
    showlegend=True,
    legend=dict(
        orientation="v",
        yanchor="top",
        y=0.45,
        xanchor="left",
        x=0.02,
        traceorder='grouped',
        groupclick="toggleitem",
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='LightGray',
        borderwidth=1
    ),
    margin=dict(
        l=50,
        r=50,
        t=120,
        b=50
    ),
    hoverdistance=50,
    spikedistance=-1,
    paper_bgcolor='white',
    dragmode='pan',
    xaxis=dict(fixedrange=False),
    yaxis=dict(fixedrange=True),
    xaxis2=dict(fixedrange=False),
    yaxis2=dict(fixedrange=True),
)

# 更新两个子图的坐标轴
for i in [1, 2]:
    fig.update_xaxes(
        title_text="",  # 移除"日期"文字
        row=i, 
        col=1, 
        showgrid=True, 
        gridwidth=1, 
        gridcolor='LightGray',
        showspikes=True,
        spikesnap='cursor',
        spikemode='across+marker',
        spikethickness=2,
        spikecolor='rgba(0,0,0,0.5)',
        spikedash='dash',
        showline=True,
        showticklabels=True,  # 显示日期数字
        fixedrange=False,
    )
    fig.update_yaxes(
        title_text="相对变化 (%)" if i == 1 else "收益率 (%)", 
        row=i, 
        col=1, 
        showgrid=True, 
        gridwidth=1, 
        gridcolor='LightGray',
        showspikes=False,
        showline=True,
        showticklabels=True,
        fixedrange=True,  # 禁止y轴缩放
    )

# 更新三个子图的坐标轴
for i in [1, 2, 3]:
    fig.update_xaxes(
        title_text="",  # 移除"日期"文字
        row=i, 
        col=1, 
        showgrid=True, 
        gridwidth=1, 
        gridcolor='LightGray',
        showspikes=True,
        spikesnap='cursor',
        spikemode='across+marker',
        spikethickness=2,
        spikecolor='rgba(0,0,0,0.5)',
        spikedash='dash',
        showline=True,
        showticklabels=True,  # 显示日期数字
        fixedrange=False,
    )
    if i < 3:  # 前两个子图的y轴设置
        fig.update_yaxes(
            title_text="相对变化 (%)" if i == 1 else "收益率 (%)",
            row=i, col=1,
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray',
            showspikes=False,
            showline=True,
            showticklabels=True,
            fixedrange=True,
        )
    else:  # 第三个子图的双Y轴设置
        # 左Y轴（美债规模）
        fig.update_yaxes(
            title_text="规模（万亿美元）",
            row=3, col=1,
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray',
            showspikes=False,
            showline=True,
            showticklabels=True,
            fixedrange=True,
            secondary_y=False,
        )
        # 右Y轴（债务占比）
        fig.update_yaxes(
            title_text="占GDP比重 (%)",
            row=3, col=1,
            showgrid=False,
            showline=True,
            showticklabels=True,
            fixedrange=True,
            secondary_y=True,
        )

# 显示图表
fig.show()