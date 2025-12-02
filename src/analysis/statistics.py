"""
统计分析模块 - 实现量化分析和统计报告
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# 添加父目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.config import PATHS
from utils.helpers import ensure_directory_exists, calculate_returns


class QuantitativeStatistics:
    """量化统计分析类"""
    
    def __init__(self, data):
        """
        初始化量化统计分析
        
        Parameters:
        data: DataFrame - 包含OHLCV数据的DataFrame
        """
        self.data = data.copy()
        self.returns = calculate_returns(data['Close'])
        
    def calculate_basic_stats(self):
        """
        计算基础统计指标
        
        Returns:
        dict - 基础统计指标
        """
        close_prices = self.data['Close']
        
        # 价格统计
        price_stats = {
            'current_price': close_prices.iloc[-1],
            'max_price': close_prices.max(),
            'min_price': close_prices.min(),
            'avg_price': close_prices.mean(),
            'price_std': close_prices.std(),
            'price_range': close_prices.max() - close_prices.min()
        }
        
        # 收益率统计
        returns_stats = {
            'total_return': (close_prices.iloc[-1] / close_prices.iloc[0] - 1) * 100,
            'avg_daily_return': self.returns.mean() * 100,
            'return_volatility': self.returns.std() * 100,
            'max_daily_return': self.returns.max() * 100,
            'min_daily_return': self.returns.min() * 100,
            'positive_days': (self.returns > 0).sum(),
            'negative_days': (self.returns < 0).sum(),
            'win_rate': (self.returns > 0).mean() * 100
        }
        
        # 成交量统计
        volume_stats = {
            'avg_volume': self.data['Volume'].mean(),
            'max_volume': self.data['Volume'].max(),
            'min_volume': self.data['Volume'].min(),
            'volume_std': self.data['Volume'].std()
        }
        
        return {
            'price_stats': price_stats,
            'returns_stats': returns_stats,
            'volume_stats': volume_stats,
            'trading_days': len(self.data)
        }
    
    def calculate_risk_metrics(self):
        """
        计算风险指标
        
        Returns:
        dict - 风险指标
        """
        returns = self.returns
        
        # 最大回撤
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        # VaR (Value at Risk) - 95%置信度
        var_95 = np.percentile(returns, 5) * 100
        var_99 = np.percentile(returns, 1) * 100
        
        # 下行波动率
        negative_returns = returns[returns < 0]
        downside_volatility = negative_returns.std() * 100 if len(negative_returns) > 0 else 0
        
        # 夏普比率（简化版，假设无风险利率为0）
        sharpe_ratio = returns.mean() / returns.std() if returns.std() != 0 else 0
        
        # Calmar比率（年化收益率/最大回撤）
        annual_return = ((1 + returns.mean()) ** 252 - 1) * 100
        calmar_ratio = abs(annual_return / max_drawdown) if max_drawdown != 0 else 0
        
        return {
            'max_drawdown': max_drawdown,
            'var_95': var_95,
            'var_99': var_99,
            'downside_volatility': downside_volatility,
            'sharpe_ratio': sharpe_ratio,
            'calmar_ratio': calmar_ratio,
            'annual_return': annual_return,
            'annual_volatility': returns.std() * np.sqrt(252) * 100
        }
    
    def analyze_signal_performance(self, signals, holding_days=5):
        """
        分析交易信号的表现
        
        Parameters:
        signals: dict - 包含交易信号的字典
        holding_days: int - 持有天数
        
        Returns:
        dict - 信号表现分析
        """
        performance_results = {}
        
        for signal_name, signal_series in signals.items():
            if isinstance(signal_series, pd.Series) and signal_series.dtype == bool:
                signal_returns = self._calculate_signal_returns(signal_series, holding_days)
                performance_results[signal_name] = signal_returns
        
        return performance_results
    
    def _calculate_signal_returns(self, signal_series, holding_days):
        """
        计算特定信号的收益率
        
        Parameters:
        signal_series: Series - 布尔类型的信号序列
        holding_days: int - 持有天数
        
        Returns:
        dict - 信号收益率统计
        """
        signal_points = signal_series[signal_series].index
        returns_list = []
        
        for signal_date in signal_points:
            # 找到信号在数据中的位置
            try:
                signal_idx = self.data.index.get_loc(signal_date)
                
                # 确保有足够的后续数据
                if signal_idx + holding_days < len(self.data):
                    entry_price = self.data['Close'].iloc[signal_idx]
                    exit_price = self.data['Close'].iloc[signal_idx + holding_days]
                    
                    return_rate = (exit_price - entry_price) / entry_price
                    returns_list.append(return_rate)
            except (KeyError, IndexError):
                continue
        
        if returns_list:
            avg_return = np.mean(returns_list) * 100
            win_rate = sum(1 for r in returns_list if r > 0) / len(returns_list) * 100
            max_return = np.max(returns_list) * 100
            min_return = np.min(returns_list) * 100
        else:
            avg_return = win_rate = max_return = min_return = 0
        
        return {
            'signal_count': len(returns_list),
            'avg_return': avg_return,
            'win_rate': win_rate,
            'max_return': max_return,
            'min_return': min_return,
            'total_trades': len(signal_points)
        }
    
    def generate_performance_report(self, indicators_data=None, signals_data=None):
        """
        生成综合表现报告
        
        Parameters:
        indicators_data: dict - 技术指标数据
        signals_data: dict - 交易信号数据
        
        Returns:
        dict - 综合表现报告
        """
        report = {
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stock_symbol': 'N/A',  # 可以从外部传入
            'analysis_period': {
                'start_date': self.data.index[0].strftime('%Y-%m-%d'),
                'end_date': self.data.index[-1].strftime('%Y-%m-%d'),
                'trading_days': len(self.data)
            }
        }
        
        # 基础统计
        report['basic_stats'] = self.calculate_basic_stats()
        
        # 风险指标
        report['risk_metrics'] = self.calculate_risk_metrics()
        
        # 信号分析
        if signals_data:
            report['signal_performance'] = self.analyze_signal_performance(signals_data)
        
        # 技术指标摘要
        if indicators_data:
            report['indicators_summary'] = self._summarize_indicators(indicators_data)
        
        return report
    
    def _summarize_indicators(self, indicators_data):
        """
        总结技术指标状态
        
        Parameters:
        indicators_data: dict - 技术指标数据
        
        Returns:
        dict - 技术指标摘要
        """
        summary = {}
        
        # 移动平均线摘要
        if 'ma_data' in indicators_data:
            ma_data = indicators_data['ma_data']
            current_price = self.data['Close'].iloc[-1]
            
            above_ma_count = 0
            total_ma_count = 0
            
            for ma_name, ma_series in ma_data.items():
                if not ma_series.isna().iloc[-1]:
                    total_ma_count += 1
                    if current_price > ma_series.iloc[-1]:
                        above_ma_count += 1
            
            summary['moving_averages'] = {
                'above_ma_ratio': above_ma_count / max(1, total_ma_count),
                'trend_status': '多头排列' if above_ma_count / max(1, total_ma_count) > 0.6 else '空头排列'
            }
        
        # 布林带摘要
        if 'bollinger_data' in indicators_data:
            bb_data = indicators_data['bollinger_data']
            current_price = self.data['Close'].iloc[-1]
            
            upper = bb_data['BB_Upper'].iloc[-1]
            lower = bb_data['BB_Lower'].iloc[-1]
            
            if current_price > upper:
                bb_position = '突破上轨'
            elif current_price < lower:
                bb_position = '跌破下轨'
            else:
                bb_position = '区间内'
            
            summary['bollinger_bands'] = {
                'position': bb_position,
                'upper_band': upper,
                'lower_band': lower
            }
        
        # MACD摘要
        if 'macd_data' in indicators_data:
            macd_data = indicators_data['macd_data']
            
            summary['macd'] = {
                'macd_value': macd_data['MACD'].iloc[-1],
                'signal_value': macd_data['Signal'].iloc[-1],
                'histogram': macd_data['Histogram'].iloc[-1],
                'trend': '金叉' if macd_data['MACD'].iloc[-1] > macd_data['Signal'].iloc[-1] else '死叉'
            }
        
        return summary
    
    def save_report_to_file(self, report, filename=None):
        """
        保存报告到文件
        
        Parameters:
        report: dict - 报告数据
        filename: str - 文件名，默认使用时间戳
        
        Returns:
        str - 保存的文件路径
        """
        if filename is None:
            filename = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        filepath = os.path.join(PATHS['reports'], filename)
        ensure_directory_exists(os.path.dirname(filepath))
        
        with open(filepath, 'w', encoding='utf-8') as f:
            self._write_report_content(f, report)
        
        return filepath
    
    def _write_report_content(self, file, report):
        """
        写入报告内容
        
        Parameters:
        file: file object - 文件对象
        report: dict - 报告数据
        """
        file.write("=" * 80 + "\n")
        file.write("量化分析报告\n")
        file.write("=" * 80 + "\n")
        file.write(f"生成时间: {report['report_date']}\n")
        file.write(f"股票代码: {report['stock_symbol']}\n")
        file.write(f"分析期间: {report['analysis_period']['start_date']} 至 {report['analysis_period']['end_date']}\n")
        file.write(f"交易天数: {report['analysis_period']['trading_days']} 天\n\n")
        
        # 基础统计
        file.write("-" * 40 + " 基础统计 " + "-" * 40 + "\n")
        price_stats = report['basic_stats']['price_stats']
        returns_stats = report['basic_stats']['returns_stats']
        
        file.write(f"当前价格: {price_stats['current_price']:.2f}\n")
        file.write(f"最高价格: {price_stats['max_price']:.2f}\n")
        file.write(f"最低价格: {price_stats['min_price']:.2f}\n")
        file.write(f"平均价格: {price_stats['avg_price']:.2f}\n")
        file.write(f"总收益率: {returns_stats['total_return']:+.2f}%\n")
        file.write(f"平均日收益率: {returns_stats['avg_daily_return']:+.4f}%\n")
        file.write(f"收益波动率: {returns_stats['return_volatility']:.4f}%\n")
        file.write(f"胜率: {returns_stats['win_rate']:.1f}%\n\n")
        
        # 风险指标
        file.write("-" * 40 + " 风险指标 " + "-" * 40 + "\n")
        risk_metrics = report['risk_metrics']
        
        file.write(f"最大回撤: {risk_metrics['max_drawdown']:-.2f}%\n")
        file.write(f"VaR(95%): {risk_metrics['var_95']:-.2f}%\n")
        file.write(f"夏普比率: {risk_metrics['sharpe_ratio']:.4f}\n")
        file.write(f"年化收益率: {risk_metrics['annual_return']:+.2f}%\n")
        file.write(f"年化波动率: {risk_metrics['annual_volatility']:.2f}%\n\n")
        
        # 信号表现
        if 'signal_performance' in report:
            file.write("-" * 40 + " 信号表现 " + "-" * 40 + "\n")
            for signal_name, performance in report['signal_performance'].items():
                file.write(f"\n{signal_name}:\n")
                file.write(f"  信号总数: {performance['total_trades']}\n")
                file.write(f"  有效交易: {performance['signal_count']}\n")
                file.write(f"  平均收益: {performance['avg_return']:+.2f}%\n")
                file.write(f"  胜率: {performance['win_rate']:.1f}%\n")
            file.write("\n")
        
        # 技术指标摘要
        if 'indicators_summary' in report:
            file.write("-" * 40 + " 技术指标摘要 " + "-" * 40 + "\n")
            summary = report['indicators_summary']
            
            if 'moving_averages' in summary:
                ma_info = summary['moving_averages']
                file.write(f"均线状态: {ma_info['trend_status']} (多头排列比例: {ma_info['above_ma_ratio']:.0%})\n")
            
            if 'macd' in summary:
                macd_info = summary['macd']
                file.write(f"MACD状态: {macd_info['trend']} (MACD: {macd_info['macd_value']:.4f})\n")
            
            if 'bollinger_bands' in summary:
                bb_info = summary['bollinger_bands']
                file.write(f"布林带位置: {bb_info['position']}\n")


def generate_comprehensive_analysis(data, indicators_data=None, signals_data=None):
    """
    便捷函数：生成综合分析报告
    
    Parameters:
    data: DataFrame - 股票数据
    indicators_data: dict - 技术指标数据
    signals_data: dict - 交易信号数据
    
    Returns:
    tuple - (statistics, report, report_path) - 统计对象、报告和保存路径
    """
    statistics = QuantitativeStatistics(data)
    report = statistics.generate_performance_report(indicators_data, signals_data)
    report_path = statistics.save_report_to_file(report)
    
    return statistics, report, report_path


if __name__ == "__main__":
    # 测试代码
    from data.data_loader import get_stock_data
    
    try:
        # 获取测试数据
        df = get_stock_data()
        print("开始测试统计分析...")
        
        # 创建统计分析
        stats = QuantitativeStatistics(df)
        
        # 基础统计
        basic_stats = stats.calculate_basic_stats()
        print(f"总收益率: {basic_stats['returns_stats']['total_return']:.2f}%")
        print(f"胜率: {basic_stats['returns_stats']['win_rate']:.1f}%")
        
        # 风险指标
        risk_metrics = stats.calculate_risk_metrics()
        print(f"最大回撤: {risk_metrics['max_drawdown']:.2f}%")
        print(f"夏普比率: {risk_metrics['sharpe_ratio']:.4f}")
        
        # 生成完整报告
        report = stats.generate_performance_report()
        
        # 保存报告
        report_path = stats.save_report_to_file(report)
        print(f"\n报告已保存到: {report_path}")
        
        print("\n统计分析测试完成！")
        
    except Exception as e:
        print(f"测试失败：{str(e)}")
