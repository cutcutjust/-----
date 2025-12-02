"""
快速测试脚本 - 验证修复是否成功
"""

import sys
sys.path.append('src')

import warnings
warnings.filterwarnings('ignore')

from data.data_loader import get_stock_data
from indicators.bollinger import BollingerBands

try:
    print("🧪 快速测试修复...")
    print("\n1️⃣  获取数据...")
    df = get_stock_data()
    print(f"✅ 数据获取成功: {len(df)} 条记录")
    
    print("\n2️⃣  测试布林带指标...")
    bollinger = BollingerBands(df)
    bollinger.calculate_bollinger_bands()
    print("✅ 计算布林带成功")
    
    print("\n3️⃣  测试布林带突破信号...")
    breakout = bollinger.identify_breakout_signals()
    print(f"✅ 识别突破信号成功")
    print(f"   上轨突破: {breakout['upper_count']} 次")
    print(f"   下轨突破: {breakout['lower_count']} 次")
    
    print("\n4️⃣  测试布林带收窄...")
    squeeze = bollinger.analyze_squeeze_pattern()
    print(f"✅ 收窄分析成功: {squeeze['total_squeezes']} 次")
    
    print("\n5️⃣  测试KDJ指标...")
    from indicators.kdj_rsi import KDJIndicator
    kdj = KDJIndicator(df)
    kdj.calculate_kdj()
    print("✅ 计算KDJ成功")
    
    print("\n6️⃣  测试KDJ超买超卖分析...")
    analysis = kdj.analyze_overbought_oversold(120)
    print(f"✅ 超买超卖分析成功")
    print(f"   超买次数: {analysis['overbought_count']}")
    print(f"   超卖次数: {analysis['oversold_count']}")
    
    print("\n7️⃣  测试KDJ收益率分析...")
    returns = kdj.calculate_overbought_returns(120, 5)
    print(f"✅ 收益率分析成功")
    print(f"   平均收益率: {returns['avg_return_pct']:+.2f}%")
    
    print("\n" + "="*50)
    print("🎉 所有测试通过！可以运行 python main.py")
    print("="*50)
    
except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()

