"""
K线图绘制模块 - 实现自定义K线图样式和技术指标图表
对应作业要求3：自定义K线图样式
"""

import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle
import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.config import CHART_STYLE, PATHS
from utils.helpers import ensure_directory_exists


class KLineChartRenderer:
    """K线图渲染类"""
    
    def __init__(self):
        """初始化K线图渲染器"""
        # 设置中文字体和负号显示
        plt.rcParams['font.sans-serif'] = [CHART_STYLE['font_family']]
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.dpi'] = CHART_STYLE['figure_dpi']
        
        # 创建自定义样式
        self.custom_style = self._create_custom_style()
    
    def _create_custom_style(self):
        """
        创建自定义图表样式
        
        Returns:
        dict - mplfinance样式配置
        """
        # 设置K线颜色
        market_colors = mpf.make_marketcolors(
            up=CHART_STYLE['up_color'],      # 上涨K线为红色实心
            down=CHART_STYLE['down_color'],  # 下跌K线为绿色空心
            edge=CHART_STYLE['edge_color'],  # K线边框颜色
            wick=CHART_STYLE['wick_color'],  # 影线颜色
            volume='inherit'                 # 成交量颜色继承K线颜色
        )
        
        # 创建样式
        style = mpf.make_mpf_style(
            marketcolors=market_colors,
            rc={
                'font.family': CHART_STYLE['font_family'],
                'axes.unicode_minus': False,
                'figure.dpi': CHART_STYLE['figure_dpi']
            }
        )
        
        return style
    
    def plot_basic_kline(self, data, title="K线图", figsize=(12, 8), save_path=None):
        """
        绘制基础K线图
        
        Parameters:
        data: DataFrame - 包含OHLCV数据的DataFrame
        title: str - 图表标题
        figsize: tuple - 图表大小
        save_path: str - 保存路径，None表示不保存
        
        Returns:
        tuple - (fig, axes) 图表对象
        """
        fig, axes = mpf.plot(
            data,
            type='candle',
            style=self.custom_style,
            title=title,
            ylabel='价格',
            volume=True,
            ylabel_lower='成交量',
            figsize=figsize,
            returnfig=True
        )
        
        # 添加网格线并设置透明度
        for ax in axes:
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.tick_params(axis='both', labelsize=10)
        
        if save_path:
            ensure_directory_exists(os.path.dirname(save_path))
            fig.savefig(save_path, bbox_inches='tight', dpi=300)
        
        return fig, axes
    
    def plot_kline_with_ma(self, data, ma_data, title="K线图+移动平均线", figsize=(12, 8), save_path=None):
        """
        绘制带移动平均线的K线图
        
        Parameters:
        data: DataFrame - 包含OHLCV数据的DataFrame
        ma_data: dict - 移动平均线数据
        title: str - 图表标题
        figsize: tuple - 图表大小  
        save_path: str - 保存路径
        
        Returns:
        tuple - (fig, axes) 图表对象
        """
        # 创建移动平均线附加图
        addplots = []
        ma_colors = ['blue', 'orange', 'purple', 'brown', 'pink', 'gray']
        
        for i, (ma_name, ma_series) in enumerate(ma_data.items()):
            if not ma_series.isna().all():
                color = ma_colors[i % len(ma_colors)]
                addplots.append(
                    mpf.make_addplot(ma_series, color=color, width=1.5, label=ma_name)
                )
        
        fig, axes = mpf.plot(
            data,
            type='candle',
            style=self.custom_style,
            title=title,
            ylabel='价格',
            volume=True,
            ylabel_lower='成交量',
            addplot=addplots,
            figsize=figsize,
            returnfig=True
        )
        
        # 添加网格和格式化
        for ax in axes:
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.tick_params(axis='both', labelsize=10)
        
        if save_path:
            ensure_directory_exists(os.path.dirname(save_path))
            fig.savefig(save_path, bbox_inches='tight', dpi=300)
        
        return fig, axes
    
    def plot_kline_with_bollinger(self, data, bollinger_data, title="K线图+布林带", figsize=(12, 8), save_path=None):
        """
        绘制带布林带的K线图
        
        Parameters:
        data: DataFrame - 包含OHLCV数据的DataFrame
        bollinger_data: dict - 布林带数据
        title: str - 图表标题
        figsize: tuple - 图表大小
        save_path: str - 保存路径
        
        Returns:
        tuple - (fig, axes) 图表对象
        """
        addplots = [
            mpf.make_addplot(bollinger_data['BB_Upper'], color='red', linestyle='--', width=1, alpha=0.8, label='上轨'),
            mpf.make_addplot(bollinger_data['BB_Middle'], color='blue', linestyle='-', width=1.5, label='中轨'),
            mpf.make_addplot(bollinger_data['BB_Lower'], color='green', linestyle='--', width=1, alpha=0.8, label='下轨')
        ]
        
        fig, axes = mpf.plot(
            data,
            type='candle',
            style=self.custom_style,
            title=title,
            ylabel='价格',
            volume=True,
            ylabel_lower='成交量',
            addplot=addplots,
            figsize=figsize,
            returnfig=True
        )
        
        # 添加布林带填充区域
        ax_main = axes[0]
        upper = bollinger_data['BB_Upper'].values
        lower = bollinger_data['BB_Lower'].values
        x_values = range(len(data))
        
        # 填充布林带区域
        ax_main.fill_between(x_values, upper, lower, alpha=0.1, color='gray')
        
        # 添加网格
        for ax in axes:
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.tick_params(axis='both', labelsize=10)
        
        if save_path:
            ensure_directory_exists(os.path.dirname(save_path))
            fig.savefig(save_path, bbox_inches='tight', dpi=300)
        
        return fig, axes
    
    def plot_bollinger_bandwidth(self, data, band_width, title="布林带宽度变化", figsize=(12, 6), save_path=None):
        """
        绘制布林带宽度变化图（Task2-2）
        
        Parameters:
        data: DataFrame - 股票数据
        band_width: Series - 布林带宽度
        title: str - 标题
        figsize: tuple - 图表大小
        save_path: str - 保存路径
        
        Returns:
        tuple - (fig, ax) 图表对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制带宽
        ax.plot(data.index, band_width, color='blue', linewidth=2, label='布林带宽度')
        
        # 计算带宽均值和标准差
        width_ma = band_width.rolling(window=20).mean()
        width_std = band_width.rolling(window=20).std()
        
        # 绘制均值和波段
        ax.plot(data.index, width_ma, color='orange', linewidth=1.5, linestyle='--', label='20日均值')
        ax.fill_between(data.index, 
                        width_ma - width_std, 
                        width_ma + width_std, 
                        alpha=0.2, color='gray', label='±1σ')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('布林带宽度', fontsize=12)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # 格式化x轴标签
        ax.tick_params(axis='both', labelsize=10)
        
        if save_path:
            ensure_directory_exists(os.path.dirname(save_path))
            fig.savefig(save_path, bbox_inches='tight', dpi=300)
        
        return fig, ax
    
    def plot_kline_with_macd_volume(self, data, macd_data, title="K线图+MACD+成交量", figsize=(14, 12), save_path=None):
        """
        绘制K线图+MACD+成交量（分3个面板：K线、MACD、成交量）
        
        Parameters:
        data: DataFrame - 包含OHLCV数据的DataFrame
        macd_data: dict - MACD数据
        title: str - 图表标题
        figsize: tuple - 图表大小
        save_path: str - 保存路径
        
        Returns:
        tuple - (fig, axes) 图表对象
        """
        # 准备MACD绘图数据
        macd_line = macd_data['MACD']
        signal_line = macd_data['Signal']
        histogram = macd_data['Histogram']
        
        # 分离正负柱状图
        histogram_positive = histogram.copy()
        histogram_positive[histogram_positive < 0] = np.nan
        histogram_negative = histogram.copy()
        histogram_negative[histogram_negative >= 0] = np.nan
        
        # 计算成交量移动平均线
        volume_ma = data['Volume'].rolling(window=5).mean()
        
        # 创建附加图 - MACD在panel=1，成交量移动平均线在panel=2
        addplots = [
            # MACD线和信号线（panel=1）
            mpf.make_addplot(macd_line, panel=1, color='red', width=1.5, ylabel='MACD'),
            mpf.make_addplot(signal_line, panel=1, color='blue', width=1.5),
            # MACD柱状图（panel=1）
            mpf.make_addplot(histogram_positive, panel=1, type='bar', width=0.8, color='red', alpha=0.8),
            mpf.make_addplot(histogram_negative, panel=1, type='bar', width=0.8, color='green', alpha=0.8),
            # 成交量移动平均线（panel=2）
            mpf.make_addplot(volume_ma, panel=2, color='orange', width=2, ylabel='成交量')
        ]
        
        fig, axes = mpf.plot(
            data,
            type='candle',
            style=self.custom_style,
            title=title,
            ylabel='价格',
            volume=True,  # 这会创建成交量面板
            addplot=addplots,
            panel_ratios=(4, 1.5, 1.5),  # 主图:MACD:成交量 = 4:1.5:1.5
            figsize=figsize,
            returnfig=True
        )
        
        # 格式化坐标轴
        for i, ax in enumerate(axes):
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.tick_params(axis='both', labelsize=10)
            
            if i == 0:  # K线主图
                ax.set_ylabel('价格 (元)', fontsize=12)
            elif i == 1:  # MACD面板
                ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.8)
                ax.set_ylabel('MACD', fontsize=12)
                # 添加图例
                ax.text(0.02, 0.95, 'MACD线', transform=ax.transAxes, fontsize=10, 
                       bbox=dict(boxstyle='round', facecolor='red', alpha=0.3))
                ax.text(0.02, 0.85, 'Signal线', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='blue', alpha=0.3))
            elif i == 2:  # 成交量面板
                ax.set_ylabel('成交量 (手)', fontsize=12)
                # 添加成交量MA5标注
                ax.text(0.02, 0.95, 'Volume', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='gray', alpha=0.3))
                ax.text(0.02, 0.85, 'MA5', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='orange', alpha=0.3))
        
        if save_path:
            ensure_directory_exists(os.path.dirname(save_path))
            fig.savefig(save_path, bbox_inches='tight', dpi=300)
        
        return fig, axes
    
    def plot_ma_and_bollinger(self, data, ma_data, bollinger_data, title="K线图+MA+布林带", figsize=(14, 8), save_path=None):
        """
        绘制MA+布林带组合图（分离设计）
        
        Parameters:
        data: DataFrame - 股票数据
        ma_data: dict - 移动平均线数据
        bollinger_data: dict - 布林带数据
        title: str - 标题
        figsize: tuple - 图表大小
        save_path: str - 保存路径
        
        Returns:
        tuple - (fig, axes) 图表对象
        """
        addplots = []
        
        # 添加移动平均线
        ma_colors = ['blue', 'orange', 'red', 'green', 'purple']
        for i, (ma_name, ma_series) in enumerate(ma_data.items()):
            if not ma_series.isna().all():
                color = ma_colors[i % len(ma_colors)]
                addplots.append(mpf.make_addplot(ma_series, color=color, width=1.5, label=ma_name))
        
        # 添加布林带
        addplots.extend([
            mpf.make_addplot(bollinger_data['BB_Upper'], color='red', linestyle='--', width=1, alpha=0.7),
            mpf.make_addplot(bollinger_data['BB_Middle'], color='blue', linestyle='-', width=1),
            mpf.make_addplot(bollinger_data['BB_Lower'], color='green', linestyle='--', width=1, alpha=0.7)
        ])
        
        fig, axes = mpf.plot(
            data,
            type='candle',
            style=self.custom_style,
            title=title,
            ylabel='价格',
            volume=True,
            ylabel_lower='成交量',
            addplot=addplots,
            figsize=figsize,
            returnfig=True
        )
        
        for ax in axes:
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.tick_params(axis='both', labelsize=10)
        
        if save_path:
            ensure_directory_exists(os.path.dirname(save_path))
            fig.savefig(save_path, bbox_inches='tight', dpi=300)
        
        return fig, axes
    
    def plot_kdj_chart(self, data, kdj_data, title="KDJ指标图", figsize=(14, 10), save_path=None):
        """
        绘制KDJ独立图表（分3个面板：K线、KDJ、成交量）
        
        Parameters:
        data: DataFrame - 股票数据
        kdj_data: dict - KDJ数据
        title: str - 标题
        figsize: tuple - 图表大小
        save_path: str - 保存路径
        
        Returns:
        tuple - (fig, axes) 图表对象
        """
        # KDJ指标在panel=1，成交量移动平均线在panel=2
        volume_ma = data['Volume'].rolling(window=5).mean()
        
        addplots = [
            # KDJ指标在panel=1
            mpf.make_addplot(kdj_data['K'], panel=1, color='blue', width=1.5, ylabel='KDJ'),
            mpf.make_addplot(kdj_data['D'], panel=1, color='orange', width=1.5),
            mpf.make_addplot(kdj_data['J'], panel=1, color='red', width=1.5),
            # 成交量移动平均线在panel=2
            mpf.make_addplot(volume_ma, panel=2, color='purple', width=2, ylabel='成交量')
        ]
        
        fig, axes = mpf.plot(
            data,
            type='candle',
            style=self.custom_style,
            title=title,
            ylabel='价格',
            volume=True,  # 成交量柱状图
            addplot=addplots,
            panel_ratios=(4, 1.5, 1.5),  # 主图:KDJ:成交量 = 4:1.5:1.5
            figsize=figsize,
            returnfig=True
        )
        
        # 格式化坐标轴
        for i, ax in enumerate(axes):
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.tick_params(axis='both', labelsize=10)
            
            if i == 0:  # K线主图
                ax.set_ylabel('价格 (元)', fontsize=12)
            elif i == 1:  # KDJ面板
                # 添加参考线
                ax.axhline(y=80, color='red', linestyle='--', alpha=0.5, linewidth=1, label='超买线')
                ax.axhline(y=20, color='green', linestyle='--', alpha=0.5, linewidth=1, label='超卖线')
                ax.axhline(y=50, color='gray', linestyle='-', alpha=0.3, linewidth=0.8)
                ax.set_ylim(-20, 120)
                ax.set_ylabel('KDJ (%)', fontsize=12)
                # 添加图例
                ax.text(0.02, 0.95, 'K线', transform=ax.transAxes, fontsize=10, 
                       bbox=dict(boxstyle='round', facecolor='blue', alpha=0.3))
                ax.text(0.02, 0.85, 'D线', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='orange', alpha=0.3))
                ax.text(0.02, 0.75, 'J线', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='red', alpha=0.3))
            elif i == 2:  # 成交量面板
                ax.set_ylabel('成交量 (手)', fontsize=12)
                ax.text(0.02, 0.95, 'Volume', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='gray', alpha=0.3))
                ax.text(0.02, 0.85, 'MA5', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='purple', alpha=0.3))
        
        if save_path:
            ensure_directory_exists(os.path.dirname(save_path))
            fig.savefig(save_path, bbox_inches='tight', dpi=300)
        
        return fig, axes
    
    def plot_rsi_chart(self, data, rsi_data, title="RSI指标图", figsize=(14, 10), save_path=None):
        """
        绘制RSI独立图表（分3个面板：K线、RSI、成交量）
        
        Parameters:
        data: DataFrame - 股票数据
        rsi_data: Series - RSI数据
        title: str - 标题
        figsize: tuple - 图表大小
        save_path: str - 保存路径
        
        Returns:
        tuple - (fig, axes) 图表对象
        """
        # RSI指标在panel=1，成交量移动平均线在panel=2
        volume_ma = data['Volume'].rolling(window=5).mean()
        
        addplots = [
            # RSI指标在panel=1
            mpf.make_addplot(rsi_data, panel=1, color='purple', width=2, ylabel='RSI'),
            # 成交量移动平均线在panel=2
            mpf.make_addplot(volume_ma, panel=2, color='brown', width=2, ylabel='成交量')
        ]
        
        fig, axes = mpf.plot(
            data,
            type='candle',
            style=self.custom_style,
            title=title,
            ylabel='价格',
            volume=True,  # 成交量柱状图
            addplot=addplots,
            panel_ratios=(4, 1.5, 1.5),  # 主图:RSI:成交量 = 4:1.5:1.5
            figsize=figsize,
            returnfig=True
        )
        
        # 格式化坐标轴
        for i, ax in enumerate(axes):
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.tick_params(axis='both', labelsize=10)
            
            if i == 0:  # K线主图
                ax.set_ylabel('价格 (元)', fontsize=12)
            elif i == 1:  # RSI面板
                # 添加参考线
                ax.axhline(y=70, color='red', linestyle='--', alpha=0.6, linewidth=1.5, label='超买线(70)')
                ax.axhline(y=30, color='green', linestyle='--', alpha=0.6, linewidth=1.5, label='超卖线(30)')
                ax.axhline(y=50, color='gray', linestyle='-', alpha=0.3, linewidth=0.8)
                ax.set_ylim(0, 100)
                ax.set_ylabel('RSI (%)', fontsize=12)
                # 添加RSI区域填充
                ax.fill_between(range(len(rsi_data)), 70, 100, alpha=0.1, color='red', label='超买区')
                ax.fill_between(range(len(rsi_data)), 0, 30, alpha=0.1, color='green', label='超卖区')
                # 添加图例
                ax.text(0.02, 0.95, 'RSI(14)', transform=ax.transAxes, fontsize=10, 
                       bbox=dict(boxstyle='round', facecolor='purple', alpha=0.3))
                ax.text(0.02, 0.85, '超买>70', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='red', alpha=0.3))
                ax.text(0.02, 0.75, '超卖<30', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='green', alpha=0.3))
            elif i == 2:  # 成交量面板
                ax.set_ylabel('成交量 (手)', fontsize=12)
                ax.text(0.02, 0.95, 'Volume', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='gray', alpha=0.3))
                ax.text(0.02, 0.85, 'MA5', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='brown', alpha=0.3))
        
        if save_path:
            ensure_directory_exists(os.path.dirname(save_path))
            fig.savefig(save_path, bbox_inches='tight', dpi=300)
        
        return fig, axes
    
    def plot_comprehensive_chart(self, data, indicators_data, title="综合技术分析图", figsize=(15, 12), save_path=None):
        """
        绘制综合技术分析图（包含多个技术指标）
        
        Parameters:
        data: DataFrame - 包含OHLCV数据的DataFrame  
        indicators_data: dict - 包含各种技术指标的字典
        title: str - 图表标题
        figsize: tuple - 图表大小
        save_path: str - 保存路径
        
        Returns:
        tuple - (fig, axes) 图表对象
        """
        addplots = []
        
        # 添加移动平均线
        if 'ma_data' in indicators_data:
            ma_colors = ['blue', 'orange', 'purple', 'brown']
            for i, (ma_name, ma_series) in enumerate(indicators_data['ma_data'].items()):
                if not ma_series.isna().all():
                    color = ma_colors[i % len(ma_colors)]
                    addplots.append(mpf.make_addplot(ma_series, color=color, width=1))
        
        # 添加布林带
        if 'bollinger_data' in indicators_data:
            bb_data = indicators_data['bollinger_data']
            addplots.extend([
                mpf.make_addplot(bb_data['BB_Upper'], color='red', linestyle='--', width=1, alpha=0.6),
                mpf.make_addplot(bb_data['BB_Middle'], color='blue', linestyle='-', width=1),
                mpf.make_addplot(bb_data['BB_Lower'], color='green', linestyle='--', width=1, alpha=0.6)
            ])
        
        # 添加MACD
        if 'macd_data' in indicators_data:
            macd_data = indicators_data['macd_data']
            histogram = macd_data['Histogram']
            histogram_positive = histogram.copy()
            histogram_positive[histogram_positive < 0] = np.nan
            histogram_negative = histogram.copy()  
            histogram_negative[histogram_negative >= 0] = np.nan
            
            addplots.extend([
                mpf.make_addplot(macd_data['MACD'], panel=1, color='red', width=1.5),
                mpf.make_addplot(macd_data['Signal'], panel=1, color='blue', width=1.5),
                mpf.make_addplot(histogram_positive, panel=1, type='bar', width=0.8, color='red', alpha=0.8),
                mpf.make_addplot(histogram_negative, panel=1, type='bar', width=0.8, color='green', alpha=0.8)
            ])
        
        # 添加KDJ和RSI
        if 'kdj_data' in indicators_data:
            kdj_data = indicators_data['kdj_data']
            addplots.extend([
                mpf.make_addplot(kdj_data['K'], panel=2, color='blue', width=1),
                mpf.make_addplot(kdj_data['D'], panel=2, color='orange', width=1),
                mpf.make_addplot(kdj_data['J'], panel=2, color='red', width=1)
            ])
        
        if 'rsi_data' in indicators_data:
            rsi_data = indicators_data['rsi_data']
            addplots.append(mpf.make_addplot(rsi_data, panel=3, color='purple', width=1.5))
        
        # 确定面板比例
        panel_count = 1  # 主图
        if 'macd_data' in indicators_data:
            panel_count += 1
        if 'kdj_data' in indicators_data:
            panel_count += 1
        if 'rsi_data' in indicators_data:
            panel_count += 1
        
        panel_ratios = [3] + [1] * (panel_count - 1)  # 主图占3，其他每个占1
        
        fig, axes = mpf.plot(
            data,
            type='candle',
            style=self.custom_style,
            title=title,
            ylabel='价格',
            volume=True,
            addplot=addplots,
            panel_ratios=panel_ratios,
            figsize=figsize,
            returnfig=True
        )
        
        # 格式化各个面板
        panel_labels = ['价格', 'MACD', 'KDJ', 'RSI']
        for i, ax in enumerate(axes[:-1]):  # 除了成交量面板
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.tick_params(axis='both', labelsize=10)
            
            if i < len(panel_labels):
                ax.set_ylabel(panel_labels[i], fontsize=12)
            
            # 为指标面板添加参考线
            if i == 1 and 'macd_data' in indicators_data:  # MACD面板
                ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.8)
            elif i == 2 and 'kdj_data' in indicators_data:  # KDJ面板
                ax.axhline(y=80, color='red', linestyle='--', alpha=0.5)
                ax.axhline(y=20, color='green', linestyle='--', alpha=0.5)
            elif i == 3 and 'rsi_data' in indicators_data:  # RSI面板
                ax.axhline(y=70, color='red', linestyle='--', alpha=0.5)
                ax.axhline(y=30, color='green', linestyle='--', alpha=0.5)
        
        if save_path:
            ensure_directory_exists(os.path.dirname(save_path))
            fig.savefig(save_path, bbox_inches='tight', dpi=300)
        
        return fig, axes


def plot_kline_chart(data, chart_type='basic', indicators_data=None, title=None, save_path=None):
    """
    便捷函数：绘制K线图
    
    Parameters:
    data: DataFrame - 股票数据
    chart_type: str - 图表类型 ('basic', 'ma', 'bollinger', 'macd_volume', 'comprehensive')
    indicators_data: dict - 技术指标数据
    title: str - 图表标题
    save_path: str - 保存路径
    
    Returns:
    tuple - (fig, axes) 图表对象
    """
    renderer = KLineChartRenderer()
    
    if title is None:
        title = f"K线图 - {chart_type.upper()}"
    
    if chart_type == 'basic':
        return renderer.plot_basic_kline(data, title, save_path=save_path)
    elif chart_type == 'ma' and indicators_data:
        return renderer.plot_kline_with_ma(data, indicators_data, title, save_path=save_path)
    elif chart_type == 'bollinger' and indicators_data:
        return renderer.plot_kline_with_bollinger(data, indicators_data, title, save_path=save_path)
    elif chart_type == 'macd_volume' and indicators_data:
        return renderer.plot_kline_with_macd_volume(data, indicators_data, title, save_path=save_path)
    elif chart_type == 'comprehensive' and indicators_data:
        return renderer.plot_comprehensive_chart(data, indicators_data, title, save_path=save_path)
    else:
        return renderer.plot_basic_kline(data, title, save_path=save_path)


if __name__ == "__main__":
    # 测试代码
    from data.data_loader import get_stock_data
    from indicators.ma_system import calculate_ma_system
    from indicators.macd import analyze_macd
    
    try:
        # 获取测试数据
        df = get_stock_data()
        print("开始测试K线图绘制...")
        
        # 计算技术指标
        ma_system, _ = calculate_ma_system(df)
        macd_indicator, _, _ = analyze_macd(df)
        
        # 创建渲染器
        renderer = KLineChartRenderer()
        
        # 测试基础K线图
        print("绘制基础K线图...")
        fig1, axes1 = renderer.plot_basic_kline(df, "测试 - 基础K线图")
        plt.show()
        
        # 测试带移动平均线的K线图
        print("绘制带移动平均线的K线图...")
        fig2, axes2 = renderer.plot_kline_with_ma(df, ma_system.ma_data, "测试 - K线图+移动平均线")
        plt.show()
        
        # 测试MACD+成交量图
        print("绘制MACD+成交量图...")
        fig3, axes3 = renderer.plot_kline_with_macd_volume(df, macd_indicator.macd_data, "测试 - K线图+MACD+成交量")
        plt.show()
        
        print("K线图绘制测试完成！")
        
    except Exception as e:
        print(f"测试失败：{str(e)}")
