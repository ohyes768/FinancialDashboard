# 使用 pandas_datareader 从 FRED 获取数据
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import platform

# 根据操作系统设置中文字体
system = platform.system()
if system == 'Windows':
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # Windows系统可用的中文字体
elif system == 'Darwin':  # MacOS
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # MacOS系统可用的中文字体
else:  # Linux等其他系统
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']  # Linux常用中文字体

plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # MacOS 系统可用的中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 设置起止时间
end = pd.to_datetime('today') - pd.Timedelta(days=2)  # 先计算结束时间
start = pd.to_datetime('2000-01-01')

# 设置数据文件路径
data_file = 'treasury_and_gdp.csv'
series_codes = {
    '国债': 'GFDEBTN',
    'GDP': 'GDP'
}

# 尝试从文件加载数据
try:
    print("正在从本地文件加载数据...")
    data = pd.read_csv(data_file, index_col=0, parse_dates=True)
    # 不要覆盖原有的列名，删除这行：
    # data.columns = series_codes.keys()
    
    # 检查数据是否需要更新
    last_date = pd.to_datetime(data.index[-1]).normalize()
    end = end.normalize()
    
    if (last_date + pd.Timedelta(days=1)) < end:
        try:
            print(f"检测到需要更新的数据（{last_date.strftime('%Y-%m-%d')} 至 {end.strftime('%Y-%m-%d')}）...")
            # 获取新数据
            new_data = web.DataReader(list(series_codes.values()), 'fred', last_date + pd.Timedelta(days=1), end)
            if not new_data.empty:
                new_data.columns = series_codes.keys()
                # 只将国债数据转换为万亿美元
                new_data['国债'] = new_data['国债'] / 1_000  # 十亿美元转万亿美元
                # 合并新旧数据
                data = pd.concat([data, new_data])
                data = data[~data.index.duplicated(keep='last')]
                # 计算债务占GDP比重
                data['债务占比'] = (data['国债'] / data['GDP']) * 100
                # 保存更新后的数据
                data.to_csv(data_file)
                print("数据已更新并保存到本地文件")
        except Exception as e:
            print(f"更新数据时发生错误: {e}")
            end = last_date

except FileNotFoundError:
    print("本地文件不存在，从 FRED 获取数据...")
    data = web.DataReader(list(series_codes.values()), 'fred', start, end)
    data.columns = series_codes.keys()
    # 只将国债数据转换为万亿美元
    data['国债'] = data['国债'] / 1_000  # 十亿美元转万亿美元
    # 计算债务占GDP比重
    data['债务占比'] = (data['国债'] / data['GDP']) * 100
    # 保存数据到 CSV 文件
    data.to_csv(data_file)
    print("数据已保存到本地文件")

# 数据处理
data = data.ffill()

# 创建两个子图
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# 第一个子图：债务总额
ax1.plot(data.index, data['国债'], label='美国国债总规模', linewidth=1.5)
ax1.set_title('美国国债总规模（2000-2025）', fontsize=14)
ax1.set_xlabel('日期', fontsize=12)
ax1.set_ylabel('规模（万亿美元）', fontsize=12)
ax1.legend(fontsize=10)
ax1.grid(alpha=0.3)

# 第二个子图：债务占GDP比重
ax2.plot(data.index, data['债务占比'], label='国债占GDP比重', linewidth=1.5, color='orange')
ax2.set_title('美国国债占GDP比重', fontsize=14)
ax2.set_xlabel('日期', fontsize=12)
ax2.set_ylabel('占比（%）', fontsize=12)
ax2.legend(fontsize=10)
ax2.grid(alpha=0.3)

# 在两个图中都标记重大事件
events = {
    '2008-09-15': '雷曼破产',
    '2020-03-23': '新冠疫情救助',
    '2022-03-16': '加息周期启动'
}

for date, label in events.items():
    event_date = pd.to_datetime(date)
    # 在债务总额图中标记
    ax1.axvline(event_date, color='red', linestyle='--', linewidth=1)
    ax1.text(event_date, data['国债'].max(), label, rotation=90, verticalalignment='top')
    # 在债务比重图中标记
    ax2.axvline(event_date, color='red', linestyle='--', linewidth=1)
    ax2.text(event_date, data['债务占比'].max(), label, rotation=90, verticalalignment='top')

plt.tight_layout()
plt.show()