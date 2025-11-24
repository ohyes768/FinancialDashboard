# fastapi_dashboard.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import uvicorn
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_dashboard.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
data_dir = os.path.join(os.path.dirname(__file__), 'data')

app = FastAPI(title="Financial Dashboard", description="金融数据可视化仪表板")

# 挂载静态文件目录（如果需要）
app.mount("/static", StaticFiles(directory="static"), name="static")

def create_financial_chart():
    """
    创建金融数据图表，逻辑与 plot_interactive_tab.py 保持一致
    """
    logger.info("开始创建金融数据图表")
    
    # 读取汇率数据
    exchange_file = os.path.join(data_dir, 'exchange_rates.csv')
    try:
        exchange_data = pd.read_csv(exchange_file, index_col=0, parse_dates=True)
        logger.info(f"成功读取汇率数据，包含 {len(exchange_data)} 条记录")
    except Exception as e:
        logger.error(f"读取汇率数据失败: {str(e)}")
        raise
    
    # 读取美债收益率数据
    treasury_file = os.path.join(data_dir, 'treasury_yields.csv')
    try:
        treasury_data = pd.read_csv(treasury_file, index_col=0, parse_dates=True)
        logger.info(f"成功读取美债收益率数据，包含 {len(treasury_data)} 条记录")
    except Exception as e:
        logger.error(f"读取美债收益率数据失败: {str(e)}")
        raise
    
    # 读取美债和GDP数据
    debt_gdp_file = os.path.join(data_dir, 'treasury_debt_gdp.csv')
    try:
        debt_gdp_data = pd.read_csv(debt_gdp_file, index_col=0, parse_dates=True)
        logger.info(f"成功读取美债和GDP数据，包含 {len(debt_gdp_data)} 条记录")
    except Exception as e:
        logger.error(f"读取美债和GDP数据失败: {str(e)}")
        raise
    
    # 读取TGA和HIBOR数据
    tga_hibor_file = os.path.join(data_dir, 'tga_hibor_data.csv')
    try:
        tga_hibor_data = pd.read_csv(tga_hibor_file, index_col=0, parse_dates=True)
        logger.info(f"成功读取TGA和HIBOR数据，包含 {len(tga_hibor_data)} 条记录")
    except Exception as e:
        logger.error(f"读取TGA和HIBOR数据失败: {str(e)}")
        raise
    
    # 处理汇率数据缺失值
    full_index = pd.date_range(start=exchange_data.index.min(), end=exchange_data.index.max(), freq='B')
    logger.info(f"生成完整时间索引，范围从 {full_index[0]} 到 {full_index[-1]}")
    
    exchange_data = exchange_data.reindex(full_index)
    exchange_data = exchange_data.interpolate(method='time')
    exchange_data = exchange_data.ffill().bfill()
    logger.info(f"汇率数据处理完成，最终包含 {len(exchange_data)} 条记录")
    
    # 处理美债数据缺失值
    treasury_data = treasury_data.reindex(full_index)
    treasury_data = treasury_data.interpolate(method='time')
    treasury_data = treasury_data.ffill().bfill()
    logger.info(f"美债数据处理完成，最终包含 {len(treasury_data)} 条记录")
    
    # 处理美债和GDP数据缺失值
    debt_gdp_data = debt_gdp_data.reindex(full_index)
    debt_gdp_data = debt_gdp_data.interpolate(method='time')
    debt_gdp_data = debt_gdp_data.ffill().bfill()
    logger.info(f"美债和GDP数据处理完成，最终包含 {len(debt_gdp_data)} 条记录")
    
    # 处理TGA和HIBOR数据缺失值
    tga_hibor_data = tga_hibor_data.reindex(full_index)
    tga_hibor_data = tga_hibor_data.interpolate(method='time')
    tga_hibor_data = tga_hibor_data.ffill().bfill()
    logger.info(f"TGA和HIBOR数据处理完成，最终包含 {len(tga_hibor_data)} 条记录")
    
    # 合并所有数据
    data = pd.concat([exchange_data, treasury_data, debt_gdp_data, tga_hibor_data], axis=1)
    logger.info(f"数据合并完成，最终数据包含 {len(data)} 条记录，{len(data.columns)} 列")
    
    # 创建带有四个子图的基础图形
    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=('汇率相对变化走势', '美债收益率走势', '美债规模、GDP规模及占比走势', 'TGA账户余额与HIBOR走势'),
        vertical_spacing=0.06,
        shared_xaxes=True,
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": True}],
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
    logger.info(f"当前日期: {current_date}")
    
    # 为每个时间范围创建数据
    for period, days in time_ranges.items():
        if days is None:
            period_data = data.copy()
        else:
            start_date = current_date - timedelta(days=days)
            period_data = data[data.index >= start_date].copy()
        
        # 计算相对变化
        if not period_data.empty:
            logger.info(f"处理时间范围 '{period}' 的数据，包含 {len(period_data)} 条记录")
            
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
                        visible=(period == '近3年'),
                        legendgroup='exchange',
                        showlegend=(period == '近3年'),
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
                        visible=(period == '近3年'),
                        legendgroup='treasury',
                        showlegend=(period == '近3年'),
                        legendgrouptitle_text="美债"
                    ),
                    row=2, col=1
                )

            # 添加美债规模曲线到第三个子图（左Y轴）
            fig.add_trace(
                go.Scatter(
                    x=period_data.index,
                    y=period_data['tot_pub_debt_out_amt'] / 1e12,  # 转换为万亿美元
                    name='美债规模',
                    line=dict(width=1.5, color='blue'),
                    visible=(period == '近3年'),
                    legendgroup='debt',
                    showlegend=(period == '近3年'),
                    legendgrouptitle_text="美债规模"
                ),
                row=3, col=1, secondary_y=False
            )
            
            # 添加GDP规模曲线到第三个子图（左Y轴）
            fig.add_trace(
                go.Scatter(
                    x=period_data.index,
                    y=period_data['GDP'] / 1000,  # 转换为万亿美元（GDP原始单位为十亿美元）
                    name='GDP规模',
                    line=dict(width=1.5, color='green'),
                    visible=(period == '近3年'),
                    legendgroup='gdp',
                    showlegend=(period == '近3年'),
                    legendgrouptitle_text="GDP规模"
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
                    visible=(period == '近3年'),
                    legendgroup='debt_ratio',
                    showlegend=(period == '近3年'),
                    legendgrouptitle_text="债务占比"
                ),
                row=3, col=1, secondary_y=True
            )
            
            # 添加TGA数据到第四个子图（左Y轴）
            fig.add_trace(
                go.Scatter(
                    x=period_data.index,
                    y=period_data['TGA'] / 1e6,  # 转换为万亿美元
                    name='TGA账户余额',
                    line=dict(width=1.5, color='purple'),
                    visible=(period == '近3年'),
                    legendgroup='tga',
                    showlegend=(period == '近3年'),
                    legendgrouptitle_text="TGA账户"
                ),
                row=4, col=1, secondary_y=False
            )
            
            # 添加HIBOR数据到第四个子图（右Y轴）
            fig.add_trace(
                go.Scatter(
                    x=period_data.index,
                    y=period_data['HIBOR'],
                    name='HIBOR',
                    line=dict(width=1.5, color='orange'),
                    visible=(period == '近3年'),
                    legendgroup='hibor',
                    showlegend=(period == '近3年'),
                    legendgrouptitle_text="HIBOR"
                ),
                row=4, col=1, secondary_y=True
            )
    
    # 更新按钮配置
    buttons = []
    exchange_trace_count = len(exchange_data.columns)
    treasury_trace_count = len(treasury_data.columns)
    debt_trace_count = 3  # 美债规模、GDP规模和占比三条线
    tga_hibor_trace_count = 2  # TGA和HIBOR两条线
    total_trace_count = exchange_trace_count + treasury_trace_count + debt_trace_count + tga_hibor_trace_count

    # 设置默认选中的时间范围
    default_period = '近3年'

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
                ],
                # 设置默认选中的按钮
                args2=[
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
                x=0.65,
                y=1.15,
                showactive=True,
                active=list(time_ranges.keys()).index(default_period),
                buttons=buttons
            ),
            dict(
                type="buttons",
                direction="right",
                x=0.85,
                y=1.15,
                showactive=False,
                buttons=[
                    dict(
                        args=[{'xaxis.autorange': True, 'yaxis.autorange': True,
                              'xaxis2.autorange': True, 'yaxis2.autorange': True,
                              'xaxis3.autorange': True, 'yaxis3.autorange': True,
                              'yaxis4.autorange': True,
                              'xaxis4.autorange': True, 'yaxis5.autorange': True}],
                        label="恢复默认视图",
                        method="relayout"
                    )
                ]
            )
        ]
    )

    # 添加读取事件文件的代码
    try:
        with open('event.txt', 'r', encoding='utf-8') as f:
            events = [line.strip().split(' ', 1) for line in f if line.strip()]
        logger.info(f"成功读取事件文件，包含 {len(events)} 个事件")
    except FileNotFoundError:
        events = []
        logger.warning("事件文件未找到，将不显示重大事件")
    except Exception as e:
        logger.error(f"读取事件文件失败: {str(e)}")
        events = []
    
    # 更新布局
    fig.update_layout(
        height=1200,
        width=1400,
        hovermode='x unified',
        showlegend=False,
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
            r=250,
            t=120,
            b=50
        ),
        hoverdistance=50,
        spikedistance=-1,
        paper_bgcolor='white',
        dragmode='zoom',
        modebar=dict(
            activecolor='#1f77b4',
            orientation='v',
            bgcolor='rgba(255,255,255,0.8)',
        ),
        xaxis=dict(fixedrange=False),
        yaxis=dict(fixedrange=True),
        xaxis2=dict(fixedrange=False),
        yaxis2=dict(fixedrange=True),
    )

    # 更新四个子图的坐标轴
    for i in [1, 2, 3, 4]:
        fig.update_xaxes(
            title_text="",
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
            showticklabels=True,
            fixedrange=False,
        )
        if i == 1:  # 第一个子图的y轴设置
            fig.update_yaxes(
                title_text="相对变化 (%)",
                row=i, col=1,
                showgrid=True,
                gridwidth=1,
                gridcolor='LightGray',
                showspikes=False,
                showline=True,
                showticklabels=True,
                fixedrange=True,
            )
        elif i == 2:  # 第二个子图的y轴设置
            fig.update_yaxes(
                title_text="收益率 (%)",
                row=i, col=1,
                showgrid=True,
                gridwidth=1,
                gridcolor='LightGray',
                showspikes=False,
                showline=True,
                showticklabels=True,
                fixedrange=True,
            )
        elif i == 3:  # 第三个子图的双Y轴设置
            # 左Y轴（美债规模和GDP规模）
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
        elif i == 4:  # 第四个子图的双Y轴设置
            # 左Y轴（TGA账户余额）
            fig.update_yaxes(
                title_text="TGA账户余额（万亿美元）",
                row=4, col=1,
                showgrid=True,
                gridwidth=1,
                gridcolor='LightGray',
                showspikes=False,
                showline=True,
                showticklabels=True,
                fixedrange=True,
                secondary_y=False,
            )
            # 右Y轴（HIBOR）
            fig.update_yaxes(
                title_text="HIBOR (%)",
                row=4, col=1,
                showgrid=False,
                showline=True,
                showticklabels=True,
                fixedrange=True,
                secondary_y=True,
            )

    # 添加事件列表注释
    if events:
        event_text = '<br>'.join([f"{date}: {desc}" for date, desc in events])
        fig.add_annotation(
            x=0.95,
            y=0.8,
            xref='paper',
            yref='paper',
            text=f"<b>重大事件</b><br><br>{event_text}",
            showarrow=False,
            font=dict(size=11),
            align='left',
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='LightGray',
            borderwidth=1,
            xanchor='left',
            yanchor='middle',
            width=280
        )
    
    logger.info("金融数据图表创建完成")
    return fig

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """
    主页路由，显示金融数据仪表板
    """
    try:
        logger.info("开始生成仪表板页面")
        
        # 创建图表
        fig = create_financial_chart()
        
        plotly_js_option = 'local'
        logger.info("统一使用local方式加载Plotly.js")
        
        # 将图表转换为HTML，根据环境选择加载方式
        chart_html = fig.to_html(
            include_plotlyjs=plotly_js_option,
            div_id='financial-chart',
            full_html=False  # 不生成完整的HTML文档
        )
        
        # 构建完整HTML页面
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>金融数据可视化仪表板</title>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .chart-container {{
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    padding: 20px;
                    margin-bottom: 20px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>金融数据可视化仪表板</h1>
                <p>实时展示汇率、美债、TGA账户和HIBOR等金融数据</p>
            </div>
            <div class="chart-container">
                {chart_html}
            </div>
            <div class="footer">
                <p>数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        logger.info("仪表板页面生成成功")
        return html_content
    except Exception as e:
        logger.error(f"生成仪表板页面时发生错误: {str(e)}", exc_info=True)
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>金融数据可视化仪表板 - 错误</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>发生错误</h1>
            <p>错误详情: {str(e)}</p>
            <p>请检查数据文件是否存在且格式正确。</p>
        </body>
        </html>
        """
        return error_html

@app.get("/health")
async def health_check():
    """
    健康检查端点
    """
    return {"status": "healthy", "message": "Financial Dashboard is running"}

if __name__ == "__main__":
    # 启动FastAPI应用，指定端口为8090
    uvicorn.run("fastapi_dashboard:app", host="0.0.0.0", port=8090, reload=True)