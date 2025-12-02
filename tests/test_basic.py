"""
基础测试脚本 - 验证项目核心功能是否正常
"""

def test_imports():
    """测试导入是否正常"""
    print("🔍 测试模块导入...")
    
    try:
        import sys
        sys.path.append('src')
        
        # 测试核心模块导入
        from utils.config import DEFAULT_STOCK_CODE
        print("✅ 配置模块导入成功")
        
        from utils.helpers import load_tushare_token
        print("✅ 辅助函数模块导入成功")
        
        from data.data_loader import StockDataLoader
        print("✅ 数据获取模块导入成功")
        
        from indicators.ma_system import MovingAverageSystem
        print("✅ 移动平均线模块导入成功")
        
        from indicators.bollinger import BollingerBands
        print("✅ 布林带模块导入成功")
        
        from indicators.kdj_rsi import KDJIndicator
        print("✅ KDJ指标模块导入成功")
        
        from indicators.macd import MACDIndicator
        print("✅ MACD指标模块导入成功")
        
        from visualization.kline_chart import KLineChartRenderer
        print("✅ K线图模块导入成功")
        
        from analysis.statistics import QuantitativeStatistics
        print("✅ 统计分析模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        return False


def test_tushare_connection():
    """测试Tushare连接"""
    print("\n🔍 测试Tushare连接...")
    
    try:
        import sys
        sys.path.append('src')
        
        from utils.helpers import load_tushare_token
        
        # 检查token文件是否存在
        token = load_tushare_token()
        if token:
            print("✅ Tushare Token加载成功")
            
            # 测试连接
            import tushare as ts
            ts.set_token(token)
            pro = ts.pro_api()
            
            # 尝试获取少量数据测试连接
            test_df = pro.daily(ts_code='600000.SH', start_date='20241120', end_date='20241201')
            if not test_df.empty:
                print(f"✅ Tushare连接成功，测试数据: {len(test_df)} 条")
                return True
            else:
                print("⚠️  Tushare连接成功，但未获取到测试数据")
                return False
        else:
            print("❌ Tushare Token加载失败")
            return False
            
    except FileNotFoundError:
        print("❌ 请在 Tushare/key.txt 文件中配置您的API Token")
        return False
    except Exception as e:
        print(f"❌ Tushare连接失败: {str(e)}")
        return False


def test_dependencies():
    """测试依赖包是否安装"""
    print("\n🔍 测试依赖包...")
    
    required_packages = [
        'pandas', 'numpy', 'matplotlib', 'tushare', 'talib', 'mplfinance'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ 所有依赖包已安装")
        return True


def test_project_structure():
    """测试项目结构"""
    print("\n🔍 测试项目结构...")
    
    import os
    
    required_dirs = [
        'src/data', 'src/indicators', 'src/visualization', 
        'src/analysis', 'src/utils', 'Tushare', 'output/charts', 'output/reports'
    ]
    
    required_files = [
        'src/data/data_loader.py', 'src/indicators/ma_system.py',
        'src/indicators/bollinger.py', 'src/indicators/kdj_rsi.py',
        'src/indicators/macd.py', 'src/visualization/kline_chart.py',
        'src/utils/config.py', 'src/utils/helpers.py',
        'main.py', 'requirements.txt', 'README.md'
    ]
    
    # 检查目录
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - 不存在")
    
    # 检查文件
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 不存在")
    
    return True


def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 金融数据分析项目 - 基础测试")
    print("=" * 60)
    
    # 测试项目结构
    test_project_structure()
    
    # 测试依赖包
    deps_ok = test_dependencies()
    
    # 测试导入
    imports_ok = test_imports()
    
    # 测试Tushare连接
    tushare_ok = test_tushare_connection()
    
    print("\n" + "=" * 60)
    print("📋 测试结果总结")
    print("=" * 60)
    
    if deps_ok and imports_ok and tushare_ok:
        print("🎉 所有测试通过！项目可以正常运行。")
        print("\n▶️  运行主程序: python main.py")
        print("▶️  运行示例: python example.py")
        return True
    else:
        print("⚠️  部分测试未通过，请检查以上错误信息。")
        
        if not deps_ok:
            print("📦 请先安装依赖包: pip install -r requirements.txt")
        
        if not tushare_ok:
            print("🔑 请配置Tushare API Token到 Tushare/key.txt 文件")
        
        return False


if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n💡 配置帮助:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 配置Tushare:")
        print("   - 访问 https://tushare.pro 注册账号")
        print("   - 获取API Token")
        print("   - 将Token保存到 Tushare/key.txt 文件")
        print("3. 重新运行测试: python test_basic.py")
    
    input("\n按回车键退出...")
