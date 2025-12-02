"""
辅助函数模块 - 提供通用的工具函数
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os


def load_tushare_token():
    """加载Tushare API Token"""
    from .config import TUSHARE_TOKEN_FILE
    
    try:
        with open(TUSHARE_TOKEN_FILE, 'r', encoding='utf-8') as f:
            token = f.read().strip()
        return token
    except FileNotFoundError:
        raise FileNotFoundError(f"请在 {TUSHARE_TOKEN_FILE} 文件中配置Tushare API Token")


def clean_stock_data(df):
    """
    清洗股票数据
    
    Parameters:
    df: DataFrame - 原始股票数据
    
    Returns:
    DataFrame - 清洗后的数据
    """
    # 数据类型转换
    numeric_cols = ['open', 'high', 'low', 'close', 'vol']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 删除空值和重复值
    df = df.dropna()
    df = df.drop_duplicates()
    
    # 删除异常值
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    
    return df


def format_date_for_tushare(date_str):
    """
    将日期格式化为Tushare要求的YYYYMMDD格式
    
    Parameters:
    date_str: str - 输入日期字符串
    
    Returns:
    str - YYYYMMDD格式的日期字符串
    """
    if isinstance(date_str, str):
        # 移除可能的分隔符
        date_str = date_str.replace('-', '').replace('/', '')
        # 如果已经是YYYYMMDD格式，直接返回
        if len(date_str) == 8:
            return date_str
    
    # 其他格式转换
    try:
        if isinstance(date_str, str):
            date_obj = pd.to_datetime(date_str)
        else:
            date_obj = date_str
        return date_obj.strftime('%Y%m%d')
    except:
        return date_str


def ensure_directory_exists(path):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(path):
        os.makedirs(path)


def calculate_returns(prices):
    """
    计算收益率
    
    Parameters:
    prices: Series - 价格序列
    
    Returns:
    Series - 收益率序列
    """
    return prices.pct_change().dropna()


def identify_cross_signals(fast_line, slow_line):
    """
    识别金叉和死叉信号
    
    Parameters:
    fast_line: Series - 快线（短周期均线）
    slow_line: Series - 慢线（长周期均线）
    
    Returns:
    tuple: (golden_cross, death_cross) - 金叉信号和死叉信号的布尔序列
    """
    # 金叉：快线从下方穿越慢线
    golden_cross = (fast_line > slow_line) & (fast_line.shift(1) <= slow_line.shift(1))
    
    # 死叉：快线从上方穿越慢线
    death_cross = (fast_line < slow_line) & (fast_line.shift(1) >= slow_line.shift(1))
    
    return golden_cross, death_cross


def count_signals(signal_series):
    """
    统计信号出现次数
    
    Parameters:
    signal_series: Series - 布尔类型的信号序列
    
    Returns:
    int - 信号出现次数
    """
    return signal_series.sum()
