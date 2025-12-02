"""
KDJ与RSI指标模块 - 实现KDJ和RSI指标计算和超买超卖分析
对应作业要求5和6：KDJ与RSI指标比较 + KDJ超买超卖统计
"""

import pandas as pd
import numpy as np
import talib as tb
import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.config import KDJ_CONFIG, RSI_CONFIG
from utils.helpers import calculate_returns


class KDJIndicator:
    """KDJ指标类"""
    
    def __init__(self, data):
        """
        初始化KDJ指标
        
        Parameters:
        data: DataFrame - 包含OHLCV数据的DataFrame
        """
        self.data = data.copy()
        self.high = data['High'].values.astype(np.float64)
        self.low = data['Low'].values.astype(np.float64)
        self.close = data['Close'].values.astype(np.float64)
        self.kdj_data = {}
        
    def calculate_kdj(self, fastk_period=None, slowk_period=None, slowd_period=None):
        """
        计算KDJ指标
        
        Parameters:
        fastk_period: int - Fast %K周期，默认9
        slowk_period: int - Slow %K周期，默认3
        slowd_period: int - Slow %D周期，默认3
        
        Returns:
        dict - 包含K、D、J值的字典
        """
        if fastk_period is None:
            fastk_period = KDJ_CONFIG['fastk_period']
        if slowk_period is None:
            slowk_period = KDJ_CONFIG['slowk_period']
        if slowd_period is None:
            slowd_period = KDJ_CONFIG['slowd_period']
        
        # 使用TA-Lib计算随机指标K和D
        k_values, d_values = tb.STOCH(
            self.high, self.low, self.close,
            fastk_period=fastk_period,
            slowk_period=slowk_period,
            slowk_matype=0,  # SMA
            slowd_period=slowd_period,
            slowd_matype=0   # SMA
        )
        
        # 计算J值：J = 3K - 2D
        j_values = 3 * k_values - 2 * d_values
        
        self.kdj_data = {
            'K': pd.Series(k_values, index=self.data.index),
            'D': pd.Series(d_values, index=self.data.index),
            'J': pd.Series(j_values, index=self.data.index)
        }
        
        # 添加到原数据中
        for key, series in self.kdj_data.items():
            self.data[key] = series
        
        return self.kdj_data
    
    def analyze_overbought_oversold(self, days=120):
        """
        分析KDJ超买超卖情况
        
        Parameters:
        days: int - 分析的交易日数量，默认120天
        
        Returns:
        dict - 超买超卖分析结果
        """
        if not self.kdj_data:
            self.calculate_kdj()
        
        # 获取最近指定天数的数据
        j_values = self.kdj_data['J'].tail(days)
        
        # 超买区：J > 100
        overbought_condition = j_values > 100
        # 超卖区：J < 0  
        oversold_condition = j_values < 0
        
        # 统计进入超买超卖区域的次数
        overbought_entries = self._count_entries(overbought_condition)
        oversold_entries = self._count_entries(oversold_condition)
        
        analysis_result = {
            'analysis_days': days,
            'overbought_count': overbought_entries,
            'oversold_count': oversold_entries,
            'overbought_condition': overbought_condition,
            'oversold_condition': oversold_condition
        }
        
        return analysis_result
    
    def _count_entries(self, condition_series):
        """
        计算进入某个区域的次数（从False变为True的次数）
        
        Parameters:
        condition_series: Series - 布尔条件序列
        
        Returns:
        int - 进入次数
        """
        # 填充NaN值，从不满足条件到满足条件的转换点
        condition_series = condition_series.fillna(False)
        prev_condition = condition_series.shift(1).fillna(False)
        entries = condition_series & (~prev_condition)
        return entries.sum()
    
    def calculate_overbought_returns(self, days=120, holding_days=5):
        """
        计算超买后指定天数的平均收益率
        
        Parameters:
        days: int - 分析的交易日数量
        holding_days: int - 持有天数
        
        Returns:
        dict - 收益率分析结果
        """
        if not self.kdj_data:
            self.calculate_kdj()
        
        # 获取最近指定天数的数据
        analysis_data = self.data.tail(days + holding_days).copy()
        j_values = analysis_data['J']
        close_prices = analysis_data['Close']
        
        # 找出超买信号点（J值从<=100变为>100）
        overbought_signals = (j_values > 100) & (j_values.shift(1) <= 100)
        
        returns_list = []
        signal_details = []
        
        for i, (date, is_signal) in enumerate(overbought_signals.items()):
            if is_signal and i + holding_days < len(analysis_data):
                # 信号发生日的收盘价
                entry_price = close_prices.iloc[i]
                # holding_days后的收盘价
                exit_price = close_prices.iloc[i + holding_days]
                
                # 计算收益率
                return_rate = (exit_price - entry_price) / entry_price
                returns_list.append(return_rate)
                
                signal_details.append({
                    'signal_date': date,
                    'entry_price': entry_price,
                    'exit_date': analysis_data.index[i + holding_days],
                    'exit_price': exit_price,
                    'return_rate': return_rate,
                    'return_pct': return_rate * 100
                })
        
        if returns_list:
            avg_return = np.mean(returns_list)
            max_return = np.max(returns_list)
            min_return = np.min(returns_list)
            win_rate = sum(1 for r in returns_list if r > 0) / len(returns_list)
        else:
            avg_return = max_return = min_return = win_rate = 0
        
        return {
            'signal_count': len(returns_list),
            'avg_return': avg_return,
            'avg_return_pct': avg_return * 100,
            'max_return': max_return,
            'min_return': min_return,
            'win_rate': win_rate,
            'signal_details': signal_details
        }
    
    def get_kdj_signals(self):
        """
        获取KDJ交易信号
        
        Returns:
        dict - KDJ交易信号
        """
        if not self.kdj_data:
            self.calculate_kdj()
        
        k_values = self.kdj_data['K']
        d_values = self.kdj_data['D']
        j_values = self.kdj_data['J']
        
        # KDJ金叉：K线从下方穿越D线
        kdj_golden_cross = (k_values > d_values) & (k_values.shift(1) <= d_values.shift(1))
        # KDJ死叉：K线从上方穿越D线
        kdj_death_cross = (k_values < d_values) & (k_values.shift(1) >= d_values.shift(1))
        
        # 超买超卖信号
        overbought_signal = j_values > 100  # 超买
        oversold_signal = j_values < 0      # 超卖
        
        return {
            'golden_cross': kdj_golden_cross,
            'death_cross': kdj_death_cross,
            'overbought': overbought_signal,
            'oversold': oversold_signal,
            'golden_count': kdj_golden_cross.sum(),
            'death_count': kdj_death_cross.sum()
        }


class RSIIndicator:
    """RSI指标类"""
    
    def __init__(self, data):
        """
        初始化RSI指标
        
        Parameters:
        data: DataFrame - 包含OHLCV数据的DataFrame
        """
        self.data = data.copy()
        self.close = data['Close'].values.astype(np.float64)
        
    def calculate_rsi(self, period=None):
        """
        计算RSI指标
        
        Parameters:
        period: int - RSI周期，默认14
        
        Returns:
        Series - RSI值序列
        """
        if period is None:
            period = RSI_CONFIG['period']
        
        rsi_values = tb.RSI(self.close, timeperiod=period)
        rsi_series = pd.Series(rsi_values, index=self.data.index)
        
        self.data['RSI'] = rsi_series
        return rsi_series
    
    def get_rsi_signals(self):
        """
        获取RSI交易信号
        
        Returns:
        dict - RSI交易信号
        """
        if 'RSI' not in self.data.columns:
            self.calculate_rsi()
        
        rsi_values = self.data['RSI']
        
        # RSI超买超卖信号
        rsi_overbought = rsi_values > 70   # 超买
        rsi_oversold = rsi_values < 30     # 超卖
        
        # RSI背离分析（简化版）
        # 这里实现简单的RSI趋势判断
        rsi_bullish = (rsi_values > 50) & (rsi_values.shift(1) <= 50)  # 转强
        rsi_bearish = (rsi_values < 50) & (rsi_values.shift(1) >= 50)  # 转弱
        
        return {
            'overbought': rsi_overbought,
            'oversold': rsi_oversold,
            'bullish_signal': rsi_bullish,
            'bearish_signal': rsi_bearish,
            'overbought_count': rsi_overbought.sum(),
            'oversold_count': rsi_oversold.sum()
        }


class KDJRSIComparator:
    """KDJ和RSI指标比较分析类"""
    
    def __init__(self, data):
        """
        初始化比较器
        
        Parameters:
        data: DataFrame - 包含OHLCV数据的DataFrame
        """
        self.data = data.copy()
        self.kdj = KDJIndicator(data)
        self.rsi = RSIIndicator(data)
        
    def calculate_all_indicators(self):
        """计算所有指标"""
        # 计算KDJ
        self.kdj.calculate_kdj()
        
        # 计算RSI
        self.rsi.calculate_rsi()
        
        # 合并数据
        for key, series in self.kdj.kdj_data.items():
            self.data[key] = series
        self.data['RSI'] = self.rsi.data['RSI']
        
        return self.data
    
    def compare_signals(self):
        """
        比较KDJ和RSI信号
        
        Returns:
        dict - 信号比较结果
        """
        kdj_signals = self.kdj.get_kdj_signals()
        rsi_signals = self.rsi.get_rsi_signals()
        
        # 信号一致性分析
        # 超买信号一致性
        overbought_agree = kdj_signals['overbought'] & rsi_signals['overbought']
        # 超卖信号一致性  
        oversold_agree = kdj_signals['oversold'] & rsi_signals['oversold']
        
        comparison_result = {
            'kdj_signals': kdj_signals,
            'rsi_signals': rsi_signals,
            'overbought_agree': overbought_agree,
            'oversold_agree': oversold_agree,
            'overbought_agree_count': overbought_agree.sum(),
            'oversold_agree_count': oversold_agree.sum()
        }
        
        return comparison_result


def analyze_kdj_rsi(data, analysis_days=120):
    """
    便捷函数：完整的KDJ和RSI分析
    
    Parameters:
    data: DataFrame - 股票数据
    analysis_days: int - 分析天数
    
    Returns:
    tuple: (comparator, kdj_analysis, returns_analysis, signal_comparison) - 分析结果
    """
    # 创建比较器
    comparator = KDJRSIComparator(data)
    comparator.calculate_all_indicators()
    
    # KDJ超买超卖分析
    kdj_analysis = comparator.kdj.analyze_overbought_oversold(analysis_days)
    
    # KDJ超买后收益率分析
    returns_analysis = comparator.kdj.calculate_overbought_returns(analysis_days)
    
    # 信号比较
    signal_comparison = comparator.compare_signals()
    
    return comparator, kdj_analysis, returns_analysis, signal_comparison


if __name__ == "__main__":
    # 测试代码
    from data.data_loader import get_stock_data
    
    try:
        # 获取测试数据
        df = get_stock_data()
        print("开始测试KDJ和RSI指标...")
        
        # 创建KDJ指标
        kdj = KDJIndicator(df)
        kdj_data = kdj.calculate_kdj()
        print(f"计算了KDJ指标：{list(kdj_data.keys())}")
        
        # KDJ超买超卖分析
        kdj_analysis = kdj.analyze_overbought_oversold(120)
        print(f"120天内超买次数：{kdj_analysis['overbought_count']}")
        print(f"120天内超卖次数：{kdj_analysis['oversold_count']}")
        
        # 超买后收益率分析
        returns_analysis = kdj.calculate_overbought_returns(120, 5)
        print(f"超买后5日平均收益率：{returns_analysis['avg_return_pct']:.2f}%")
        print(f"胜率：{returns_analysis['win_rate']:.2f}")
        
        # RSI指标
        rsi = RSIIndicator(df)
        rsi.calculate_rsi()
        rsi_signals = rsi.get_rsi_signals()
        print(f"RSI超买次数：{rsi_signals['overbought_count']}")
        print(f"RSI超卖次数：{rsi_signals['oversold_count']}")
        
        # KDJ和RSI比较
        comparator = KDJRSIComparator(df)
        comparator.calculate_all_indicators()
        comparison = comparator.compare_signals()
        print(f"超买信号一致次数：{comparison['overbought_agree_count']}")
        print(f"超卖信号一致次数：{comparison['oversold_agree_count']}")
        
        print("\nKDJ和RSI指标测试完成！")
        
    except Exception as e:
        print(f"测试失败：{str(e)}")
