# 使用 fredapi 从 FRED 获取数据
import pandas as pd
from fredapi import Fred
import matplotlib.pyplot as plt
import platform
import os

# 确保data目录存在
data_dir = 'data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 根据操作系统设置中文字体
system = platform.system()
if system == 'Windows':
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # Windows系统可用的中文字体
elif system == 'Darwin':  # MacOS
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # MacOS系统可用的中文字体
else:  # Linux等其他系统
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']  # Linux常用中文字体

plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 设置FRED API密钥（请替换为您的实际API密钥）
api_key = '8ecbb41e142454c0ce3ada51ebb489a8'  # 请替换为您自己的API密钥
fred = Fred(api_key=api_key)

# 设置起止时间
end = pd.to_datetime('today') - pd.Timedelta(days=2)  # 先计算结束时间
start = pd.to_datetime('2000-01-01')

# FRED系列代码映射
series_codes = {
    '3个月': 'DGS3MO',
    '2年': 'DGS2',
    '10年': 'DGS10'
}

# 设置数据文件路径
data_file = os.path.join(data_dir, 'treasury_yields.csv')  # 保存到data目录

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
            new_data_dict = {}
            for name, code in series_codes.items():
                try:
                    series = fred.get_series(code, observation_start=last_date + pd.Timedelta(days=1), observation_end=end)
                    new_data_dict[name] = series
                except Exception as e:
                    print(f"获取 {name} ({code}) 数据时出错: {e}")
            
            if new_data_dict:
                new_data = pd.DataFrame(new_data_dict)
                if not new_data.empty:
                    # 合并新旧数据
                    data = pd.concat([data, new_data])
                    data = data[~data.index.duplicated(keep='last')]  # 删除重复的日期，保留最新的数据
                    # 保存更新后的数据
                    data.to_csv(data_file)
                    print("数据已更新并保存到本地文件")
                else:
                    print("没有新的数据需要更新")
            else:
                print("没有新的数据需要更新")
        except Exception as e:
            print(f"更新数据时发生错误: {e}")
            print("使用已有的最新数据继续...")
            end = last_date
            
except FileNotFoundError:
    print("本地文件不存在，从 FRED 获取数据...")
    # 从FRED获取数据
    data_dict = {}
    for name, code in series_codes.items():
        try:
            series = fred.get_series(code, observation_start=start, observation_end=end)
            data_dict[name] = series
            print(f"成功获取 {name} 数据，共 {len(series)} 条记录")
        except Exception as e:
            print(f"获取 {name} ({code}) 数据时出错: {e}")
            # 创建空序列作为占位符
            data_dict[name] = pd.Series(dtype='float64')
    
    data = pd.DataFrame(data_dict)
    data.columns = series_codes.keys()
    # 保存数据到 CSV 文件
    data.to_csv(data_file)
    print("数据已保存到本地文件")

# 填充缺失值（向前填充）
data = data.ffill()

# 绘制图表
plt.figure(figsize=(12, 6))
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
    event_date = pd.to_datetime(date)
    if not data.empty and len(data) > 0:
        max_yield = data.max().max() if not data.empty else 0
        if pd.notna(max_yield):
            plt.axvline(event_date, color='red', linestyle='--', linewidth=1)
            plt.text(event_date, max_yield, label, rotation=90, verticalalignment='top')

plt.tight_layout()
plt.show()