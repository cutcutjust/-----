"""
多时间周期图表模块 - 实现日线、周线、月线对比分析
对应作业要求4：多时间周期图表
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import mplfinance as mpf
from matplotlib.patches import Rectangle
import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.config import CHART_STYLE, PATHS
from utils.helpers import ensure_directory_exists
from visualization.kline_chart import KLineChartRenderer


class MultiTimeFrameAnalyzer:
    """多时间周期分析器"""
    
    def __init__(self):
        """初始化多时间周期分析器"""
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = [CHART_STYLE['font_family']]
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.dpi'] = CHART_STYLE['figure_dpi']
        
        self.renderer = KLineChartRenderer()
    
    def prepare_multi_timeframe_data(self, daily_data):
        """
        准备多时间周期数据
        
        Parameters:
        daily_data: DataFrame - 日线数据
        
        Returns:
        dict - 包含日线、周线、月线数据的字典
        """
        # 日线数据（已有）
        daily = daily_data.copy()
        
        # 转换为周线数据
        weekly = daily_data.resample('W').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min', 
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        
        # 转换为月线数据
        monthly = daily_data.resample('M').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        
        return {
            'daily': daily,
            'weekly': weekly,
            'monthly': monthly
        }
    
    def calculate_multi_timeframe_ma(self, timeframe_data):
        """
        计算多时间周期移动平均线
        
        Parameters:
        timeframe_data: dict - 多时间周期数据
        
        Returns:
        dict - 包含各周期移动平均线的字典
        """
        ma_results = {}
        
        for timeframe, data in timeframe_data.items():
            close_prices = data['Close']
            
            # 计算适合不同周期的移动平均线
            if timeframe == 'daily':
                periods = [5, 10, 20, 60]
            elif timeframe == 'weekly':
                periods = [5, 10, 20]  # 对应日线的25、50、100日
            else:  # monthly
                periods = [3, 6, 12]   # 对应季度、半年、年线
            
            ma_data = {}
            for period in periods:
                if len(close_prices) >= period:
                    ma_data[f'MA_{period}'] = close_prices.rolling(window=period).mean()
            
            ma_results[timeframe] = ma_data
        
        return ma_results
    
    def calculate_multi_timeframe_macd(self, timeframe_data):
        """
        计算多时间周期MACD
        
        Parameters:
        timeframe_data: dict - 多时间周期数据
        
        Returns:
        dict - 包含各周期MACD的字典
        """
        macd_results = {}
        
        for timeframe, data in timeframe_data.items():
            close_prices = data['Close']
            
            # 根据时间周期调整MACD参数
            if timeframe == 'daily':
                fast, slow, signal = 12, 26, 9
            elif timeframe == 'weekly':
                fast, slow, signal = 12, 26, 9  # 周线使用相同参数
            else:  # monthly
                fast, slow, signal = 6, 12, 5   # 月线使用较短参数
            
            # 手动计算MACD
            ema_fast = close_prices.ewm(span=fast, adjust=False).mean()
            ema_slow = close_prices.ewm(span=slow, adjust=False).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            histogram = macd_line - signal_line
            
            macd_results[timeframe] = {
                'MACD': macd_line,
                'Signal': signal_line,
                'Histogram': histogram
            }
        
        return macd_results
    
    def analyze_multi_timeframe_trend(self, timeframe_data, ma_data):
        """
        分析多时间周期趋势
        
        Parameters:
        timeframe_data: dict - 多时间周期数据
        ma_data: dict - 各周期移动平均线数据
        
        Returns:
        dict - 趋势分析结果
        """
        trend_analysis = {}
        
        for timeframe in timeframe_data.keys():
            data = timeframe_data[timeframe]
            mas = ma_data[timeframe]
            
            current_price = data['Close'].iloc[-1]
            
            # 判断与移动平均线的关系
            above_ma_count = 0
            total_ma_count = 0
            
            for ma_name, ma_series in mas.items():
                if not ma_series.isna().iloc[-1]:
                    total_ma_count += 1
                    if current_price > ma_series.iloc[-1]:
                        above_ma_count += 1
            
            # 趋势判断
            if total_ma_count > 0:
                ma_ratio = above_ma_count / total_ma_count
                if ma_ratio >= 0.75:
                    trend = '强势上涨'
                elif ma_ratio >= 0.5:
                    trend = '温和上涨'
                elif ma_ratio >= 0.25:
                    trend = '温和下跌'
                else:
                    trend = '明显下跌'
            else:
                trend = '数据不足'
            
            # 价格变化
            if len(data) >= 2:
                price_change = (current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]
                price_change_pct = price_change * 100
            else:
                price_change_pct = 0
            
            trend_analysis[timeframe] = {
                'current_price': current_price,
                'trend': trend,
                'above_ma_ratio': ma_ratio if total_ma_count > 0 else 0,
                'price_change_pct': price_change_pct
            }
        
        return trend_analysis
    
    def plot_multi_timeframe_comparison(self, timeframe_data, ma_data, macd_data, title="多时间周期对比分析", figsize=(20, 15), save_path=None):
        """
        绘制多时间周期对比图表
        
        Parameters:
        timeframe_data: dict - 多时间周期数据
        ma_data: dict - 移动平均线数据
        macd_data: dict - MACD数据
        title: str - 图表标题
        figsize: tuple - 图表大小
        save_path: str - 保存路径
        
        Returns:
        tuple - (fig, axes) 图表对象
        """
        # 创建子图布局
        fig = plt.figure(figsize=figsize)
        gs = gridspec.GridSpec(3, 2, height_ratios=[2, 2, 2], width_ratios=[3, 1], 
                              hspace=0.3, wspace=0.2)
        
        timeframes = ['daily', 'weekly', 'monthly']
        timeframe_names = ['日线', '周线', '月线']
        
        axes = []
        
        for i, (timeframe, name) in enumerate(zip(timeframes, timeframe_names)):
            if timeframe not in timeframe_data:
                continue
            
            data = timeframe_data[timeframe]
            ma_indicators = ma_data[timeframe]
            macd_indicators = macd_data[timeframe]
            
            # 主K线图
            ax_main = fig.add_subplot(gs[i, 0])
            
            # 绘制K线
            self._plot_candlesticks(ax_main, data)
            
            # 绘制移动平均线
            colors = ['blue', 'orange', 'red', 'green', 'purple']
            for j, (ma_name, ma_series) in enumerate(ma_indicators.items()):
                color = colors[j % len(colors)]
                ax_main.plot(data.index, ma_series, color=color, linewidth=1.5, 
                           label=ma_name, alpha=0.8)
            
            ax_main.set_title(f'{name} - K线图+移动平均线', fontsize=14, fontweight='bold')
            ax_main.set_ylabel('价格', fontsize=12)
            ax_main.legend(loc='upper left', fontsize=10)
            ax_main.grid(True, alpha=0.3)
            
            # MACD子图
            ax_macd = fig.add_subplot(gs[i, 1])
            
            macd_line = macd_indicators['MACD']
            signal_line = macd_indicators['Signal']
            histogram = macd_indicators['Histogram']
            
            # 绘制MACD
            ax_macd.plot(data.index, macd_line, color='red', linewidth=1.5, label='MACD')
            ax_macd.plot(data.index, signal_line, color='blue', linewidth=1.5, label='Signal')
            
            # 绘制柱状图
            colors_hist = ['red' if x > 0 else 'green' for x in histogram]
            ax_macd.bar(data.index, histogram, color=colors_hist, alpha=0.6, width=1)
            
            ax_macd.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.8)
            ax_macd.set_title(f'{name} - MACD', fontsize=14, fontweight='bold')
            ax_macd.set_ylabel('MACD', fontsize=12)
            ax_macd.legend(loc='upper left', fontsize=10)
            ax_macd.grid(True, alpha=0.3)
            
            axes.append((ax_main, ax_macd))
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        
        if save_path:
            ensure_directory_exists(os.path.dirname(save_path))
            fig.savefig(save_path, bbox_inches='tight', dpi=300)
        
        return fig, axes
    
    def _plot_candlesticks(self, ax, data):
        """
        在指定坐标轴上绘制K线
        
        Parameters:
        ax: matplotlib.axes.Axes - 坐标轴对象
        data: DataFrame - OHLCV数据
        """
        for i, (date, row) in enumerate(data.iterrows()):
            open_price = row['Open']
            high_price = row['High']
            low_price = row['Low']
            close_price = row['Close']
            
            # 确定颜色
            color = CHART_STYLE['up_color'] if close_price >= open_price else CHART_STYLE['down_color']
            
            # 绘制影线
            ax.plot([i, i], [low_price, high_price], color='black', linewidth=1)
            
            # 绘制实体
            height = abs(close_price - open_price)
            bottom = min(open_price, close_price)
            
            if close_price >= open_price:  # 上涨
                rect = Rectangle((i-0.3, bottom), 0.6, height, 
                               facecolor=color, edgecolor='black', linewidth=0.5)
            else:  # 下跌
                rect = Rectangle((i-0.3, bottom), 0.6, height, 
                               facecolor='white', edgecolor=color, linewidth=0.5)
            
            ax.add_patch(rect)
        
        # 设置x轴
        ax.set_xlim(-0.5, len(data)-0.5)
        
        # 设置x轴标签（简化显示）
        n_ticks = min(10, len(data))
        tick_indices = np.linspace(0, len(data)-1, n_ticks, dtype=int)
        tick_labels = [data.index[i].strftime('%Y-%m-%d') for i in tick_indices]
        
        ax.set_xticks(tick_indices)
        ax.set_xticklabels(tick_labels, rotation=45, fontsize=10)
    
    def plot_trend_comparison_table(self, trend_analysis, title="多时间周期趋势对比", figsize=(12, 8), save_path=None):
        """
        绘制趋势对比表格
        
        Parameters:
        trend_analysis: dict - 趋势分析结果
        title: str - 图表标题
        figsize: tuple - 图表大小
        save_path: str - 保存路径
        
        Returns:
        tuple - (fig, ax) 图表对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 准备表格数据
        timeframe_names = {'daily': '日线', 'weekly': '周线', 'monthly': '月线'}
        table_data = []
        
        for timeframe, analysis in trend_analysis.items():
            table_data.append([
                timeframe_names.get(timeframe, timeframe),
                f"{analysis['current_price']:.2f}",
                analysis['trend'],
                f"{analysis['above_ma_ratio']:.0%}",
                f"{analysis['price_change_pct']:+.2f}%"
            ])
        
        # 创建表格
        columns = ['时间周期', '当前价格', '趋势判断', '均线多头排列比例', '周期内涨跌幅']
        
        table = ax.table(cellText=table_data, colLabels=columns, 
                        cellLoc='center', loc='center',
                        colWidths=[0.15, 0.15, 0.2, 0.25, 0.2])
        
        # 设置表格样式
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 2)
        
        # 设置表头样式
        for i in range(len(columns)):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 设置数据行样式
        for i in range(1, len(table_data) + 1):
            for j in range(len(columns)):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#f1f1f2')
                
                # 根据趋势设置颜色
                if j == 2:  # 趋势判断列
                    trend = table_data[i-1][j]
                    if '上涨' in trend:
                        table[(i, j)].set_facecolor('#ffcccc')
                    elif '下跌' in trend:
                        table[(i, j)].set_facecolor('#ccffcc')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        
        if save_path:
            ensure_directory_exists(os.path.dirname(save_path))
            fig.savefig(save_path, bbox_inches='tight', dpi=300)
        
        return fig, ax


def analyze_multi_timeframe(daily_data, save_charts=True):
    """
    便捷函数：完整的多时间周期分析
    
    Parameters:
    daily_data: DataFrame - 日线数据
    save_charts: bool - 是否保存图表
    
    Returns:
    tuple - (analyzer, timeframe_data, trend_analysis) - 分析器和结果
    """
    analyzer = MultiTimeFrameAnalyzer()
    
    # 准备多时间周期数据
    timeframe_data = analyzer.prepare_multi_timeframe_data(daily_data)
    
    # 计算技术指标
    ma_data = analyzer.calculate_multi_timeframe_ma(timeframe_data)
    macd_data = analyzer.calculate_multi_timeframe_macd(timeframe_data)
    
    # 趋势分析
    trend_analysis = analyzer.analyze_multi_timeframe_trend(timeframe_data, ma_data)
    
    if save_charts:
        # 保存对比图表
        chart_path = os.path.join(PATHS['charts'], 'multi_timeframe_comparison.png')
        analyzer.plot_multi_timeframe_comparison(
            timeframe_data, ma_data, macd_data, 
            save_path=chart_path
        )
        
        # 保存趋势对比表
        table_path = os.path.join(PATHS['charts'], 'trend_comparison_table.png')
        analyzer.plot_trend_comparison_table(
            trend_analysis,
            save_path=table_path
        )
    
    return analyzer, {'timeframe_data': timeframe_data, 'ma_data': ma_data, 'macd_data': macd_data}, trend_analysis


if __name__ == "__main__":
    # 测试代码
    from data.data_loader import get_stock_data
    
    try:
        # 获取测试数据
        df = get_stock_data()
        print("开始测试多时间周期分析...")
        
        # 创建分析器
        analyzer = MultiTimeFrameAnalyzer()
        
        # 准备多时间周期数据
        timeframe_data = analyzer.prepare_multi_timeframe_data(df)
        print(f"准备了多时间周期数据：{list(timeframe_data.keys())}")
        
        for tf, data in timeframe_data.items():
            print(f"{tf}: {len(data)} 条记录")
        
        # 计算移动平均线
        ma_data = analyzer.calculate_multi_timeframe_ma(timeframe_data)
        
        # 计算MACD
        macd_data = analyzer.calculate_multi_timeframe_macd(timeframe_data)
        
        # 趋势分析
        trend_analysis = analyzer.analyze_multi_timeframe_trend(timeframe_data, ma_data)
        
        print("\n多时间周期趋势分析：")
        for tf, analysis in trend_analysis.items():
            print(f"{tf}: {analysis['trend']} (当前价格: {analysis['current_price']:.2f})")
        
        # 绘制对比图表
        print("\n绘制多时间周期对比图表...")
        fig, axes = analyzer.plot_multi_timeframe_comparison(
            timeframe_data, ma_data, macd_data
        )
        plt.show()
        
        # 绘制趋势对比表
        print("绘制趋势对比表格...")
        fig2, ax2 = analyzer.plot_trend_comparison_table(trend_analysis)
        plt.show()
        
        print("\n多时间周期分析测试完成！")
        
    except Exception as e:
        print(f"测试失败：{str(e)}")
