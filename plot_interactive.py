import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 读取数据
data_file = 'treasury_yields.csv'
data = pd.read_csv(data_file, index_col=0, parse_dates=True)

# 创建交互式图表
fig = px.line(data, 
              title='美国国债收益率曲线（2000-2025）',
              labels={'value': '收益率 (%)', 
                     'index': '日期',
                     'variable': '期限'},
              template='plotly_white')

# 添加重大事件标记
events = {
    '2008-09-15': '雷曼破产',
    '2020-03-23': '美联储无限QE',
    '2022-03-16': '加息周期启动'
}

# 添加垂直线和标注
for date, label in events.items():
    fig.add_vline(x=date, line_dash="dash", line_color="red", opacity=0.5)
    fig.add_annotation(x=date, 
                      y=data.max().max(),
                      text=label,
                      showarrow=True,
                      arrowhead=1)

# 更新布局
fig.update_layout(
    hovermode='x unified',
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ),
    font=dict(size=12)
)

# 显示图表
fig.show()