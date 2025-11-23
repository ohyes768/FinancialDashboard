# tgaHibor.py
from fredapi import Fred
import pandas as pd
import matplotlib.pyplot as plt
import platform
import requests
import json
from datetime import datetime, timedelta
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

# 初始化Fred对象，传入你的API Key
fred = Fred(api_key='8ecbb41e142454c0ce3ada51ebb489a8')

# 设置数据文件路径
tga_hibor_file = os.path.join(data_dir, 'tga_hibor_data.csv')  # 保存到data目录

# 设置起止时间
end = pd.to_datetime('today') - pd.Timedelta(days=2)  # 先计算结束时间
start = pd.to_datetime('2020-01-01')

# HKMA API URL
hkma_api_url = "https://api.hkma.gov.hk/public/market-data-and-statistics/daily-monetary-statistics/daily-figures-interbank-liquidity"

def fetch_hkma_hibor_data(start_date, end_date):
    """
    从HKMA API一次性获取指定时间段内的HIBOR数据
    """
    try:
        # 构造请求参数，一次性获取整个时间段的数据
        params = {
            'from': start_date.strftime('%Y%m%d'),
            'to': end_date.strftime('%Y%m%d')
        }
        
        print(f"正在从HKMA获取 {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')} 的HIBOR数据...")
        response = requests.get(hkma_api_url, params=params, timeout=30)  # 增加超时时间
        
        if response.status_code == 200:
            data = response.json()
            
            # 检查是否有数据
            if data.get('result', {}).get('records'):
                records = data['result']['records']
                hibor_data = []
                
                for record in records:
                    # 提取日期和隔夜HIBOR利率
                    date_str = record.get('end_of_date')
                    hibor_value = record.get('hibor_overnight')
                    
                    if date_str and hibor_value is not None:
                        # 将日期字符串转换为datetime对象
                        date_obj = pd.to_datetime(date_str, format='%Y-%m-%d')
                        hibor_data.append({
                            'date': date_obj,
                            'hibor_overnight': float(hibor_value)
                        })
                
                if hibor_data:
                    df = pd.DataFrame(hibor_data)
                    df = df.set_index('date').sort_index()
                    print(f"✅ 成功获取 {len(df)} 条HIBOR数据")
                    return df
                else:
                    print("⚠️ HKMA返回的数据格式不符合预期")
                    return pd.DataFrame()
            else:
                print("⚠️ HKMA API未返回有效数据")
                return pd.DataFrame()
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ 获取HIBOR数据时出错: {e}")
        return pd.DataFrame()

def get_tga_data(observation_start, observation_end):
    """
    获取TGA账户余额数据，使用WTREGEN代码
    """
    try:
        print("尝试获取 TGA 数据 (代码: WTREGEN)...")
        tga_data = fred.get_series('WTREGEN', observation_start=observation_start, observation_end=observation_end)
        if not tga_data.empty:
            print(f"✅ 成功获取 WTREGEN 数据，共 {len(tga_data)} 条记录")
            return tga_data
        else:
            print("⚠️ WTREGEN 数据为空")
    except Exception as e:
        print(f"❌ 获取 WTREGEN 失败: {e}")
    
    print("❌ TGA数据获取失败，返回空序列")
    return pd.Series(dtype='float64')

# 尝试从文件加载数据，如果文件不存在则从 FRED 和 HKMA 获取
try:
    print("正在从本地文件加载数据...")
    combined_data = pd.read_csv(tga_hibor_file, index_col=0, parse_dates=True)
    
    # 检查数据是否需要更新
    last_date = pd.to_datetime(combined_data.index[-1]).normalize()  # 标准化到日期，去除时间部分
    end = end.normalize()  # 标准化结束日期，去除时间部分
    
    if (last_date + pd.Timedelta(days=1)) < end:  # 如果最后日期加1天仍小于结束日期，则需要更新
        try:
            print(f"检测到需要更新的数据（{last_date.strftime('%Y-%m-%d')} 至 {end.strftime('%Y-%m-%d')}）...")
            
            # 获取新数据 - 一次性获取整个时间段的数据
            new_hibor_df = fetch_hkma_hibor_data(last_date + pd.Timedelta(days=1), end)
            new_tga = get_tga_data(last_date + pd.Timedelta(days=1), end)
            
            # 创建新数据DataFrame
            if not new_hibor_df.empty:
                new_data_dict = {
                    'HIBOR': new_hibor_df['hibor_overnight'],
                    'TGA': new_tga
                }
                new_data = pd.DataFrame(new_data_dict)
                
                if not new_data.empty:
                    # 合并新旧数据
                    combined_data = pd.concat([combined_data, new_data])
                    combined_data = combined_data[~combined_data.index.duplicated(keep='last')]  # 删除重复的日期，保留最新的数据
                    # 保存更新后的数据
                    combined_data.to_csv(tga_hibor_file)
                    print("数据已更新并保存到本地文件")
                else:
                    print("没有新的数据需要更新")
            else:
                print("未能获取新的HIBOR数据")
        except Exception as e:
            print(f"更新数据时发生错误: {e}")
            print("使用已有的最新数据继续...")
            
except FileNotFoundError:
    print("本地文件不存在，从 FRED 和 HKMA 获取数据...")
    
    # 从HKMA一次性获取HIBOR数据
    hibor_df = fetch_hkma_hibor_data(start, end)
    
    # 从FRED获取TGA数据
    tga_data = get_tga_data(start, end)
    
    # 创建DataFrame
    if not hibor_df.empty:
        combined_data = pd.DataFrame({
            'HIBOR': hibor_df['hibor_overnight'],
            'TGA': tga_data
        })
        
        # 保存数据到 CSV 文件
        combined_data.to_csv(tga_hibor_file)
        print("数据已保存到本地文件")
    else:
        print("未能获取HIBOR数据，程序终止")
        exit()

# 填充缺失值（向前填充）
combined_data = combined_data.ffill()

# 绘制图表
fig, ax1 = plt.subplots(figsize=(12, 6))

# 绘制HIBOR数据
color = 'tab:blue'
ax1.set_xlabel('日期', fontsize=12)
ax1.set_ylabel('HIBOR (%)', color=color, fontsize=12)
ax1.plot(combined_data.index, combined_data['HIBOR'], color=color, label='HIBOR', linewidth=1.5)
ax1.tick_params(axis='y', labelcolor=color)

# 创建共享x轴的第二个y轴用于TGA数据
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('TGA账户余额 (十亿美元)', color=color, fontsize=12)
ax2.plot(combined_data.index, combined_data['TGA'], color=color, label='TGA', linewidth=1.5)
ax2.tick_params(axis='y', labelcolor=color)

# 添加标题和网格
plt.title('香港银行同业拆息(HIBOR)与美国财政部TGA账户余额', fontsize=14)
fig.tight_layout()
ax1.grid(alpha=0.3)

# 标记重大事件
events = {
    '2020-03-23': '美联储无限QE',
    '2022-03-16': '加息周期启动'
}

for date, label in events.items():
    event_date = pd.to_datetime(date)
    if not combined_data.empty and len(combined_data) > 0:
        max_hibor = combined_data['HIBOR'].max() if not combined_data['HIBOR'].empty else 0
        if pd.notna(max_hibor):
            ax1.axvline(event_date, color='green', linestyle='--', linewidth=1)
            ax1.text(event_date, max_hibor, label, rotation=90, verticalalignment='top')

plt.tight_layout()
plt.show()