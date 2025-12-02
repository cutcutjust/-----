"""
MACD指标模块 - 实现MACD指标计算和信号分析
用于K线图的副图显示
"""

import pandas as pd
import numpy as np
import talib as tb
import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.config import MACD_CONFIG
from utils.helpers import identify_cross_signals, count_signals


class MACDIndicator:
    """MACD指标类"""
    
    def __init__(self, data):
        """
        初始化MACD指标
        
        Parameters:
        data: DataFrame - 包含OHLCV数据的DataFrame
        """
        self.data = data.copy()
        self.close = data['Close'].values.astype(np.float64)
        self.macd_data = {}
        
    def calculate_macd(self, fast_period=None, slow_period=None, signal_period=None):
        """
        计算MACD指标
        
        Parameters:
        fast_period: int - 快线周期，默认12
        slow_period: int - 慢线周期，默认26  
        signal_period: int - 信号线周期，默认9
        
        Returns:
        dict - 包含MACD、Signal、Histogram的字典
        """
        if fast_period is None:
            fast_period = MACD_CONFIG['fast_period']
        if slow_period is None:
            slow_period = MACD_CONFIG['slow_period']
        if signal_period is None:
            signal_period = MACD_CONFIG['signal_period']
        
        # 使用TA-Lib计算MACD
        macd_line, signal_line, histogram = tb.MACD(
            self.close,
            fastperiod=fast_period,
            slowperiod=slow_period,
            signalperiod=signal_period
        )
        
        self.macd_data = {
            'MACD': pd.Series(macd_line, index=self.data.index),
            'Signal': pd.Series(signal_line, index=self.data.index),
            'Histogram': pd.Series(histogram, index=self.data.index)
        }
        
        # 添加到原数据中
        for key, series in self.macd_data.items():
            self.data[key] = series
        
        return self.macd_data
    
    def calculate_macd_manual(self, fast_period=None, slow_period=None, signal_period=None):
        """
        手动计算MACD（用于教学和验证）
        
        Parameters:
        fast_period: int - 快线周期，默认12
        slow_period: int - 慢线周期，默认26
        signal_period: int - 信号线周期，默认9
        
        Returns:
        dict - 包含MACD各组件的字典
        """
        if fast_period is None:
            fast_period = MACD_CONFIG['fast_period']
        if slow_period is None:
            slow_period = MACD_CONFIG['slow_period']
        if signal_period is None:
            signal_period = MACD_CONFIG['signal_period']
        
        close_series = pd.Series(self.close, index=self.data.index)
        
        # 计算快慢EMA
        ema_fast = close_series.ewm(span=fast_period, adjust=False).mean()
        ema_slow = close_series.ewm(span=slow_period, adjust=False).mean()
        
        # MACD线（DIF）= EMA12 - EMA26
        macd_line = ema_fast - ema_slow
        
        # 信号线（DEA）= MACD的9日EMA
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # 柱状图（MACD）= MACD线 - 信号线
        histogram = macd_line - signal_line
        
        manual_macd = {
            'EMA_Fast': ema_fast,
            'EMA_Slow': ema_slow,
            'MACD_Manual': macd_line,
            'Signal_Manual': signal_line,
            'Histogram_Manual': histogram
        }
        
        return manual_macd
    
    def identify_macd_signals(self):
        """
        识别MACD交易信号
        
        Returns:
        dict - 包含MACD交易信号的字典
        """
        if not self.macd_data:
            self.calculate_macd()
        
        macd_line = self.macd_data['MACD']
        signal_line = self.macd_data['Signal']
        histogram = self.macd_data['Histogram']
        
        # MACD金叉死叉信号
        golden_cross, death_cross = identify_cross_signals(macd_line, signal_line)
        
        # MACD零轴穿越
        # 上穿零轴（从负变正）
        zero_cross_up = (macd_line > 0) & (macd_line.shift(1) <= 0)
        # 下穿零轴（从正变负）
        zero_cross_down = (macd_line < 0) & (macd_line.shift(1) >= 0)
        
        # 柱状图信号
        # 柱状图由负转正
        hist_turn_positive = (histogram > 0) & (histogram.shift(1) <= 0)
        # 柱状图由正转负
        hist_turn_negative = (histogram < 0) & (histogram.shift(1) >= 0)
        
        # 背离信号（简化版）
        # 这里实现简单的背离检测
        price_series = pd.Series(self.close, index=self.data.index)
        
        signals = {
            'golden_cross': golden_cross,
            'death_cross': death_cross,
            'zero_cross_up': zero_cross_up,
            'zero_cross_down': zero_cross_down,
            'hist_turn_positive': hist_turn_positive,
            'hist_turn_negative': hist_turn_negative,
            'golden_count': count_signals(golden_cross),
            'death_count': count_signals(death_cross),
            'zero_up_count': count_signals(zero_cross_up),
            'zero_down_count': count_signals(zero_cross_down)
        }
        
        return signals
    
    def get_macd_trend_analysis(self):
        """
        获取MACD趋势分析
        
        Returns:
        dict - MACD趋势分析结果
        """
        if not self.macd_data:
            self.calculate_macd()
        
        macd_line = self.macd_data['MACD']
        signal_line = self.macd_data['Signal']
        histogram = self.macd_data['Histogram']
        
        # 获取最新值
        latest_macd = macd_line.iloc[-1]
        latest_signal = signal_line.iloc[-1]
        latest_histogram = histogram.iloc[-1]
        
        # 趋势判断
        if latest_macd > latest_signal and latest_macd > 0:
            trend = '强势上涨'
        elif latest_macd > latest_signal and latest_macd < 0:
            trend = '弱势反弹'
        elif latest_macd < latest_signal and latest_macd < 0:
            trend = '弱势下跌'
        else:
            trend = '强势回调'
        
        # 动量判断
        if latest_histogram > histogram.iloc[-2]:
            momentum = '动量增强'
        elif latest_histogram < histogram.iloc[-2]:
            momentum = '动量减弱'
        else:
            momentum = '动量持平'
        
        return {
            'latest_macd': latest_macd,
            'latest_signal': latest_signal,
            'latest_histogram': latest_histogram,
            'trend': trend,
            'momentum': momentum,
            'macd_above_signal': latest_macd > latest_signal,
            'macd_above_zero': latest_macd > 0
        }
    
    def prepare_for_plotting(self):
        """
        为绘图准备MACD数据（分离正负柱状图）
        
        Returns:
        dict - 用于绘图的MACD数据
        """
        if not self.macd_data:
            self.calculate_macd()
        
        histogram = self.macd_data['Histogram']
        
        # 分离正负柱状图
        histogram_positive = histogram.copy()
        histogram_positive[histogram_positive < 0] = np.nan
        
        histogram_negative = histogram.copy()
        histogram_negative[histogram_negative >= 0] = np.nan
        
        plot_data = {
            'MACD': self.macd_data['MACD'],
            'Signal': self.macd_data['Signal'],
            'Histogram_Positive': histogram_positive,
            'Histogram_Negative': histogram_negative
        }
        
        return plot_data
    
    def get_current_macd_status(self):
        """
        获取当前MACD状态
        
        Returns:
        dict - 当前MACD状态信息
        """
        trend_analysis = self.get_macd_trend_analysis()
        signals = self.identify_macd_signals()
        
        # 检查最近是否有信号
        recent_golden = signals['golden_cross'].tail(5).any()
        recent_death = signals['death_cross'].tail(5).any()
        
        status = {
            'current_values': {
                'macd': trend_analysis['latest_macd'],
                'signal': trend_analysis['latest_signal'],
                'histogram': trend_analysis['latest_histogram']
            },
            'trend': trend_analysis['trend'],
            'momentum': trend_analysis['momentum'],
            'recent_signals': {
                'golden_cross': recent_golden,
                'death_cross': recent_death
            }
        }
        
        return status


def analyze_macd(data):
    """
    便捷函数：完整的MACD分析
    
    Parameters:
    data: DataFrame - 股票数据
    
    Returns:
    tuple: (macd_indicator, signals, trend_analysis) - MACD指标对象和分析结果
    """
    macd_indicator = MACDIndicator(data)
    macd_indicator.calculate_macd()
    
    signals = macd_indicator.identify_macd_signals()
    trend_analysis = macd_indicator.get_macd_trend_analysis()
    
    return macd_indicator, signals, trend_analysis


if __name__ == "__main__":
    # 测试代码
    from data.data_loader import get_stock_data
    
    try:
        # 获取测试数据
        df = get_stock_data()
        print("开始测试MACD指标...")
        
        # 创建MACD指标
        macd = MACDIndicator(df)
        
        # 计算MACD
        macd_data = macd.calculate_macd()
        print(f"计算了MACD指标：{list(macd_data.keys())}")
        
        # 识别信号
        signals = macd.identify_macd_signals()
        print(f"MACD金叉次数：{signals['golden_count']}")
        print(f"MACD死叉次数：{signals['death_count']}")
        print(f"零轴上穿次数：{signals['zero_up_count']}")
        print(f"零轴下穿次数：{signals['zero_down_count']}")
        
        # 趋势分析
        trend_analysis = macd.get_macd_trend_analysis()
        print(f"\n当前MACD趋势：{trend_analysis['trend']}")
        print(f"动量状态：{trend_analysis['momentum']}")
        
        # 当前状态
        current_status = macd.get_current_macd_status()
        print(f"MACD值：{current_status['current_values']['macd']:.4f}")
        print(f"Signal值：{current_status['current_values']['signal']:.4f}")
        print(f"Histogram值：{current_status['current_values']['histogram']:.4f}")
        
        print("\nMACD指标测试完成！")
        
    except Exception as e:
        print(f"测试失败：{str(e)}")
