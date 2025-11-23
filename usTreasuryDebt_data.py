# 使用 usGDP.py 和 usDebt.py 的方法获取数据
import pandas as pd
import requests
from fredapi import Fred
import matplotlib.pyplot as plt
import platform
from datetime import datetime
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

# 设置数据文件路径
data_file = os.path.join(data_dir, 'treasury_debt_gdp.csv')  # 保存到data目录

def get_real_time_debt():
    """
    从美国财政部获取实时债务数据 (来自 usDebt.py)
    """
    try:
        # 方法1: 财政部API
        url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny"
        params = {
            'page[size]': 10000,
            'sort': '-record_date'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        # 转换为DataFrame
        debt_df = pd.DataFrame(data['data'])
        debt_df['record_date'] = pd.to_datetime(debt_df['record_date'])
        debt_df['tot_pub_debt_out_amt'] = pd.to_numeric(debt_df['tot_pub_debt_out_amt'])
        
        debt_df = debt_df.set_index('record_date').sort_index()
        print(f"最新债务数据: {debt_df['tot_pub_debt_out_amt'].iloc[-1]:,.0f} (日期: {debt_df.index[-1].strftime('%Y-%m-%d')})")
        
        return debt_df[['tot_pub_debt_out_amt']]
        
    except Exception as e:
        print(f"API获取失败: {e}")
        return get_debt_manual()

def get_debt_manual():
    """
    备用方法：从财政部网站表格数据解析 (来自 usDebt.py)
    """
    try:
        # 财政部每日债务数据页面
        debt_url = "https://www.treasurydirect.gov/NP/debt/current"
        
        # 使用pandas直接读取HTML表格
        tables = pd.read_html(debt_url)
        debt_data = tables[0]  # 通常是第一个表格
        
        print("从财政部网站获取的实时债务数据:")
        print(debt_data.head())
        
        return debt_data
    except Exception as e:
        print(f"网页获取也失败: {e}")
        return None

# 主程序逻辑
if __name__ == "__main__":
    try:
        print("正在从本地文件加载数据...")
        data = pd.read_csv(data_file, index_col=0, parse_dates=True)
        
        # 检查数据是否需要更新
        last_date = pd.to_datetime(data.index[-1]).normalize()
        end = end.normalize()  # 标准化结束日期，去除时间部分
        
        if (last_date + pd.Timedelta(days=1)) < end:
            print(f"检测到需要更新的数据（{last_date.strftime('%Y-%m-%d')} 至 {end.strftime('%Y-%m-%d')}）...")
            try:
                # 获取最新债务数据
                debt_data = get_real_time_debt()
                
                if debt_data is not None:
                    # 确保债务数据的时间索引是连续的
                    debt_data = debt_data.resample('D').ffill()  # 每日数据
                    
                    # 获取新的GDP数据
                    gdp_data = fred.get_series('GDP')
                    gdp_df = pd.DataFrame(gdp_data, columns=['GDP'])
                    gdp_df.index = pd.to_datetime(gdp_df.index)
                    
                    # 将GDP数据重采样为每日数据，使用前向填充
                    gdp_data_daily = gdp_df.resample('D').ffill()
                    
                    # 合并数据
                    combined_data = pd.merge(debt_data, gdp_data_daily, left_index=True, right_index=True, how='outer')
                    combined_data = combined_data.sort_index()
                    
                    # 只保留2000年之后的数据
                    combined_data = combined_data[combined_data.index >= '2000-01-01']
                    
                    # 计算债务占GDP比重（注意单位转换：GDP是十亿美元，债务是美元）
                    combined_data['债务占比'] = (combined_data['tot_pub_debt_out_amt'] / (combined_data['GDP'] * 1e9)) * 100
                    
                    # 合并新旧数据
                    data = pd.concat([data, combined_data])
                    data = data[~data.index.duplicated(keep='last')]  # 删除重复的日期，保留最新的数据
                    
                    # 保存到CSV
                    data.to_csv(data_file)
                    print("数据已更新并保存到本地文件")
                else:
                    print("获取最新债务数据失败，使用已有数据继续...")
            except Exception as e:
                print(f"更新数据时发生错误: {e}")
                print("使用已有的最新数据继续...")
        else:
            print("数据已是最新，无需更新")
            
    except FileNotFoundError:
        print("本地文件不存在，从源获取数据...")
        # 获取债务和GDP数据
        debt_data = get_real_time_debt()
        
        if debt_data is not None:
            # 确保债务数据的时间索引是连续的
            debt_data = debt_data.resample('D').ffill()  # 每日数据
            
            # 获取GDP数据
            gdp_data = fred.get_series('GDP')
            gdp_df = pd.DataFrame(gdp_data, columns=['GDP'])
            gdp_df.index = pd.to_datetime(gdp_df.index)
            
            # 将GDP数据重采样为每日数据，使用前向填充
            gdp_data_daily = gdp_df.resample('D').ffill()
            
            # 合并数据
            data = pd.merge(debt_data, gdp_data_daily, left_index=True, right_index=True, how='outer')
            data = data.sort_index()
            
            # 只保留2000年之后的数据
            data = data[data.index >= '2000-01-01']
            
            # 计算债务占GDP比重（注意单位转换：GDP是十亿美元，债务是美元）
            data['债务占比'] = (data['tot_pub_debt_out_amt'] / (data['GDP'] * 1e9)) * 100
            
            # 保存到CSV
            data.to_csv(data_file)
            print("数据已保存到本地文件")
        else:
            print("无法获取数据，程序退出")
            exit()

    # 数据处理 - 只保留2000年之后的数据
    data = data[data.index >= '2000-01-01']
    data = data.ffill()

    # 创建两个子图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # 第一个子图：债务总额
    ax1.plot(data.index, data['tot_pub_debt_out_amt']/1e12, label='美国国债总规模', linewidth=1.5)
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
        ax1.text(event_date, (data['tot_pub_debt_out_amt']/1e12).max(), label, rotation=90, verticalalignment='top')
        # 在债务比重图中标记
        ax2.axvline(event_date, color='red', linestyle='--', linewidth=1)
        ax2.text(event_date, data['债务占比'].max(), label, rotation=90, verticalalignment='top')

    plt.tight_layout()
    plt.show()