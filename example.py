"""
金融数据分析项目使用示例
演示如何使用各个模块的核心功能
"""

import sys
sys.path.append('src')

from data.data_loader import get_stock_data
from indicators.ma_system import calculate_ma_system
from indicators.bollinger import analyze_bollinger_bands
from indicators.kdj_rsi import analyze_kdj_rsi
from visualization.kline_chart import plot_kline_chart
from analysis.statistics import generate_comprehensive_analysis


def example_basic_usage():
    """基础使用示例"""
    print("=== 金融数据分析项目 - 基础使用示例 ===\n")
    
    # 1. 获取股票数据
    print("1. 获取股票数据...")
    try:
        df = get_stock_data("600000.SH", "20240101", "20241201")
        print(f"   成功获取数据: {len(df)} 条记录")
        print(f"   时间范围: {df.index[0].date()} 至 {df.index[-1].date()}")
    except Exception as e:
        print(f"   数据获取失败: {e}")
        return
    
    # 2. 计算移动平均线系统
    print("\n2. 计算移动平均线系统...")
    try:
        ma_system, ma_stats = calculate_ma_system(df)
        print(f"   计算了 {len(ma_system.ma_data)} 条移动平均线")
        print("   交叉频率统计:")
        print(ma_stats.to_string(index=False))
    except Exception as e:
        print(f"   计算失败: {e}")
    
    # 3. 布林带分析
    print("\n3. 布林带指标分析...")
    try:
        bollinger, breakout, squeeze = analyze_bollinger_bands(df)
        print(f"   上轨突破: {breakout['upper_count']} 次")
        print(f"   下轨突破: {breakout['lower_count']} 次")
        print(f"   收窄次数: {squeeze['total_squeezes']} 次")
    except Exception as e:
        print(f"   分析失败: {e}")
    
    # 4. KDJ和RSI分析
    print("\n4. KDJ与RSI指标分析...")
    try:
        comparator, kdj_analysis, returns, comparison = analyze_kdj_rsi(df)
        print(f"   120天内KDJ超买: {kdj_analysis['overbought_count']} 次")
        print(f"   120天内KDJ超卖: {kdj_analysis['oversold_count']} 次")
        print(f"   超买后平均收益: {returns['avg_return_pct']:+.2f}%")
    except Exception as e:
        print(f"   分析失败: {e}")
    
    # 5. 绘制基础K线图
    print("\n5. 绘制K线图...")
    try:
        fig, axes = plot_kline_chart(df, 'basic', title="基础K线图示例")
        print("   K线图绘制成功")
        # plt.show()  # 注释掉以避免阻塞
    except Exception as e:
        print(f"   绘图失败: {e}")
    
    # 6. 生成统计报告
    print("\n6. 生成分析报告...")
    try:
        stats, report, report_path = generate_comprehensive_analysis(df)
        print(f"   报告生成成功: {report_path}")
        print(f"   总收益率: {report['basic_stats']['returns_stats']['total_return']:+.2f}%")
        print(f"   最大回撤: {report['risk_metrics']['max_drawdown']:-.2f}%")
    except Exception as e:
        print(f"   报告生成失败: {e}")
    
    print("\n=== 基础示例完成 ===")


def example_advanced_usage():
    """高级使用示例"""
    print("\n=== 高级使用示例：自定义分析 ===\n")
    
    # 获取数据
    try:
        df = get_stock_data()
        
        # 自定义技术指标组合分析
        from indicators.ma_system import MovingAverageSystem
        from indicators.macd import MACDIndicator
        
        # 创建移动平均线系统
        ma_system = MovingAverageSystem(df)
        ma_system.calculate_all_ma()
        
        # 创建MACD指标
        macd = MACDIndicator(df)
        macd.calculate_macd()
        
        # 综合信号分析
        ma_signals = ma_system.identify_ma_cross_signals()
        macd_signals = macd.identify_macd_signals()
        
        print("自定义信号统计:")
        print(f"  MA金叉信号: {sum(signals['golden_count'] for signals in ma_signals.values())}")
        print(f"  MACD金叉信号: {macd_signals['golden_count']}")
        
        # 趋势一致性分析
        trend_analysis = ma_system.get_ma_trend_analysis()
        macd_trend = macd.get_macd_trend_analysis()
        
        print(f"\n趋势一致性分析:")
        print(f"  MA系统趋势: {trend_analysis['overall_trend']}")
        print(f"  MACD趋势: {macd_trend['trend']}")
        
    except Exception as e:
        print(f"高级分析失败: {e}")


if __name__ == "__main__":
    # 运行基础示例
    example_basic_usage()
    
    # 运行高级示例
    example_advanced_usage()
    
    print("\n✅ 所有示例运行完成！")
