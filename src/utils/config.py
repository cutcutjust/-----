"""
配置文件 - 管理项目的核心配置参数
"""

# Tushare配置
TUSHARE_TOKEN_FILE = "Tushare/key.txt"
DEFAULT_STOCK_CODE = "600000.SH"  # 浦发银行作为默认股票

# 日期配置
DEFAULT_START_DATE = "20240101"
DEFAULT_END_DATE = "20241201"

# 技术指标参数
MA_PERIODS = {
    'sma': [5, 10, 20, 60],  # 简单移动平均线周期
    'ema': [12, 26]          # 指数移动平均线周期
}

BOLLINGER_CONFIG = {
    'period': 20,     # 布林带周期
    'std_dev': 2      # 标准差倍数
}

KDJ_CONFIG = {
    'fastk_period': 9,
    'slowk_period': 3,
    'slowd_period': 3
}

RSI_CONFIG = {
    'period': 14      # RSI周期
}

MACD_CONFIG = {
    'fast_period': 12,
    'slow_period': 26,
    'signal_period': 9
}

# 图表样式配置
CHART_STYLE = {
    'up_color': 'red',      # 上涨颜色
    'down_color': 'green',  # 下跌颜色
    'edge_color': 'black',  # 边框颜色
    'wick_color': 'black',  # 影线颜色
    'font_family': 'SimHei', # 中文字体
    'figure_dpi': 300       # 图片清晰度
}

# 文件路径配置
PATHS = {
    'data': 'data/',
    'charts': 'output/charts/',
    'reports': 'output/reports/'
}
