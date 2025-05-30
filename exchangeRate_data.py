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

# 设置起止时间
end = pd.to_datetime('today') - pd.Timedelta(days=2)  # 先计算结束时间
start = pd.to_datetime('2000-01-01')

# 从FRED获取数据（需安装 pandas_datareader）
series_codes = {
    '美元指数': 'DTWEXBGS',  # 美元指数
    '美元兑人民币': 'DEXCHUS',  # USD/CNY汇率
    '美元兑日元': 'DEXJPUS',   # USD/JPY汇率
    '美元兑欧元': 'DEXUSEU'    # USD/EUR汇率
}

# 设置数据文件路径
data_file = 'exchange_rates.csv'

# 尝试从文件加载数据，如果文件不存在则从 FRED 获取
try:
    print("正在从本地文件加载数据...")
    data = pd.read_csv(data_file, index_col=0, parse_dates=True)
    data.columns = series_codes.keys()
    
    # 将所有数据统一为2位小数
    data = data.round(2)
    
    # 检查数据完整性
    date_range = pd.date_range(start=data.index[0], end=data.index[-1], freq='B')
    missing_dates = date_range.difference(data.index)
    
    if len(missing_dates) > 0:
        print(f"检测到{len(missing_dates)}个交易日数据缺失，正在补充...")
        try:
            # 获取缺失日期的数据
            missing_data = web.DataReader(list(series_codes.values()), 'fred', 
                                        missing_dates[0], missing_dates[-1])
            if not missing_data.empty:
                missing_data.columns = series_codes.keys()
                missing_data = missing_data.round(2)
                # 合并数据
                data = pd.concat([data, missing_data])
                data = data.sort_index()
                data = data[~data.index.duplicated(keep='last')]
                # 保存更新后的数据
                data.to_csv(data_file, float_format='%.2f')
                print("缺失数据已补充并保存")
        except Exception as e:
            print(f"补充缺失数据时发生错误: {e}")
    
    # 检查是否需要更新最新数据
    last_date = pd.to_datetime(data.index[-1]).normalize()
    end = end.normalize()
    
    if (last_date + pd.Timedelta(days=1)) < end:
        try:
            print(f"检测到需要更新的数据（{last_date.strftime('%Y-%m-%d')} 至 {end.strftime('%Y-%m-%d')}）...")
            # 获取新数据
            new_data = web.DataReader(list(series_codes.values()), 'fred', last_date + pd.Timedelta(days=1), end)
            if not new_data.empty:
                new_data.columns = series_codes.keys()
                # 将新数据也统一为2位小数
                new_data = new_data.round(2)
                # 合并新旧数据
                data = pd.concat([data, new_data])
                data = data[~data.index.duplicated(keep='last')]
                # 保存更新后的数据
                data.to_csv(data_file, float_format='%.2f')  # 保存时指定格式为2位小数
                print("数据已更新并保存到本地文件")
            else:
                print("没有新的数据需要更新")
        except Exception as e:
            print(f"更新数据时发生错误: {e}")
            print("使用已有的最新数据继续...")
            end = last_date

except FileNotFoundError:
    print("本地文件不存在，从 FRED 获取数据...")
    data = web.DataReader(list(series_codes.values()), 'fred', start, end)
    data.columns = series_codes.keys()
    # 将数据统一为2位小数
    data = data.round(2)
    # 保存数据到 CSV 文件，指定2位小数格式
    data.to_csv(data_file, float_format='%.2f')
    print("数据已保存到本地文件")

# 数据处理：转换汇率和标准化
# 1. 转换汇率方向
data['美元兑欧元'] = 1 / data['美元兑欧元']  # 转换为 USD/EUR

# 2. 计算百分比变化（相对于基期的变化）
base_date = '2000-01-03'  # 使用2000年初作为基期
for col in data.columns:
    base_value = data.loc[base_date:, col].iloc[0]  # 获取基期值
    data[col] = (data[col] - base_value) / base_value * 100  # 转换为相对基期的百分比变化

# 填充缺失值（向前填充）
data = data.ffill()

# 绘制图表
plt.figure(figsize=(12,6))
for col in data.columns:
    plt.plot(data.index, data[col], label=col, linewidth=1.5)

plt.title('主要汇率相对变化走势（2000年至今，%）', fontsize=14)
plt.xlabel('日期', fontsize=12)
plt.ylabel('相对2000年初的变化（%）', fontsize=12)
plt.legend(fontsize=10)
plt.grid(alpha=0.3)
plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)  # 添加零线

# 标记重大事件
events = {
    '2005-07-21': '人民币汇改',
    '2008-09-15': '雷曼破产',
    '2015-08-11': '811汇改',
    '2022-03-16': '美联储加息周期启动'
}

# 添加重要事件标记
for date, label in events.items():
    event_date = pd.to_datetime(date)
    plt.axvline(event_date, color='red', linestyle='--', linewidth=1)
    plt.text(event_date, data.max().max(), label,
            rotation=90, verticalalignment='top', fontsize=8)

plt.tight_layout()
plt.show()