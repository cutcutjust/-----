"""
移动平均线系统模块 - 实现SMA、EMA计算和金叉死叉信号识别
对应作业要求1：移动平均线系统构建
"""

import pandas as pd
import numpy as np
import talib as tb
import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.config import MA_PERIODS
from utils.helpers import identify_cross_signals, count_signals


class MovingAverageSystem:
    """移动平均线系统类"""
    
    def __init__(self, data):
        """
        初始化移动平均线系统
        
        Parameters:
        data: DataFrame - 包含OHLCV数据的DataFrame
        """
        self.data = data.copy()
        self.close = data['Close'].values.astype(np.float64)
        self.ma_data = {}  # 存储计算的均线数据
        self.signals = {}  # 存储交易信号
        
    def calculate_sma(self, periods=None):
        """
        计算简单移动平均线(SMA)
        
        Parameters:
        periods: list - 均线周期列表，默认使用配置中的周期
        
        Returns:
        dict - 包含各周期SMA的字典
        """
        if periods is None:
            periods = MA_PERIODS['sma']
        
        sma_results = {}
        for period in periods:
            sma_values = tb.SMA(self.close, timeperiod=period)
            sma_results[f'SMA_{period}'] = pd.Series(sma_values, index=self.data.index)
            
        return sma_results
    
    def calculate_ema(self, periods=None):
        """
        计算指数移动平均线(EMA)
        
        Parameters:
        periods: list - 均线周期列表，默认使用配置中的周期
        
        Returns:
        dict - 包含各周期EMA的字典
        """
        if periods is None:
            periods = MA_PERIODS['ema']
        
        ema_results = {}
        for period in periods:
            ema_values = tb.EMA(self.close, timeperiod=period)
            ema_results[f'EMA_{period}'] = pd.Series(ema_values, index=self.data.index)
            
        return ema_results
    
    def calculate_all_ma(self):
        """计算所有移动平均线"""
        # 计算SMA
        sma_results = self.calculate_sma()
        self.ma_data.update(sma_results)
        
        # 计算EMA
        ema_results = self.calculate_ema()
        self.ma_data.update(ema_results)
        
        # 将结果添加到数据中
        for ma_name, ma_series in self.ma_data.items():
            self.data[ma_name] = ma_series
        
        return self.ma_data
    
    def identify_ma_cross_signals(self):
        """
        识别均线金叉死叉信号
        
        Returns:
        dict - 包含各种均线交叉信号的字典
        """
        cross_signals = {}
        
        # 确保均线已计算
        if not self.ma_data:
            self.calculate_all_ma()
        
        # 定义需要分析的均线对
        cross_pairs = [
            ('SMA_5', 'SMA_10'),   # 5日与10日均线
            ('SMA_5', 'SMA_20'),   # 5日与20日均线
            ('SMA_10', 'SMA_20'),  # 10日与20日均线
            ('SMA_20', 'SMA_60'),  # 20日与60日均线
            ('EMA_12', 'EMA_26'),  # 12日与26日EMA
        ]
        
        for fast_ma, slow_ma in cross_pairs:
            if fast_ma in self.ma_data and slow_ma in self.ma_data:
                fast_line = self.ma_data[fast_ma]
                slow_line = self.ma_data[slow_ma]
                
                golden_cross, death_cross = identify_cross_signals(fast_line, slow_line)
                
                pair_name = f"{fast_ma}_{slow_ma}"
                cross_signals[pair_name] = {
                    'golden_cross': golden_cross,
                    'death_cross': death_cross,
                    'golden_count': count_signals(golden_cross),
                    'death_count': count_signals(death_cross)
                }
        
        self.signals['cross_signals'] = cross_signals
        return cross_signals
    
    def calculate_cross_frequency_stats(self):
        """
        统计不同周期均线的交叉频率
        
        Returns:
        DataFrame - 交叉频率统计表
        """
        if 'cross_signals' not in self.signals:
            self.identify_ma_cross_signals()
        
        stats_data = []
        for pair_name, signals in self.signals['cross_signals'].items():
            stats_data.append({
                '均线组合': pair_name,
                '金叉次数': signals['golden_count'],
                '死叉次数': signals['death_count'],
                '总交叉次数': signals['golden_count'] + signals['death_count'],
                '数据天数': len(self.data),
                '平均交叉间隔(天)': len(self.data) / max(1, signals['golden_count'] + signals['death_count'])
            })
        
        stats_df = pd.DataFrame(stats_data)
        return stats_df
    
    def get_latest_ma_values(self):
        """
        获取最新的移动平均线数值
        
        Returns:
        dict - 最新的移动平均线数值
        """
        if not self.ma_data:
            self.calculate_all_ma()
        
        latest_values = {}
        for ma_name, ma_series in self.ma_data.items():
            latest_values[ma_name] = ma_series.iloc[-1] if not ma_series.isna().iloc[-1] else None
        
        return latest_values
    
    def get_ma_trend_analysis(self):
        """
        获取移动平均线趋势分析
        
        Returns:
        dict - 趋势分析结果
        """
        if not self.ma_data:
            self.calculate_all_ma()
        
        trend_analysis = {}
        current_price = self.data['Close'].iloc[-1]
        
        # 分析价格与各均线的关系
        price_vs_ma = {}
        for ma_name, ma_series in self.ma_data.items():
            latest_ma = ma_series.iloc[-1]
            if not np.isnan(latest_ma):
                price_vs_ma[ma_name] = {
                    'value': latest_ma,
                    'above_ma': current_price > latest_ma,
                    'difference_pct': ((current_price - latest_ma) / latest_ma) * 100
                }
        
        trend_analysis['price_vs_ma'] = price_vs_ma
        trend_analysis['current_price'] = current_price
        
        # 判断整体趋势
        above_count = sum(1 for info in price_vs_ma.values() if info['above_ma'])
        total_count = len(price_vs_ma)
        
        if above_count >= total_count * 0.7:
            trend_analysis['overall_trend'] = '多头排列'
        elif above_count <= total_count * 0.3:
            trend_analysis['overall_trend'] = '空头排列'
        else:
            trend_analysis['overall_trend'] = '震荡整理'
        
        return trend_analysis


def calculate_ma_system(data):
    """
    便捷函数：计算完整的移动平均线系统
    
    Parameters:
    data: DataFrame - 股票数据
    
    Returns:
    tuple: (ma_system, stats_df) - 移动平均线系统对象和统计数据
    """
    ma_system = MovingAverageSystem(data)
    ma_system.calculate_all_ma()
    ma_system.identify_ma_cross_signals()
    stats_df = ma_system.calculate_cross_frequency_stats()
    
    return ma_system, stats_df


if __name__ == "__main__":
    # 测试代码
    from data.data_loader import get_stock_data
    
    try:
        # 获取测试数据
        df = get_stock_data()
        print("开始测试移动平均线系统...")
        
        # 创建移动平均线系统
        ma_system = MovingAverageSystem(df)
        
        # 计算所有均线
        ma_data = ma_system.calculate_all_ma()
        print(f"计算了 {len(ma_data)} 条移动平均线")
        
        # 识别交叉信号
        cross_signals = ma_system.identify_ma_cross_signals()
        print(f"识别了 {len(cross_signals)} 组均线交叉信号")
        
        # 统计交叉频率
        stats_df = ma_system.calculate_cross_frequency_stats()
        print("\n均线交叉频率统计：")
        print(stats_df)
        
        # 趋势分析
        trend_analysis = ma_system.get_ma_trend_analysis()
        print(f"\n当前整体趋势：{trend_analysis['overall_trend']}")
        
        print("\n移动平均线系统测试完成！")
        
    except Exception as e:
        print(f"测试失败：{str(e)}")
