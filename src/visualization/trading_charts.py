"""
Advanced Trading Visualization Module
Uses Plotly for professional trading charts and analytics
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json

class TradingCharts:
    """
    Professional trading charts using Plotly
    """
    
    def __init__(self):
        """Initialize trading charts"""
        self.default_config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': [
                'pan2d', 'lasso2d', 'select2d', 'autoScale2d', 'hoverClosestCartesian',
                'hoverCompareCartesian', 'toggleSpikelines'
            ]
        }
        
        # Professional trading color scheme
        self.colors = {
            'bullish': '#00C851',     # Green
            'bearish': '#FF4444',     # Red
            'neutral': '#33B5E5',     # Blue
            'background': '#1E1E1E',  # Dark gray
            'grid': '#333333',        # Light gray
            'text': '#FFFFFF',        # White
            'volume': '#FFB74D',      # Orange
            'ma_fast': '#E1BEE7',     # Light purple
            'ma_slow': '#FFE082',     # Light yellow
            'rsi': '#81C784',         # Light green
            'macd': '#90CAF9'         # Light blue
        }
    
    def create_candlestick_chart(self, data: pd.DataFrame, symbol: str = "Symbol", 
                                indicators: Dict = None, trades: List[Dict] = None) -> go.Figure:
        """
        Create professional candlestick chart with indicators
        
        Args:
            data: OHLCV data with datetime index
            symbol: Symbol name for title
            indicators: Dictionary of indicator data
            trades: List of trade executions to plot
            
        Returns:
            Plotly figure object
        """
        # Create subplots for main chart and indicators
        subplot_titles = [f"{symbol} Price Action"]
        rows = 1
        row_heights = [0.7]
        
        # Add subplot for volume
        if 'volume' in data.columns:
            subplot_titles.append("Volume")
            rows += 1
            row_heights.append(0.15)
        
        # Add subplot for RSI if available
        if indicators and 'rsi' in indicators:
            subplot_titles.append("RSI")
            rows += 1
            row_heights.append(0.15)
        
        # Create subplots
        fig = make_subplots(
            rows=rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=subplot_titles,
            row_heights=row_heights
        )
        
        # Main candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name=symbol,
                increasing_line_color=self.colors['bullish'],
                decreasing_line_color=self.colors['bearish'],
                increasing_fillcolor=self.colors['bullish'],
                decreasing_fillcolor=self.colors['bearish']
            ),
            row=1, col=1
        )
        
        current_row = 1
        
        # Add moving averages if available
        if indicators:
            if 'sma_20' in indicators:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=indicators['sma_20'],
                        mode='lines',
                        name='SMA 20',
                        line=dict(color=self.colors['ma_fast'], width=2),
                        opacity=0.8
                    ),
                    row=1, col=1
                )
            
            if 'sma_50' in indicators:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=indicators['sma_50'],
                        mode='lines',
                        name='SMA 50',
                        line=dict(color=self.colors['ma_slow'], width=2),
                        opacity=0.8
                    ),
                    row=1, col=1
                )
            
            # Add Bollinger Bands if available
            if 'bb_upper' in indicators and 'bb_lower' in indicators:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=indicators['bb_upper'],
                        mode='lines',
                        name='BB Upper',
                        line=dict(color=self.colors['neutral'], width=1, dash='dash'),
                        opacity=0.6
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=indicators['bb_lower'],
                        mode='lines',
                        name='BB Lower',
                        line=dict(color=self.colors['neutral'], width=1, dash='dash'),
                        fill='tonexty',
                        fillcolor='rgba(51, 181, 229, 0.1)',
                        opacity=0.6
                    ),
                    row=1, col=1
                )
        
        # Add trade markers if provided
        if trades:
            buy_trades = [t for t in trades if t.get('action', '').upper() == 'BUY']
            sell_trades = [t for t in trades if t.get('action', '').upper() == 'SELL']
            
            if buy_trades:
                buy_dates = [t['timestamp'] for t in buy_trades]
                buy_prices = [t['price'] for t in buy_trades]
                
                fig.add_trace(
                    go.Scatter(
                        x=buy_dates,
                        y=buy_prices,
                        mode='markers',
                        name='Buy Signals',
                        marker=dict(
                            symbol='triangle-up',
                            size=12,
                            color=self.colors['bullish'],
                            line=dict(width=2, color='white')
                        )
                    ),
                    row=1, col=1
                )
            
            if sell_trades:
                sell_dates = [t['timestamp'] for t in sell_trades]
                sell_prices = [t['price'] for t in sell_trades]
                
                fig.add_trace(
                    go.Scatter(
                        x=sell_dates,
                        y=sell_prices,
                        mode='markers',
                        name='Sell Signals',
                        marker=dict(
                            symbol='triangle-down',
                            size=12,
                            color=self.colors['bearish'],
                            line=dict(width=2, color='white')
                        )
                    ),
                    row=1, col=1
                )
        
        # Add volume chart
        if 'volume' in data.columns:
            current_row += 1
            
            # Color volume bars based on price movement
            volume_colors = []
            for i in range(len(data)):
                if i == 0:
                    volume_colors.append(self.colors['neutral'])
                else:
                    if data['close'].iloc[i] >= data['close'].iloc[i-1]:
                        volume_colors.append(self.colors['bullish'])
                    else:
                        volume_colors.append(self.colors['bearish'])
            
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['volume'],
                    name='Volume',
                    marker_color=volume_colors,
                    opacity=0.7
                ),
                row=current_row, col=1
            )
        
        # Add RSI chart
        if indicators and 'rsi' in indicators:
            current_row += 1
            
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=indicators['rsi'],
                    mode='lines',
                    name='RSI',
                    line=dict(color=self.colors['rsi'], width=2)
                ),
                row=current_row, col=1
            )
            
            # Add RSI overbought/oversold levels
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=current_row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=current_row, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=current_row, col=1)
            
            # Update RSI y-axis
            fig.update_yaxes(range=[0, 100], row=current_row, col=1)
        
        # Update layout
        fig.update_layout(
            title=f"{symbol} - Professional Trading Chart",
            template="plotly_dark",
            height=600 + (rows - 1) * 150,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        # Remove range slider for cleaner look
        fig.update_layout(xaxis_rangeslider_visible=False)
        
        return fig
    
    def create_performance_dashboard(self, backtest_results: Dict) -> go.Figure:
        """
        Create comprehensive performance dashboard
        
        Args:
            backtest_results: Results from backtest containing trades, metrics, etc.
            
        Returns:
            Plotly figure with performance metrics
        """
        # Create subplot layout
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=[
                "Portfolio Value Over Time",
                "Trade Distribution",
                "Monthly Returns",
                "Drawdown Analysis"
            ],
            specs=[[{"secondary_y": False}, {"type": "bar"}],
                   [{"type": "bar"}, {"secondary_y": False}]]
        )
        
        # 1. Portfolio value over time
        if 'portfolio_value' in backtest_results:
            portfolio_data = backtest_results['portfolio_value']
            fig.add_trace(
                go.Scatter(
                    x=portfolio_data.index,
                    y=portfolio_data.values,
                    mode='lines',
                    name='Portfolio Value',
                    line=dict(color=self.colors['bullish'], width=2),
                    fill='tonexty'
                ),
                row=1, col=1
            )
        
        # 2. Trade distribution (wins vs losses)
        if 'trades' in backtest_results:
            trades = backtest_results['trades']
            wins = len([t for t in trades if t.get('pnl', 0) > 0])
            losses = len([t for t in trades if t.get('pnl', 0) < 0])
            
            fig.add_trace(
                go.Bar(
                    x=['Winning Trades', 'Losing Trades'],
                    y=[wins, losses],
                    name='Trade Distribution',
                    marker_color=[self.colors['bullish'], self.colors['bearish']]
                ),
                row=1, col=2
            )
        
        # 3. Monthly returns
        if 'monthly_returns' in backtest_results:
            monthly_returns = backtest_results['monthly_returns']
            colors = [self.colors['bullish'] if x >= 0 else self.colors['bearish'] for x in monthly_returns.values]
            
            fig.add_trace(
                go.Bar(
                    x=monthly_returns.index,
                    y=monthly_returns.values,
                    name='Monthly Returns',
                    marker_color=colors
                ),
                row=2, col=1
            )
        
        # 4. Drawdown analysis
        if 'drawdown' in backtest_results:
            drawdown = backtest_results['drawdown']
            fig.add_trace(
                go.Scatter(
                    x=drawdown.index,
                    y=drawdown.values,
                    mode='lines',
                    name='Drawdown',
                    line=dict(color=self.colors['bearish'], width=2),
                    fill='tozeroy',
                    fillcolor='rgba(255, 68, 68, 0.3)'
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title="Performance Dashboard",
            template="plotly_dark",
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_correlation_heatmap(self, correlation_data: pd.DataFrame) -> go.Figure:
        """
        Create correlation heatmap for multiple assets
        
        Args:
            correlation_data: Correlation matrix
            
        Returns:
            Plotly heatmap figure
        """
        fig = go.Figure(data=go.Heatmap(
            z=correlation_data.values,
            x=correlation_data.columns,
            y=correlation_data.index,
            colorscale='RdYlBu',
            zmid=0,
            text=correlation_data.values.round(2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Asset Correlation Matrix",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    def create_risk_metrics_chart(self, metrics: Dict) -> go.Figure:
        """
        Create risk metrics visualization
        
        Args:
            metrics: Dictionary of risk metrics
            
        Returns:
            Plotly figure with risk metrics
        """
        # Create radar chart for risk metrics
        categories = list(metrics.keys())
        values = list(metrics.values())
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Risk Metrics',
            line_color=self.colors['neutral']
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values) * 1.1]
                )),
            showlegend=False,
            title="Risk Profile",
            template="plotly_dark"
        )
        
        return fig
    
    def create_multi_timeframe_analysis(self, data_dict: Dict[str, pd.DataFrame], 
                                      symbol: str = "Symbol") -> go.Figure:
        """
        Create multi-timeframe analysis chart
        
        Args:
            data_dict: Dictionary with timeframes as keys and OHLCV data as values
            symbol: Symbol name
            
        Returns:
            Plotly figure with multiple timeframes
        """
        timeframes = list(data_dict.keys())
        rows = len(timeframes)
        
        fig = make_subplots(
            rows=rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=[f"{symbol} - {tf}" for tf in timeframes]
        )
        
        for i, (timeframe, data) in enumerate(data_dict.items(), 1):
            # Add candlestick for each timeframe
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['open'],
                    high=data['high'],
                    low=data['low'],
                    close=data['close'],
                    name=f"{timeframe}",
                    increasing_line_color=self.colors['bullish'],
                    decreasing_line_color=self.colors['bearish']
                ),
                row=i, col=1
            )
        
        fig.update_layout(
            title=f"{symbol} - Multi-Timeframe Analysis",
            template="plotly_dark",
            height=200 * rows,
            showlegend=False
        )
        
        # Remove range sliders except for the bottom chart
        for i in range(1, rows):
            fig.update_layout(**{f'xaxis{i}_rangeslider_visible': False})
        
        return fig
    
    def create_live_dashboard(self, current_data: Dict, alerts: List[Dict]) -> go.Figure:
        """
        Create live trading dashboard
        
        Args:
            current_data: Current market data
            alerts: Recent alerts
            
        Returns:
            Plotly figure for live dashboard
        """
        # Create 2x2 subplot layout
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=[
                "Current Price Movement",
                "Alert Distribution",
                "Volume Analysis", 
                "Recent Signals"
            ],
            specs=[[{"type": "indicator"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # 1. Current price indicator
        if 'current_price' in current_data:
            price = current_data['current_price']
            change = current_data.get('price_change', 0)
            change_pct = current_data.get('price_change_percent', 0)
            
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=price,
                    delta={'reference': price - change, 'relative': True},
                    title={"text": "Current Price"},
                    number={'prefix': "$"},
                    domain={'x': [0, 1], 'y': [0, 1]}
                ),
                row=1, col=1
            )
        
        # 2. Alert distribution pie chart
        if alerts:
            alert_types = {}
            for alert in alerts:
                alert_type = alert.get('type', 'unknown')
                alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
            
            fig.add_trace(
                go.Pie(
                    labels=list(alert_types.keys()),
                    values=list(alert_types.values()),
                    name="Alert Types"
                ),
                row=1, col=2
            )
        
        # 3. Volume analysis
        if 'volume_data' in current_data:
            volume_data = current_data['volume_data']
            fig.add_trace(
                go.Bar(
                    x=volume_data.index,
                    y=volume_data.values,
                    name="Volume",
                    marker_color=self.colors['volume']
                ),
                row=2, col=1
            )
        
        # 4. Recent signals
        if alerts:
            recent_signals = [a for a in alerts if a.get('type') == 'signal'][-10:]  # Last 10 signals
            if recent_signals:
                x_vals = [s.get('timestamp', '') for s in recent_signals]
                y_vals = [s.get('price', 0) for s in recent_signals]
                colors = [self.colors['bullish'] if s.get('action') == 'BUY' else self.colors['bearish'] 
                         for s in recent_signals]
                
                fig.add_trace(
                    go.Scatter(
                        x=x_vals,
                        y=y_vals,
                        mode='markers+lines',
                        name="Recent Signals",
                        marker=dict(color=colors, size=8),
                        line=dict(color=self.colors['neutral'])
                    ),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Live Trading Dashboard",
            template="plotly_dark",
            height=600
        )
        
        return fig

def create_sample_chart(symbol: str = "BTC-USD") -> go.Figure:
    """
    Create a sample trading chart for demonstration
    
    Args:
        symbol: Symbol to create chart for
        
    Returns:
        Sample Plotly figure
    """
    # Generate sample data
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    
    # Generate realistic price movement
    price = 100
    prices = []
    volumes = []
    
    for i in range(len(dates)):
        # Random walk with slight upward bias
        change = np.random.normal(0.001, 0.02)
        price *= (1 + change)
        
        # OHLC data
        open_price = price
        high_price = price * np.random.uniform(1.0, 1.02)
        low_price = price * np.random.uniform(0.98, 1.0)
        close_price = price * np.random.uniform(0.99, 1.01)
        
        prices.append({
            'open': open_price,
            'high': max(high_price, open_price, close_price),
            'low': min(low_price, open_price, close_price),
            'close': close_price
        })
        
        # Random volume
        volumes.append(np.random.uniform(1000000, 5000000))
        
        price = close_price
    
    # Create DataFrame
    df = pd.DataFrame(prices, index=dates)
    df['volume'] = volumes
    
    # Add some indicators
    df['sma_20'] = df['close'].rolling(20).mean()
    df['sma_50'] = df['close'].rolling(50).mean()
    
    # Calculate RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    indicators = {
        'sma_20': df['sma_20'],
        'sma_50': df['sma_50'],
        'rsi': rsi
    }
    
    # Generate some sample trades
    trades = [
        {'timestamp': '2023-03-15', 'action': 'BUY', 'price': df.loc['2023-03-15', 'close']},
        {'timestamp': '2023-06-20', 'action': 'SELL', 'price': df.loc['2023-06-20', 'close']},
        {'timestamp': '2023-09-10', 'action': 'BUY', 'price': df.loc['2023-09-10', 'close']},
    ]
    
    # Create chart
    charts = TradingCharts()
    return charts.create_candlestick_chart(df, symbol, indicators, trades)