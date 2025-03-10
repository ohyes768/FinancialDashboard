# 使用 pandas_datareader 从 FRED 获取数据
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # MacOS 系统可用的中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 设置起止时间
end = pd.to_datetime('today') - pd.Timedelta(days=2)  # 先计算结束时间
start = pd.to_datetime('2000-01-01')

# # 确保开始日期早于结束日期
# if start >= end:
#     print("警告：开始日期不能晚于结束日期，已自动调整...")
#     start = end - pd.Timedelta(days=365*5)  # 如果日期有问题，默认获取最近5年的数据

# 从FRED获取数据（需安装 pandas_datareader）
series_codes = {
    '3个月': 'DGS3MO',
    '2年': 'DGS2',
    '10年': 'DGS10'
}

# 设置数据文件路径
data_file = 'treasury_yields.csv'

# 尝试从文件加载数据，如果文件不存在则从 FRED 获取
try:
    print("正在从本地文件加载数据...")
    data = pd.read_csv(data_file, index_col=0, parse_dates=True)
    data.columns = series_codes.keys()
    
    # 检查数据是否需要更新
    last_date = pd.to_datetime(data.index[-1]).normalize()  # 标准化到日期，去除时间部分
    end = end.normalize()  # 标准化结束日期，去除时间部分
    
    if (last_date + pd.Timedelta(days=1)) < end:  # 如果最后日期加1天仍小于结束日期，则需要更新
        try:
            print(f"检测到需要更新的数据（{last_date.strftime('%Y-%m-%d')} 至 {end.strftime('%Y-%m-%d')}）...")
            # 获取新数据
            new_data = web.DataReader(list(series_codes.values()), 'fred', last_date + pd.Timedelta(days=1), end)
            if not new_data.empty:
                new_data.columns = series_codes.keys()
                # 合并新旧数据
                data = pd.concat([data, new_data])
                data = data[~data.index.duplicated(keep='last')]  # 删除重复的日期，保留最新的数据
                # 保存更新后的数据
                data.to_csv(data_file)
                print("数据已更新并保存到本地文件")
            else:
                print("没有新的数据需要更新")
        except Exception as e:
            print(f"更新数据时发生错误: {e}")
            print("使用已有的最新数据继续...")
            end = last_date
        new_data.columns = series_codes.keys()
        
        # 合并新旧数据
        data = pd.concat([data, new_data])
        data = data[~data.index.duplicated(keep='last')]  # 删除重复的日期，保留最新的数据
        
        # 保存更新后的数据
        data.to_csv(data_file)
        print("数据已更新并保存到本地文件")
except FileNotFoundError:
    print("本地文件不存在，从 FRED 获取数据...")
    data = web.DataReader(list(series_codes.values()), 'fred', start, end)
    data.columns = series_codes.keys()
    # 保存数据到 CSV 文件
    data.to_csv(data_file)
    print("数据已保存到本地文件")

# 填充缺失值（向前填充）
data = data.ffill()

# 绘制图表
plt.figure(figsize=(12,6))
for col in data.columns:
    plt.plot(data.index, data[col], label=col, linewidth=1.5)

plt.title('美国国债收益率曲线（2000-2025）', fontsize=14)  # 更新了年份范围
plt.xlabel('日期', fontsize=12)
plt.ylabel('收益率 (%)', fontsize=12)
plt.legend(fontsize=10)
plt.grid(alpha=0.3)

# 标记重大事件（例如2008金融危机、2020疫情）
events = {
    '2008-09-15': '雷曼破产',
    '2020-03-23': '美联储无限QE',
    '2022-03-16': '加息周期启动'
}

for date, label in events.items():
    plt.axvline(pd.to_datetime(date), color='red', linestyle='--', linewidth=1)
    plt.text(pd.to_datetime(date), data.max().max(), label, rotation=90, verticalalignment='top')

plt.show()
