"""
布林带指标模块 - 实现布林带计算和突破信号分析
对应作业要求2：布林带指标分析
"""

import pandas as pd
import numpy as np
import talib as tb
import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.config import BOLLINGER_CONFIG


class BollingerBands:
    """布林带指标类"""
    
    def __init__(self, data):
        """
        初始化布林带指标
        
        Parameters:
        data: DataFrame - 包含OHLCV数据的DataFrame
        """
        self.data = data.copy()
        self.close = data['Close'].values.astype(np.float64)
        self.bollinger_data = {}
        
    def calculate_bollinger_bands(self, period=None, std_dev=None):
        """
        计算布林带指标
        
        Parameters:
        period: int - 计算周期，默认20日
        std_dev: float - 标准差倍数，默认2倍
        
        Returns:
        dict - 包含上轨、中轨、下轨的字典
        """
        if period is None:
            period = BOLLINGER_CONFIG['period']
        if std_dev is None:
            std_dev = BOLLINGER_CONFIG['std_dev']
        
        # 使用TA-Lib计算布林带
        upper, middle, lower = tb.BBANDS(
            self.close, 
            timeperiod=period, 
            nbdevup=std_dev, 
            nbdevdn=std_dev, 
            matype=0  # SMA
        )
        
        self.bollinger_data = {
            'BB_Upper': pd.Series(upper, index=self.data.index),
            'BB_Middle': pd.Series(middle, index=self.data.index), 
            'BB_Lower': pd.Series(lower, index=self.data.index)
        }
        
        # 添加到原数据中
        for key, series in self.bollinger_data.items():
            self.data[key] = series
        
        return self.bollinger_data
    
    def calculate_band_width(self):
        """
        计算布林带宽度(Band Width)
        
        Returns:
        Series - 布林带宽度序列
        """
        if not self.bollinger_data:
            self.calculate_bollinger_bands()
        
        upper = self.bollinger_data['BB_Upper']
        lower = self.bollinger_data['BB_Lower']
        middle = self.bollinger_data['BB_Middle']
        
        # 布林带宽度 = (上轨 - 下轨) / 中轨
        band_width = (upper - lower) / middle
        self.data['BB_Width'] = band_width
        
        return band_width
    
    def calculate_percent_b(self):
        """
        计算%B指标（价格在布林带中的相对位置）
        
        Returns:
        Series - %B指标序列
        """
        if not self.bollinger_data:
            self.calculate_bollinger_bands()
        
        close_prices = pd.Series(self.close, index=self.data.index)
        upper = self.bollinger_data['BB_Upper']
        lower = self.bollinger_data['BB_Lower']
        
        # %B = (收盘价 - 下轨) / (上轨 - 下轨)
        percent_b = (close_prices - lower) / (upper - lower)
        self.data['Percent_B'] = percent_b
        
        return percent_b
    
    def identify_breakout_signals(self):
        """
        识别布林带突破信号
        
        Returns:
        dict - 包含突破信号的字典
        """
        if not self.bollinger_data:
            self.calculate_bollinger_bands()
        
        close_prices = pd.Series(self.close, index=self.data.index)
        upper = self.bollinger_data['BB_Upper']
        lower = self.bollinger_data['BB_Lower']
        
        # 突破上轨信号（强势）
        upper_breakout = (close_prices > upper).fillna(False)
        # 跌破下轨信号（弱势）
        lower_breakout = (close_prices < lower).fillna(False)
        
        # 突破上轨后的时点（从不突破到突破）
        upper_breakout_points = upper_breakout & (~upper_breakout.shift(1).fillna(False))
        # 跌破下轨后的时点
        lower_breakout_points = lower_breakout & (~lower_breakout.shift(1).fillna(False))
        
        breakout_signals = {
            'upper_breakout': upper_breakout,
            'lower_breakout': lower_breakout,
            'upper_breakout_points': upper_breakout_points,
            'lower_breakout_points': lower_breakout_points,
            'upper_count': upper_breakout_points.sum(),
            'lower_count': lower_breakout_points.sum()
        }
        
        return breakout_signals
    
    def analyze_squeeze_pattern(self):
        """
        分析布林带收窄（挤压）模式及突破方向
        
        Returns:
        dict - 包含收窄分析的字典
        """
        if 'BB_Width' not in self.data.columns:
            self.calculate_band_width()
        
        band_width = self.data['BB_Width']
        close_prices = pd.Series(self.close, index=self.data.index)
        
        # 计算布林带宽度的滚动均值和标准差
        width_ma = band_width.rolling(window=20).mean()
        width_std = band_width.rolling(window=20).std()
        
        # 定义收窄：当前宽度小于均值减去一个标准差
        squeeze_condition = (band_width < (width_ma - width_std)).fillna(False)
        
        # 找出收窄期间
        squeeze_periods = []
        in_squeeze = False
        squeeze_start = None
        
        for i, is_squeeze in enumerate(squeeze_condition):
            if is_squeeze and not in_squeeze:
                # 开始收窄
                squeeze_start = i
                in_squeeze = True
            elif not is_squeeze and in_squeeze:
                # 结束收窄
                if squeeze_start is not None:
                    squeeze_periods.append((squeeze_start, i-1))
                in_squeeze = False
        
        # 分析每次收窄后的突破方向
        squeeze_analysis = []
        for start_idx, end_idx in squeeze_periods:
            if end_idx + 5 < len(self.data):  # 确保有足够的后续数据
                # 收窄结束时的价格
                end_price = close_prices.iloc[end_idx]
                # 收窄结束后5日的价格
                future_price = close_prices.iloc[end_idx + 5]
                
                # 判断突破方向
                price_change = (future_price - end_price) / end_price
                if price_change > 0.02:  # 向上突破（涨幅>2%）
                    direction = '向上突破'
                elif price_change < -0.02:  # 向下突破（跌幅>2%）
                    direction = '向下突破'
                else:
                    direction = '横向整理'
                
                squeeze_analysis.append({
                    'start_date': self.data.index[start_idx],
                    'end_date': self.data.index[end_idx],
                    'duration': end_idx - start_idx + 1,
                    'end_price': end_price,
                    'future_price': future_price,
                    'price_change_pct': price_change * 100,
                    'breakout_direction': direction
                })
        
        return {
            'squeeze_condition': squeeze_condition,
            'squeeze_periods': squeeze_periods,
            'squeeze_analysis': squeeze_analysis,
            'total_squeezes': len(squeeze_periods)
        }
    
    def get_current_bollinger_status(self):
        """
        获取当前布林带状态
        
        Returns:
        dict - 当前布林带状态信息
        """
        if not self.bollinger_data:
            self.calculate_bollinger_bands()
        
        # 获取最新数据
        current_price = self.close[-1]
        upper = self.bollinger_data['BB_Upper'].iloc[-1]
        middle = self.bollinger_data['BB_Middle'].iloc[-1]
        lower = self.bollinger_data['BB_Lower'].iloc[-1]
        
        if 'BB_Width' not in self.data.columns:
            self.calculate_band_width()
        current_width = self.data['BB_Width'].iloc[-1]
        
        if 'Percent_B' not in self.data.columns:
            self.calculate_percent_b()
        current_percent_b = self.data['Percent_B'].iloc[-1]
        
        # 判断位置状态
        if current_price > upper:
            position_status = '突破上轨'
        elif current_price < lower:
            position_status = '跌破下轨'
        elif current_price > middle:
            position_status = '中轨上方'
        else:
            position_status = '中轨下方'
        
        # 判断宽度状态
        width_ma = self.data['BB_Width'].rolling(window=20).mean().iloc[-1]
        if current_width > width_ma * 1.2:
            width_status = '宽度较大'
        elif current_width < width_ma * 0.8:
            width_status = '宽度收窄'
        else:
            width_status = '宽度正常'
        
        return {
            'current_price': current_price,
            'upper_band': upper,
            'middle_band': middle,
            'lower_band': lower,
            'band_width': current_width,
            'percent_b': current_percent_b,
            'position_status': position_status,
            'width_status': width_status
        }


def analyze_bollinger_bands(data):
    """
    便捷函数：完整的布林带分析
    
    Parameters:
    data: DataFrame - 股票数据
    
    Returns:
    tuple: (bollinger, breakout_signals, squeeze_analysis) - 布林带对象和分析结果
    """
    bollinger = BollingerBands(data)
    bollinger.calculate_bollinger_bands()
    bollinger.calculate_band_width()
    bollinger.calculate_percent_b()
    
    breakout_signals = bollinger.identify_breakout_signals()
    squeeze_analysis = bollinger.analyze_squeeze_pattern()
    
    return bollinger, breakout_signals, squeeze_analysis


if __name__ == "__main__":
    # 测试代码
    from data.data_loader import get_stock_data
    
    try:
        # 获取测试数据
        df = get_stock_data()
        print("开始测试布林带指标...")
        
        # 创建布林带分析
        bollinger = BollingerBands(df)
        
        # 计算布林带
        bb_data = bollinger.calculate_bollinger_bands()
        print(f"计算了布林带三轨：{list(bb_data.keys())}")
        
        # 计算带宽
        band_width = bollinger.calculate_band_width()
        print(f"计算了布林带宽度，最新值：{band_width.iloc[-1]:.4f}")
        
        # 识别突破信号
        breakout_signals = bollinger.identify_breakout_signals()
        print(f"上轨突破次数：{breakout_signals['upper_count']}")
        print(f"下轨突破次数：{breakout_signals['lower_count']}")
        
        # 收窄模式分析
        squeeze_analysis = bollinger.analyze_squeeze_pattern()
        print(f"检测到 {squeeze_analysis['total_squeezes']} 次布林带收窄")
        
        # 当前状态
        current_status = bollinger.get_current_bollinger_status()
        print(f"\n当前布林带状态：")
        print(f"价格位置：{current_status['position_status']}")
        print(f"带宽状态：{current_status['width_status']}")
        
        print("\n布林带指标测试完成！")
        
    except Exception as e:
        print(f"测试失败：{str(e)}")
