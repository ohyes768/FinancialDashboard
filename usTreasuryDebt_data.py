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

# 设置数据文件路径
data_file = 'treasury_debt.csv'

# 尝试从文件加载数据，如果文件不存在则从 FRED 获取
try:
    print("正在从本地文件加载数据...")
    data = pd.read_csv(data_file, index_col=0, parse_dates=True)
    
    # 检查数据是否需要更新
    last_date = pd.to_datetime(data.index[-1]).normalize()
    end = end.normalize()
    
    if (last_date + pd.Timedelta(days=1)) < end:
        try:
            print(f"检测到需要更新的数据（{last_date.strftime('%Y-%m-%d')} 至 {end.strftime('%Y-%m-%d')}）...")
            # 获取新数据
            new_data = web.DataReader('GFDEBTN', 'fred', last_date + pd.Timedelta(days=1), end)
            if not new_data.empty:
                # 合并新旧数据
                data = pd.concat([data, new_data])
                data = data[~data.index.duplicated(keep='last')]
                # 保存更新后的数据
                data.to_csv(data_file)
                print("数据已更新并保存到本地文件")
            else:
                print("没有新的数据需要更新")
        except Exception as e:
            print(f"更新数据时发生错误: {e}")
            print("使用已有的最新数据继续...")
            end = last_date

except FileNotFoundError:
    print("本地文件不存在，从 FRED 获取数据...")
    data = web.DataReader('GFDEBTN', 'fred', start, end)
    # 保存数据到 CSV 文件
    data.to_csv(data_file)
    print("数据已保存到本地文件")

# 填充缺失值（向前填充）
data = data.ffill()

# 将数据单位从百万美元转换为万亿美元
data = data / 1_000_000

# 绘制图表
plt.figure(figsize=(12,6))
plt.plot(data.index, data['GFDEBTN'], label='美国国债总规模', linewidth=1.5)

plt.title('美国国债总规模（2000-2025）', fontsize=14)
plt.xlabel('日期', fontsize=12)
plt.ylabel('规模（万亿美元）', fontsize=12)
plt.legend(fontsize=10)
plt.grid(alpha=0.3)

# 标记重大事件
events = {
    '2008-09-15': '雷曼破产',
    '2020-03-23': '新冠疫情救助',
    '2022-03-16': '加息周期启动'
}

for date, label in events.items():
    plt.axvline(pd.to_datetime(date), color='red', linestyle='--', linewidth=1)
    plt.text(pd.to_datetime(date), data['GFDEBTN'].max(), label, rotation=90, verticalalignment='top')

plt.show()