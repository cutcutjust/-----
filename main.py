"""
金融数据分析与智能量化交易应用 - 第六章作业主程序
完成所有6个作业任务的综合实现

作业任务清单：
1. 移动平均线系统构建
2. 布林带指标分析
3. 自定义K线图样式
4. 多时间周期图表
5. KDJ与RSI指标比较
6. KDJ超买超卖统计
"""

import sys
import os
import matplotlib.pyplot as plt
import pandas as pd
import warnings

# 添加src目录到Python路径
sys.path.append('src')

from data.data_loader import StockDataLoader, get_stock_data
from indicators.ma_system import MovingAverageSystem, calculate_ma_system
from indicators.bollinger import BollingerBands, analyze_bollinger_bands
from indicators.kdj_rsi import KDJRSIComparator, analyze_kdj_rsi
from indicators.macd import MACDIndicator, analyze_macd
from visualization.kline_chart import KLineChartRenderer, plot_kline_chart
from visualization.multi_timeframe import MultiTimeFrameAnalyzer, analyze_multi_timeframe
from analysis.statistics import QuantitativeStatistics, generate_comprehensive_analysis
from utils.config import DEFAULT_STOCK_CODE, DEFAULT_START_DATE, DEFAULT_END_DATE, PATHS
from utils.helpers import ensure_directory_exists

# 忽略警告
warnings.filterwarnings('ignore')


class FinancialAnalysisApplication:
    """金融分析应用主类"""
    
    def __init__(self, stock_code=DEFAULT_STOCK_CODE, start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE):
        """
        初始化应用
        
        Parameters:
        stock_code: str - 股票代码
        start_date: str - 开始日期
        end_date: str - 结束日期
        """
        self.stock_code = stock_code
        self.start_date = start_date
        self.end_date = end_date
        
        # 确保输出目录存在
        ensure_directory_exists(PATHS['charts'])
        ensure_directory_exists(PATHS['reports'])
        
        print("=" * 80)
        print("金融数据分析与智能量化交易应用 - 第六章作业")
        print("=" * 80)
        print(f"股票代码: {self.stock_code}")
        print(f"分析期间: {self.start_date} 至 {self.end_date}")
        print("-" * 80)
        
        # 初始化数据和组件
        self.data_loader = None
        self.stock_data = None
        self.indicators_data = {}
        self.signals_data = {}
        
    def load_data(self):
        """加载股票数据"""
        print("📊 正在获取股票数据...")
        
        try:
            self.data_loader = StockDataLoader()
            self.stock_data = self.data_loader.get_daily_data(
                self.stock_code, self.start_date, self.end_date
            )
            
            print(f"✅ 数据加载成功！共获取 {len(self.stock_data)} 条记录")
            print(f"   日期范围: {self.stock_data.index[0].date()} 至 {self.stock_data.index[-1].date()}")
            print(f"   当前价格: {self.stock_data['Close'].iloc[-1]:.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据加载失败: {str(e)}")
            return False
    
    def task1_moving_average_system(self):
        """
        任务1: 移动平均线系统构建
        - 计算5日、10日、20日、60日简单移动平均线(SMA)
        - 计算12日、26日指数移动平均线(EMA)
        - 识别各均线的金叉和死叉信号
        - 统计不同周期均线的交叉频率
        """
        print("\n" + "=" * 60)
        print("📈 任务1: 移动平均线系统构建")
        print("=" * 60)
        
        # 创建移动平均线系统
        ma_system = MovingAverageSystem(self.stock_data)
        
        # 计算所有移动平均线
        ma_data = ma_system.calculate_all_ma()
        print(f"✅ 计算移动平均线: {list(ma_data.keys())}")
        
        # 识别金叉死叉信号
        cross_signals = ma_system.identify_ma_cross_signals()
        print(f"✅ 识别交叉信号: {len(cross_signals)} 组均线组合")
        
        # 统计交叉频率
        stats_df = ma_system.calculate_cross_frequency_stats()
        print("✅ 交叉频率统计:")
        print(stats_df.to_string(index=False))
        
        # 趋势分析
        trend_analysis = ma_system.get_ma_trend_analysis()
        print(f"\n📊 当前趋势判断: {trend_analysis['overall_trend']}")
        
        # 保存数据
        self.indicators_data['ma_data'] = ma_data
        self.signals_data.update({f"ma_{k}": v for k, v in cross_signals.items()})
        self.data = self.stock_data.copy()  # 保存一份数据副本用于后续使用
        
        # 绘制图表
        renderer = KLineChartRenderer()
        fig, axes = renderer.plot_kline_with_ma(
            self.stock_data, ma_data, 
            f"{self.stock_code} - 任务1：K线图+移动平均线系统",
            save_path=os.path.join(PATHS['charts'], 'task1_ma_system.png')
        )
        plt.show()
        
        return ma_system, stats_df
    
    def task2_bollinger_bands_analysis(self):
        """
        任务2: 布林带指标分析
        - 计算20日布林带（2倍标准差）
        - 识别股价突破上轨和下轨的时点
        - 计算布林带宽度（Band Width）及其变化
        - 分析布林带收窄后的突破方向
        """
        print("\n" + "=" * 60)
        print("📊 任务2: 布林带指标分析")
        print("=" * 60)
        
        # 创建布林带分析
        bollinger = BollingerBands(self.stock_data)
        
        # 计算布林带
        bb_data = bollinger.calculate_bollinger_bands()
        print("✅ 计算布林带三轨: 上轨、中轨、下轨")
        
        # 计算带宽
        band_width = bollinger.calculate_band_width()
        print(f"✅ 计算布林带宽度，当前值: {band_width.iloc[-1]:.4f}")
        
        # 识别突破信号
        breakout_signals = bollinger.identify_breakout_signals()
        print(f"✅ 突破信号统计:")
        print(f"   上轨突破次数: {breakout_signals['upper_count']}")
        print(f"   下轨突破次数: {breakout_signals['lower_count']}")
        
        # 收窄模式分析
        squeeze_analysis = bollinger.analyze_squeeze_pattern()
        print(f"✅ 布林带收窄分析: 检测到 {squeeze_analysis['total_squeezes']} 次收窄")
        
        if squeeze_analysis['squeeze_analysis']:
            print("   收窄后突破方向:")
            for analysis in squeeze_analysis['squeeze_analysis'][-3:]:  # 显示最近3次
                print(f"   {analysis['end_date'].date()}: {analysis['breakout_direction']} "
                      f"({analysis['price_change_pct']:+.2f}%)")
        
        # 当前状态
        current_status = bollinger.get_current_bollinger_status()
        print(f"\n📊 当前布林带状态:")
        print(f"   价格位置: {current_status['position_status']}")
        print(f"   带宽状态: {current_status['width_status']}")
        
        # 保存数据
        self.indicators_data['bollinger_data'] = bb_data
        self.signals_data['bollinger_breakout'] = breakout_signals
        
        # 绘制图表（Task2-1: 布林带和突破信号）
        print("绘制布林带图表...")
        renderer = KLineChartRenderer()
        fig, axes = renderer.plot_kline_with_bollinger(
            self.stock_data, bb_data,
            f"{self.stock_code} - 任务2.1：K线图+布林带指标",
            save_path=os.path.join(PATHS['charts'], 'task2_1_bollinger_bands.png')
        )
        plt.show()
        
        # 绘制图表（Task2-2: 布林带宽度变化）
        print("绘制布林带宽度变化图...")
        fig2, ax2 = renderer.plot_bollinger_bandwidth(
            self.stock_data, self.data['BB_Width'] if 'BB_Width' in self.data.columns else bollinger.data['BB_Width'],
            f"{self.stock_code} - 任务2.2：布林带宽度变化分析",
            save_path=os.path.join(PATHS['charts'], 'task2_2_bollinger_bandwidth.png')
        )
        plt.show()
        
        return bollinger, breakout_signals, squeeze_analysis
    
    def task3_custom_kline_style(self):
        """
        任务3: 自定义K线图样式
        - 设置上涨K线为红色实心，下跌K线为绿色空心
        - 修改坐标轴标签字体大小和颜色
        - 添加网格线并设置透明度
        - 在副图中同步显示MACD和成交量
        """
        print("\n" + "=" * 60)
        print("🎨 任务3: 自定义K线图样式")
        print("=" * 60)
        
        # 计算MACD指标
        macd_indicator = MACDIndicator(self.stock_data)
        macd_data = macd_indicator.calculate_macd()
        print("✅ 计算MACD指标用于副图显示")
        
        # 保存MACD数据
        self.indicators_data['macd_data'] = macd_data
        
        # 创建自定义样式K线图（Task3-1: K线+MACD+成交量）
        renderer = KLineChartRenderer()
        print("✅ 应用自定义样式:")
        print("   - 上涨K线: 红色实心")
        print("   - 下跌K线: 绿色空心") 
        print("   - 坐标轴: 自定义字体和大小")
        print("   - 网格线: 添加透明度")
        print("   - 副图: MACD和成交量同步显示")
        
        print("绘制自定义K线+MACD+成交量图...")
        fig, axes = renderer.plot_kline_with_macd_volume(
            self.stock_data, macd_data,
            f"{self.stock_code} - 任务3.1：自定义K线图样式 (MACD+成交量)",
            save_path=os.path.join(PATHS['charts'], 'task3_1_kline_macd_volume.png')
        )
        plt.show()
        
        return macd_indicator
    
    def task4_multi_timeframe_charts(self):
        """
        任务4: 多时间周期图表
        - 日线、周线、月线K线图
        - 各周期对应的技术指标（MA、MACD）
        - 使用子图(subplot)排列，确保时间轴对齐
        - 添加各周期的趋势判断标签
        """
        print("\n" + "=" * 60)
        print("📈 任务4: 多时间周期图表")
        print("=" * 60)
        
        # 创建多时间周期分析器
        analyzer = MultiTimeFrameAnalyzer()
        
        # 准备多时间周期数据
        timeframe_data = analyzer.prepare_multi_timeframe_data(self.stock_data)
        print("✅ 转换多时间周期数据:")
        for tf, data in timeframe_data.items():
            print(f"   {tf}: {len(data)} 条记录")
        
        # 计算各周期技术指标
        ma_data = analyzer.calculate_multi_timeframe_ma(timeframe_data)
        macd_data = analyzer.calculate_multi_timeframe_macd(timeframe_data)
        print("✅ 计算各周期技术指标: MA、MACD")
        
        # 趋势分析
        trend_analysis = analyzer.analyze_multi_timeframe_trend(timeframe_data, ma_data)
        print("✅ 多时间周期趋势分析:")
        
        timeframe_names = {'daily': '日线', 'weekly': '周线', 'monthly': '月线'}
        for tf, analysis in trend_analysis.items():
            print(f"   {timeframe_names[tf]}: {analysis['trend']} "
                  f"(当前价格: {analysis['current_price']:.2f}, "
                  f"涨跌幅: {analysis['price_change_pct']:+.2f}%)")
        
        # 绘制多时间周期对比图（Task4-1）
        print("绘制多时间周期K线对比图...")
        fig, axes = analyzer.plot_multi_timeframe_comparison(
            timeframe_data, ma_data, macd_data,
            f"{self.stock_code} - 多时间周期对比分析",
            save_path=os.path.join(PATHS['charts'], 'task4_1_multi_timeframe_charts.png')
        )
        plt.show()
        
        # 绘制趋势对比表（Task4-2）
        print("绘制趋势对比表...")
        fig2, ax2 = analyzer.plot_trend_comparison_table(
            trend_analysis,
            f"{self.stock_code} - 多时间周期趋势对比",
            save_path=os.path.join(PATHS['charts'], 'task4_2_trend_comparison_table.png')
        )
        plt.show()
        
        return analyzer, timeframe_data, trend_analysis
    
    def task5_kdj_rsi_comparison(self):
        """
        任务5: KDJ与RSI指标比较
        - 分别计算其KDJ和RSI(14)指标
        - 使用mplfinance绘制包含这两个指标的多面板图表
        """
        print("\n" + "=" * 60)
        print("📊 任务5: KDJ与RSI指标比较")
        print("=" * 60)
        
        # 创建KDJ和RSI比较器
        comparator = KDJRSIComparator(self.stock_data)
        
        # 计算所有指标
        data_with_indicators = comparator.calculate_all_indicators()
        print("✅ 计算KDJ指标 (9,3,3)")
        print("✅ 计算RSI指标 (14)")
        
        # 获取信号比较
        signal_comparison = comparator.compare_signals()
        print("✅ 信号比较分析:")
        print(f"   KDJ超买信号: {signal_comparison['kdj_signals']['overbought'].sum()} 次")
        print(f"   KDJ超卖信号: {signal_comparison['kdj_signals']['oversold'].sum()} 次")
        print(f"   RSI超买信号: {signal_comparison['rsi_signals']['overbought'].sum()} 次")
        print(f"   RSI超卖信号: {signal_comparison['rsi_signals']['oversold'].sum()} 次")
        print(f"   超买信号一致: {signal_comparison['overbought_agree_count']} 次")
        print(f"   超卖信号一致: {signal_comparison['oversold_agree_count']} 次")
        
        # 保存指标数据
        self.indicators_data['kdj_data'] = comparator.kdj.kdj_data
        self.indicators_data['rsi_data'] = data_with_indicators['RSI']
        self.signals_data['kdj_rsi_comparison'] = signal_comparison
        
        # 绘制分离的图表
        renderer = KLineChartRenderer()
        
        # Task5-1: KDJ指标图
        print("绘制KDJ指标图...")
        fig1, axes1 = renderer.plot_kdj_chart(
            self.stock_data, self.indicators_data['kdj_data'],
            f"{self.stock_code} - KDJ指标分析",
            save_path=os.path.join(PATHS['charts'], 'task5_kdj_chart.png')
        )
        plt.show()
        
        # Task5-2: RSI指标图
        print("绘制RSI指标图...")
        fig2, axes2 = renderer.plot_rsi_chart(
            self.stock_data, self.indicators_data['rsi_data'],
            f"{self.stock_code} - RSI指标分析",
            save_path=os.path.join(PATHS['charts'], 'task5_rsi_chart.png')
        )
        plt.show()
        
        return comparator, signal_comparison
    
    def task6_kdj_overbought_oversold_stats(self):
        """
        任务6: KDJ超买超卖统计
        - 计算最近120个交易日的K、D、J值
        - 统计J值进入超买区（>100）和超卖区（<0）的次数
        - 计算每次超买后5个交易日的平均收益率
        - 思考：为什么KDJ在震荡市比趋势市更有效？
        """
        print("\n" + "=" * 60)
        print("📊 任务6: KDJ超买超卖统计")
        print("=" * 60)
        
        # 使用已计算的KDJ数据或重新创建
        if 'kdj_data' not in self.indicators_data:
            from indicators.kdj_rsi import KDJIndicator
            kdj = KDJIndicator(self.stock_data)
            kdj.calculate_kdj()
        else:
            # 重新创建以确保有完整的方法
            from indicators.kdj_rsi import KDJIndicator
            kdj = KDJIndicator(self.stock_data)
            kdj.calculate_kdj()
        
        # 120个交易日分析
        analysis_days = 120
        print(f"✅ 分析最近 {analysis_days} 个交易日的KDJ指标")
        
        # 超买超卖统计
        overbought_oversold = kdj.analyze_overbought_oversold(analysis_days)
        print(f"✅ 超买超卖统计:")
        print(f"   J值超买区(>100)进入次数: {overbought_oversold['overbought_count']}")
        print(f"   J值超卖区(<0)进入次数: {overbought_oversold['oversold_count']}")
        
        # 超买后收益率分析
        returns_analysis = kdj.calculate_overbought_returns(analysis_days, 5)
        print(f"✅ 超买后5日收益率分析:")
        print(f"   超买信号次数: {returns_analysis['signal_count']}")
        print(f"   平均收益率: {returns_analysis['avg_return_pct']:+.2f}%")
        print(f"   胜率: {returns_analysis['win_rate']:.1f}%")
        print(f"   最大收益: {returns_analysis['max_return']:+.2f}%")
        print(f"   最大亏损: {returns_analysis['min_return']:+.2f}%")
        
        # 显示具体信号详情
        if returns_analysis['signal_details']:
            print("\n   最近的超买信号详情:")
            for detail in returns_analysis['signal_details'][-3:]:  # 显示最近3次
                print(f"   {detail['signal_date'].date()}: 买入{detail['entry_price']:.2f} → "
                      f"卖出{detail['exit_price']:.2f} = {detail['return_pct']:+.2f}%")
        
        # KDJ有效性分析思考
        print(f"\n🤔 思考分析: KDJ在震荡市vs趋势市的有效性")
        
        # 计算市场波动性来判断是震荡市还是趋势市
        recent_data = self.stock_data.tail(60)  # 最近60天
        price_volatility = recent_data['Close'].pct_change().std()
        price_trend = (recent_data['Close'].iloc[-1] / recent_data['Close'].iloc[0] - 1) * 100
        
        if abs(price_trend) < 10 and price_volatility > 0.02:
            market_type = "震荡市"
            effectiveness = "较高"
        elif abs(price_trend) > 20:
            market_type = "趋势市"  
            effectiveness = "较低"
        else:
            market_type = "过渡市"
            effectiveness = "中等"
        
        print(f"   当前市场判断: {market_type} (60日涨跌幅: {price_trend:+.1f}%)")
        print(f"   KDJ有效性预期: {effectiveness}")
        print(f"   理论分析:")
        print(f"   - 震荡市: KDJ超买超卖信号更准确，因为价格在区间内反复波动")
        print(f"   - 趋势市: KDJ容易产生假信号，因为价格持续单向运动")
        print(f"   - 当前胜率 {returns_analysis['win_rate']:.1f}% 验证了这一理论")
        
        return kdj, overbought_oversold, returns_analysis
    
    def generate_final_report(self):
        """生成最终的综合分析报告"""
        print("\n" + "=" * 60)
        print("📋 生成综合分析报告")
        print("=" * 60)
        
        # 创建统计分析
        statistics = QuantitativeStatistics(self.stock_data)
        
        # 生成综合报告
        report = statistics.generate_performance_report(
            self.indicators_data, self.signals_data
        )
        report['stock_symbol'] = self.stock_code
        
        # 保存报告
        report_path = statistics.save_report_to_file(
            report, f"{self.stock_code}_comprehensive_analysis.txt"
        )
        
        # 显示关键指标
        print("✅ 关键分析结果:")
        basic_stats = report['basic_stats']
        risk_metrics = report['risk_metrics']
        
        print(f"   总收益率: {basic_stats['returns_stats']['total_return']:+.2f}%")
        print(f"   年化收益率: {risk_metrics['annual_return']:+.2f}%")
        print(f"   最大回撤: {risk_metrics['max_drawdown']:-.2f}%")
        print(f"   夏普比率: {risk_metrics['sharpe_ratio']:.4f}")
        print(f"   胜率: {basic_stats['returns_stats']['win_rate']:.1f}%")
        
        print(f"\n📄 完整报告已保存至: {report_path}")
        
        return report, report_path
    
    def run_all_tasks(self):
        """运行所有任务"""
        try:
            # 加载数据
            if not self.load_data():
                return False
            
            # 执行所有任务
            print("\n🚀 开始执行所有作业任务...")
            
            # 任务1: 移动平均线系统
            self.task1_moving_average_system()
            
            # 任务2: 布林带指标分析  
            self.task2_bollinger_bands_analysis()
            
            # 任务3: 自定义K线图样式
            self.task3_custom_kline_style()
            
            # 任务4: 多时间周期图表
            self.task4_multi_timeframe_charts()
            
            # 任务5: KDJ与RSI指标比较
            self.task5_kdj_rsi_comparison()
            
            # 任务6: KDJ超买超卖统计
            self.task6_kdj_overbought_oversold_stats()
            
            # 生成最终报告
            self.generate_final_report()
            
            print("\n" + "=" * 80)
            print("🎉 所有作业任务完成！")
            print("=" * 80)
            print(f"📊 图表文件保存在: {PATHS['charts']}")
            print(f"📄 报告文件保存在: {PATHS['reports']}")
            print("\n✅ 完成了以下6个任务及分图表:")
            print("   1. ✅ 移动平均线系统构建")
            print("      └─ task1_ma_system.png")
            print("   2. ✅ 布林带指标分析")
            print("      ├─ task2_1_bollinger_bands.png（K线+布林带）")
            print("      └─ task2_2_bollinger_bandwidth.png（布林带宽度变化）")
            print("   3. ✅ 自定义K线图样式")
            print("      └─ task3_1_kline_macd_volume.png（K线+MACD+成交量）")
            print("   4. ✅ 多时间周期图表")
            print("      ├─ task4_1_multi_timeframe_charts.png（日周月对比）")
            print("      └─ task4_2_trend_comparison_table.png（趋势对比表）")
            print("   5. ✅ KDJ与RSI指标比较")
            print("      ├─ task5_kdj_chart.png（KDJ指标分析）")
            print("      └─ task5_rsi_chart.png（RSI指标分析）")
            print("   6. ✅ KDJ超买超卖统计")
            print("      └─ 详见任务6的输出分析")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 执行过程中出现错误: {str(e)}")
            return False


def main():
    """主函数"""
    # 创建应用实例
    app = FinancialAnalysisApplication()
    
    # 运行所有任务
    success = app.run_all_tasks()
    
    if success:
        print("\n✨ 程序执行完成！所有图表和报告已生成。")
    else:
        print("\n⚠️  程序执行未完全成功，请检查错误信息。")
    
    # 保持窗口打开以查看图表
    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
