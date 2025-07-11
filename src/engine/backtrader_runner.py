import backtrader as bt
import pandas as pd
from typing import Dict, Any, List, Type, Optional
from datetime import datetime

class BacktraderEngine:
    def __init__(self, initial_cash: float = 10000, commission: float = 0.001, alert_dispatcher=None):
        self.initial_cash = initial_cash
        self.commission = commission
        self.alert_dispatcher = alert_dispatcher
        self.cerebro = None
        
    def run_backtest(self, strategy_class: Type[bt.Strategy], data: pd.DataFrame, 
                     strategy_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a backtest with the given strategy and data
        
        Args:
            strategy_class: The strategy class to use
            data: DataFrame with OHLCV data
            strategy_params: Parameters to pass to the strategy
            
        Returns:
            Dictionary with backtest results
        """
        # Initialize Cerebro engine
        self.cerebro = bt.Cerebro()
        
        # Add initial cash
        self.cerebro.broker.setcash(self.initial_cash)
        
        # Set commission
        self.cerebro.broker.setcommission(commission=self.commission)
        
        # Convert pandas dataframe to backtrader data feed
        data_feed = bt.feeds.PandasData(
            dataname=data,
            datetime=None,  # Use index as datetime
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
            openinterest=None
        )
        
        # Add data to cerebro
        self.cerebro.adddata(data_feed)
        
        # Prepare strategy parameters
        if strategy_params is None:
            strategy_params = {}
        
        # Add alert dispatcher to strategy params if available
        if self.alert_dispatcher:
            # Create a custom strategy class that includes the alert dispatcher
            class StrategyWithAlerts(strategy_class):
                def __init__(self):
                    super().__init__()
                    self.alert_dispatcher = self.p.alert_dispatcher
            
            # Add alert dispatcher to params
            strategy_params['alert_dispatcher'] = self.alert_dispatcher
            strategy_class = StrategyWithAlerts
        
        # Add strategy with parameters
        self.cerebro.addstrategy(strategy_class, **strategy_params)
        
        # Add analyzers
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        # Add observer for portfolio value
        self.cerebro.addobserver(bt.observers.Value)
        self.cerebro.addobserver(bt.observers.DrawDown)
        
        # Run backtest
        initial_value = self.cerebro.broker.getvalue()
        strategies = self.cerebro.run()
        final_value = self.cerebro.broker.getvalue()
        
        # Extract results
        strategy = strategies[0]
        
        # Get analyzer results
        sharpe = strategy.analyzers.sharpe.get_analysis()
        drawdown = strategy.analyzers.drawdown.get_analysis()
        returns = strategy.analyzers.returns.get_analysis()
        trades = strategy.analyzers.trades.get_analysis()
        
        # Get portfolio values over time
        portfolio_values = []
        for i in range(len(strategy)):
            portfolio_values.append(strategy.observers.value.lines.value[i])
        
        # Get trades
        trade_list = self._extract_trades(strategy)
        
        # Compile results
        results = {
            'initial_value': initial_value,
            'final_value': final_value,
            'total_return': (final_value - initial_value) / initial_value * 100,
            'sharpe_ratio': sharpe.get('sharperatio', None),
            'max_drawdown': drawdown.get('max', {}).get('drawdown', 0),
            'total_trades': trades.get('total', {}).get('total', 0),
            'winning_trades': trades.get('won', {}).get('total', 0),
            'losing_trades': trades.get('lost', {}).get('total', 0),
            'portfolio_value': portfolio_values,
            'trades': trade_list
        }
        
        return results
    
    def _extract_trades(self, strategy) -> List[Dict[str, Any]]:
        """Extract trade information from the strategy"""
        trades = []
        
        # Get all completed trades
        for trade in strategy._trades:
            if trade.isclosed:
                trade_info = {
                    'entry_time': bt.num2date(trade.dtopen).strftime('%Y-%m-%d %H:%M:%S'),
                    'exit_time': bt.num2date(trade.dtclose).strftime('%Y-%m-%d %H:%M:%S'),
                    'entry_price': trade.price,
                    'exit_price': trade.priceclosed,
                    'size': trade.size,
                    'pnl': trade.pnl,
                    'pnl_pct': trade.pnl / (trade.price * abs(trade.size)) * 100,
                    'commission': trade.commission
                }
                trades.append(trade_info)
        
        return trades
    
    def plot_results(self, save_path: Optional[str] = None):
        """Plot the backtest results"""
        if self.cerebro:
            if save_path:
                self.cerebro.plot(savefig=True, figfilename=save_path)
            else:
                self.cerebro.plot()
    
    def run_multi_timeframe_backtest(self, strategy_class: Type[bt.Strategy], 
                                      timeframe_data: Dict[str, pd.DataFrame],
                                      strategy_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a multi-timeframe backtest
        
        Args:
            strategy_class: The strategy class to use
            timeframe_data: Dictionary with timeframe as key and DataFrame as value
            strategy_params: Parameters to pass to the strategy
            
        Returns:
            Dictionary with backtest results
        """
        # Initialize Cerebro engine
        self.cerebro = bt.Cerebro()
        
        # Add initial cash
        self.cerebro.broker.setcash(self.initial_cash)
        
        # Set commission
        self.cerebro.broker.setcommission(commission=self.commission)
        
        # Add data feeds for each timeframe
        data_feeds = {}
        primary_timeframe = None
        
        # Sort timeframes by frequency (shortest first for primary data)
        timeframe_order = ['5m', '15m', '30m', '1h', '2h', '4h', '1d']
        sorted_timeframes = sorted(timeframe_data.keys(), key=lambda x: timeframe_order.index(x) if x in timeframe_order else 999)
        
        for i, (timeframe, df) in enumerate([(tf, timeframe_data[tf]) for tf in sorted_timeframes]):
            # Convert pandas dataframe to backtrader data feed
            data_feed = bt.feeds.PandasData(
                dataname=df,
                datetime=None,  # Use index as datetime
                open='open',
                high='high',
                low='low',
                close='close',
                volume='volume',
                openinterest=None,
                name=f"{timeframe}_data"
            )
            
            # Add data to cerebro
            self.cerebro.adddata(data_feed, name=timeframe)
            data_feeds[timeframe] = data_feed
            
            # First timeframe is primary
            if i == 0:
                primary_timeframe = timeframe
        
        # Prepare strategy parameters
        if strategy_params is None:
            strategy_params = {}
        
        # Update timeframe configs with data feeds
        timeframe_configs = strategy_params.get('timeframe_configs', {})
        for tf_name in timeframe_configs:
            if tf_name in data_feeds:
                timeframe_configs[tf_name]['data'] = data_feeds[tf_name]
        
        strategy_params['timeframe_configs'] = timeframe_configs
        
        # Add alert dispatcher to strategy params if available
        if self.alert_dispatcher:
            strategy_params['alert_dispatcher'] = self.alert_dispatcher
        
        # Add strategy with parameters
        self.cerebro.addstrategy(strategy_class, **strategy_params)
        
        # Add analyzers
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        # Add observer for portfolio value
        self.cerebro.addobserver(bt.observers.Value)
        self.cerebro.addobserver(bt.observers.DrawDown)
        
        # Run backtest
        initial_value = self.cerebro.broker.getvalue()
        strategies = self.cerebro.run()
        final_value = self.cerebro.broker.getvalue()
        
        # Extract results
        strategy = strategies[0]
        
        # Get analyzer results
        sharpe = strategy.analyzers.sharpe.get_analysis()
        drawdown = strategy.analyzers.drawdown.get_analysis()
        returns = strategy.analyzers.returns.get_analysis()
        trades = strategy.analyzers.trades.get_analysis()
        
        # Get portfolio values over time
        portfolio_values = []
        for i in range(len(strategy)):
            portfolio_values.append(strategy.observers.value.lines.value[i])
        
        # Get trades
        trade_list = self._extract_trades(strategy)
        
        # Compile results
        results = {
            'initial_value': initial_value,
            'final_value': final_value,
            'total_return': (final_value - initial_value) / initial_value * 100,
            'sharpe_ratio': sharpe.get('sharperatio', None),
            'max_drawdown': drawdown.get('max', {}).get('drawdown', 0),
            'total_trades': trades.get('total', {}).get('total', 0),
            'winning_trades': trades.get('won', {}).get('total', 0),
            'losing_trades': trades.get('lost', {}).get('total', 0),
            'portfolio_value': portfolio_values,
            'trades': trade_list,
            'timeframes_used': list(timeframe_data.keys())
        }
        
        return results
    
    def run_live(self, strategy_class: Type[bt.Strategy], data_feed, 
                 strategy_params: Dict[str, Any] = None):
        """
        Run strategy in live mode (placeholder for future implementation)
        """
        raise NotImplementedError("Live trading not yet implemented")