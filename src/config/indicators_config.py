"""
Indicator configuration and metadata for all supported Backtrader indicators
"""

INDICATOR_CONFIGS = {
    # Momentum Indicators
    'RSI': {
        'class': 'RSI',
        'description': 'Relative Strength Index - Momentum oscillator',
        'params': {
            'period': {'default': 14, 'min': 2, 'max': 100, 'type': 'int', 'description': 'Period for RSI calculation'},
        },
        'range': (0, 100),
        'lines': ['rsi'],
        'category': 'momentum'
    },
    
    'CCI': {
        'class': 'CCI',
        'description': 'Commodity Channel Index - Identifies cyclical trends',
        'params': {
            'period': {'default': 14, 'min': 5, 'max': 50, 'type': 'int', 'description': 'Period for CCI calculation'},
        },
        'range': (-200, 200),
        'lines': ['cci'],
        'category': 'momentum'
    },
    
    'Stochastic': {
        'class': 'Stochastic',
        'description': 'Stochastic Oscillator - Momentum indicator',
        'params': {
            'period': {'default': 14, 'min': 5, 'max': 50, 'type': 'int', 'description': 'Period for calculation'},
            'period_dfast': {'default': 3, 'min': 1, 'max': 10, 'type': 'int', 'description': 'Fast %D period'},
            'period_dslow': {'default': 3, 'min': 1, 'max': 10, 'type': 'int', 'description': 'Slow %D period'},
        },
        'range': (0, 100),
        'lines': ['percK', 'percD'],
        'category': 'momentum'
    },
    
    'Williams': {
        'class': 'WilliamsR',
        'description': 'Williams %R - Momentum indicator',
        'params': {
            'period': {'default': 14, 'min': 5, 'max': 50, 'type': 'int', 'description': 'Period for calculation'},
        },
        'range': (-100, 0),
        'lines': ['percR'],
        'category': 'momentum'
    },
    
    'ROC': {
        'class': 'ROC',
        'description': 'Rate of Change - Momentum oscillator',
        'params': {
            'period': {'default': 12, 'min': 1, 'max': 100, 'type': 'int', 'description': 'Period for ROC calculation'},
        },
        'range': None,
        'lines': ['roc'],
        'category': 'momentum'
    },
    
    # Trend Indicators
    'SMA': {
        'class': 'SMA',
        'description': 'Simple Moving Average - Trend following',
        'params': {
            'period': {'default': 20, 'min': 2, 'max': 200, 'type': 'int', 'description': 'Period for average'},
        },
        'range': None,
        'lines': ['sma'],
        'category': 'trend'
    },
    
    'EMA': {
        'class': 'EMA',
        'description': 'Exponential Moving Average - Weighted trend',
        'params': {
            'period': {'default': 20, 'min': 2, 'max': 200, 'type': 'int', 'description': 'Period for average'},
        },
        'range': None,
        'lines': ['ema'],
        'category': 'trend'
    },
    
    'WMA': {
        'class': 'WMA',
        'description': 'Weighted Moving Average - Weighted trend',
        'params': {
            'period': {'default': 20, 'min': 2, 'max': 200, 'type': 'int', 'description': 'Period for average'},
        },
        'range': None,
        'lines': ['wma'],
        'category': 'trend'
    },
    
    'DEMA': {
        'class': 'DEMA',
        'description': 'Double Exponential Moving Average',
        'params': {
            'period': {'default': 20, 'min': 2, 'max': 200, 'type': 'int', 'description': 'Period for average'},
        },
        'range': None,
        'lines': ['dema'],
        'category': 'trend'
    },
    
    'TEMA': {
        'class': 'TEMA',
        'description': 'Triple Exponential Moving Average',
        'params': {
            'period': {'default': 20, 'min': 2, 'max': 200, 'type': 'int', 'description': 'Period for average'},
        },
        'range': None,
        'lines': ['tema'],
        'category': 'trend'
    },
    
    'ADX': {
        'class': 'ADX',
        'description': 'Average Directional Index - Trend strength',
        'params': {
            'period': {'default': 14, 'min': 5, 'max': 50, 'type': 'int', 'description': 'Period for ADX calculation'},
        },
        'range': (0, 100),
        'lines': ['adx', 'plusDI', 'minusDI'],
        'category': 'trend'
    },
    
    'MACD': {
        'class': 'MACD',
        'description': 'Moving Average Convergence Divergence',
        'params': {
            'period_me1': {'default': 12, 'min': 5, 'max': 50, 'type': 'int', 'description': 'Fast EMA period'},
            'period_me2': {'default': 26, 'min': 10, 'max': 100, 'type': 'int', 'description': 'Slow EMA period'},
            'period_signal': {'default': 9, 'min': 3, 'max': 50, 'type': 'int', 'description': 'Signal line period'},
        },
        'range': None,
        'lines': ['macd', 'signal', 'histo'],
        'category': 'trend'
    },
    
    'Ichimoku': {
        'class': 'Ichimoku',
        'description': 'Ichimoku Cloud - Comprehensive trend system',
        'params': {
            'tenkan': {'default': 9, 'min': 5, 'max': 20, 'type': 'int', 'description': 'Tenkan-sen period'},
            'kijun': {'default': 26, 'min': 20, 'max': 50, 'type': 'int', 'description': 'Kijun-sen period'},
            'senkou': {'default': 52, 'min': 40, 'max': 100, 'type': 'int', 'description': 'Senkou Span B period'},
            'senkou_lead': {'default': 26, 'min': 20, 'max': 50, 'type': 'int', 'description': 'Senkou lead period'},
            'chikou': {'default': 26, 'min': 20, 'max': 50, 'type': 'int', 'description': 'Chikou span period'},
        },
        'range': None,
        'lines': ['tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b', 'chikou_span'],
        'category': 'trend'
    },
    
    # Volatility Indicators
    'BollingerBands': {
        'class': 'BollingerBands',
        'description': 'Bollinger Bands - Volatility bands',
        'params': {
            'period': {'default': 20, 'min': 5, 'max': 50, 'type': 'int', 'description': 'Period for moving average'},
            'devfactor': {'default': 2.0, 'min': 0.5, 'max': 4.0, 'type': 'float', 'description': 'Standard deviation factor'},
        },
        'range': None,
        'lines': ['mid', 'top', 'bot'],
        'category': 'volatility'
    },
    
    'ATR': {
        'class': 'ATR',
        'description': 'Average True Range - Volatility measure',
        'params': {
            'period': {'default': 14, 'min': 5, 'max': 50, 'type': 'int', 'description': 'Period for ATR calculation'},
        },
        'range': None,
        'lines': ['atr'],
        'category': 'volatility'
    },
    
    'StandardDev': {
        'class': 'StandardDev',
        'description': 'Standard Deviation - Price volatility',
        'params': {
            'period': {'default': 20, 'min': 5, 'max': 100, 'type': 'int', 'description': 'Period for calculation'},
        },
        'range': None,
        'lines': ['stddev'],
        'category': 'volatility'
    },
    
    'Keltner': {
        'class': 'KeltnerChannel',
        'description': 'Keltner Channel - Volatility-based channel',
        'params': {
            'period': {'default': 20, 'min': 5, 'max': 50, 'type': 'int', 'description': 'EMA period'},
            'devfactor': {'default': 1.5, 'min': 0.5, 'max': 3.0, 'type': 'float', 'description': 'ATR multiplier'},
        },
        'range': None,
        'lines': ['mid', 'top', 'bot'],
        'category': 'volatility'
    },
    
    'DonchianChannel': {
        'class': 'DonchianChannels',
        'description': 'Donchian Channel - Price channel indicator',
        'params': {
            'period': {'default': 20, 'min': 5, 'max': 100, 'type': 'int', 'description': 'Period for high/low'},
        },
        'range': None,
        'lines': ['dch', 'dcm', 'dcl'],
        'category': 'volatility'
    },
    
    # Volume Indicators
    'OBV': {
        'class': 'OBV',
        'description': 'On Balance Volume - Volume trend',
        'params': {},
        'range': None,
        'lines': ['obv'],
        'category': 'volume'
    },
    
    'AD': {
        'class': 'AD',
        'description': 'Accumulation/Distribution - Volume flow',
        'params': {},
        'range': None,
        'lines': ['ad'],
        'category': 'volume'
    },
    
    'MFI': {
        'class': 'MFI',
        'description': 'Money Flow Index - Volume-weighted RSI',
        'params': {
            'period': {'default': 14, 'min': 5, 'max': 50, 'type': 'int', 'description': 'Period for MFI calculation'},
        },
        'range': (0, 100),
        'lines': ['mfi'],
        'category': 'volume'
    },
    
    'CMF': {
        'class': 'ChaikinMoneyFlow',
        'description': 'Chaikin Money Flow - Money flow indicator',
        'params': {
            'period': {'default': 20, 'min': 5, 'max': 50, 'type': 'int', 'description': 'Period for calculation'},
        },
        'range': (-1, 1),
        'lines': ['cmf'],
        'category': 'volume'
    },
    
    # Other Indicators
    'ParabolicSAR': {
        'class': 'ParabolicSAR',
        'description': 'Parabolic SAR - Stop and reverse system',
        'params': {
            'af': {'default': 0.02, 'min': 0.01, 'max': 0.1, 'type': 'float', 'description': 'Acceleration factor'},
            'afmax': {'default': 0.2, 'min': 0.1, 'max': 0.5, 'type': 'float', 'description': 'Maximum acceleration'},
        },
        'range': None,
        'lines': ['psar'],
        'category': 'other'
    },
    
    'Pivot': {
        'class': 'PivotPoint',
        'description': 'Pivot Points - Support/Resistance levels',
        'params': {},
        'range': None,
        'lines': ['p', 'r1', 'r2', 's1', 's2'],
        'category': 'other'
    },
    
    'ZigZag': {
        'class': 'ZigZag',
        'description': 'ZigZag - Filters out price movements',
        'params': {
            'retrace': {'default': 0.05, 'min': 0.01, 'max': 0.2, 'type': 'float', 'description': 'Retracement percentage'},
        },
        'range': None,
        'lines': ['zigzag'],
        'category': 'other'
    }
}

def get_indicator_by_category(category):
    """Get all indicators in a specific category"""
    return {k: v for k, v in INDICATOR_CONFIGS.items() if v['category'] == category}

def get_indicator_categories():
    """Get all unique indicator categories"""
    return list(set(ind['category'] for ind in INDICATOR_CONFIGS.values()))

def get_indicator_params(indicator_name):
    """Get parameter configuration for a specific indicator"""
    if indicator_name in INDICATOR_CONFIGS:
        return INDICATOR_CONFIGS[indicator_name]['params']
    return {}

def get_indicator_lines(indicator_name):
    """Get line names for a specific indicator"""
    if indicator_name in INDICATOR_CONFIGS:
        return INDICATOR_CONFIGS[indicator_name]['lines']
    return []