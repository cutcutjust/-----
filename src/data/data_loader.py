"""
数据获取模块 - 封装Tushare API调用，提供统一的数据获取接口
"""

import pandas as pd
import tushare as ts
import numpy as np
from datetime import datetime
import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.config import DEFAULT_STOCK_CODE, DEFAULT_START_DATE, DEFAULT_END_DATE
from utils.helpers import load_tushare_token, clean_stock_data, format_date_for_tushare


class StockDataLoader:
    """股票数据获取类"""
    
    def __init__(self):
        """初始化数据加载器"""
        self.token = load_tushare_token()
        ts.set_token(self.token)
        self.pro = ts.pro_api()
        
    def get_daily_data(self, ts_code=None, start_date=None, end_date=None):
        """
        获取股票日线数据
        
        Parameters:
        ts_code: str - 股票代码，默认为配置中的默认股票
        start_date: str - 开始日期，格式YYYYMMDD
        end_date: str - 结束日期，格式YYYYMMDD
        
        Returns:
        DataFrame - 股票日线数据
        """
        # 使用默认值
        if ts_code is None:
            ts_code = DEFAULT_STOCK_CODE
        if start_date is None:
            start_date = DEFAULT_START_DATE
        if end_date is None:
            end_date = DEFAULT_END_DATE
            
        # 格式化日期
        start_date = format_date_for_tushare(start_date)
        end_date = format_date_for_tushare(end_date)
        
        try:
            # 获取数据
            df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            
            if df.empty:
                raise ValueError(f"未获取到股票 {ts_code} 的数据，请检查股票代码和日期范围")
            
            # 数据预处理
            df = self._preprocess_data(df)
            
            print(f"成功获取股票 {ts_code} 数据，时间范围：{start_date} 到 {end_date}，共 {len(df)} 条记录")
            return df
            
        except Exception as e:
            print(f"获取股票数据失败：{str(e)}")
            raise e
    
    def get_stock_basic_info(self, ts_code):
        """
        获取股票基本信息
        
        Parameters:
        ts_code: str - 股票代码
        
        Returns:
        DataFrame - 股票基本信息
        """
        try:
            df = self.pro.stock_basic(ts_code=ts_code, fields='ts_code,symbol,name,area,industry,market')
            return df
        except Exception as e:
            print(f"获取股票基本信息失败：{str(e)}")
            return pd.DataFrame()
    
    def _preprocess_data(self, df):
        """
        数据预处理
        
        Parameters:
        df: DataFrame - 原始数据
        
        Returns:
        DataFrame - 预处理后的数据
        """
        # 日期转换和排序
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values('trade_date', ascending=True)
        df = df.set_index('trade_date')
        
        # 重命名列名，统一格式
        df = df.rename(columns={
            'open': 'Open',
            'high': 'High', 
            'low': 'Low',
            'close': 'Close',
            'vol': 'Volume'
        })
        
        # 选择核心列
        core_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df = df[core_columns].copy()
        
        # 数据清洗
        df = clean_stock_data(df)
        
        # 数据验证
        if len(df) < 30:
            raise ValueError(f"数据量不足，仅有 {len(df)} 条记录，建议至少30条以上")
        
        return df
    
    def get_multiple_timeframes(self, ts_code=None, start_date=None, end_date=None):
        """
        获取多时间周期数据（日线、周线、月线）
        
        Parameters:
        ts_code: str - 股票代码
        start_date: str - 开始日期
        end_date: str - 结束日期
        
        Returns:
        dict - 包含不同周期数据的字典
        """
        # 获取日线数据
        daily_data = self.get_daily_data(ts_code, start_date, end_date)
        
        # 转换为周线数据
        weekly_data = self._convert_to_weekly(daily_data)
        
        # 转换为月线数据
        monthly_data = self._convert_to_monthly(daily_data)
        
        return {
            'daily': daily_data,
            'weekly': weekly_data,
            'monthly': monthly_data
        }
    
    def _convert_to_weekly(self, daily_data):
        """将日线数据转换为周线数据"""
        weekly = daily_data.resample('W').agg({
            'Open': 'first',
            'High': 'max', 
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        return weekly
    
    def _convert_to_monthly(self, daily_data):
        """将日线数据转换为月线数据"""
        monthly = daily_data.resample('M').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min', 
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        return monthly


# 便捷函数
def get_stock_data(ts_code=DEFAULT_STOCK_CODE, start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE):
    """
    便捷函数：获取股票数据
    
    Parameters:
    ts_code: str - 股票代码
    start_date: str - 开始日期
    end_date: str - 结束日期
    
    Returns:
    DataFrame - 股票数据
    """
    loader = StockDataLoader()
    return loader.get_daily_data(ts_code, start_date, end_date)


if __name__ == "__main__":
    # 测试数据获取
    try:
        loader = StockDataLoader()
        
        # 获取默认股票数据
        df = loader.get_daily_data()
        print("数据获取成功！")
        print(f"数据形状：{df.shape}")
        print(f"日期范围：{df.index.min()} 到 {df.index.max()}")
        print("\n前5行数据：")
        print(df.head())
        
        # 获取股票基本信息
        info = loader.get_stock_basic_info(DEFAULT_STOCK_CODE)
        if not info.empty:
            print(f"\n股票信息：{info.iloc[0]['name']} ({info.iloc[0]['ts_code']})")
        
    except Exception as e:
        print(f"测试失败：{str(e)}")
