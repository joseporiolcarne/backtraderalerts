try:
    import backtrader as bt
    import backtrader.indicators as btind
except ImportError:
    bt = None
    btind = None

if bt is not None:
    class RSICrossoverStrategy(bt.Strategy):
        params = (
            ('rsi_period', 14),
            ('rsi_oversold', 30),
            ('rsi_overbought', 70),
            ('printlog', True),
        )
        
        def __init__(self):
            # Create RSI indicator
            self.rsi = btind.RSI(self.datas[0], period=self.params.rsi_period)
            
            # Keep track of pending orders
            self.order = None
        
        def notify_order(self, order):
            if order.status in [order.Submitted, order.Accepted]:
                return
            
            if order.status in [order.Completed]:
                if order.isbuy():
                    self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
                    
                    # Send Telegram alert if dispatcher is available
                    if hasattr(self, 'alert_dispatcher') and self.alert_dispatcher:
                        self.alert_dispatcher.send_alert(
                            'BUY',
                            self.datas[0]._name,
                            order.executed.price,
                            order.executed.size
                        )
                else:
                    self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
                    
                    # Send Telegram alert if dispatcher is available
                    if hasattr(self, 'alert_dispatcher') and self.alert_dispatcher:
                        self.alert_dispatcher.send_alert(
                            'SELL',
                            self.datas[0]._name,
                            order.executed.price,
                            order.executed.size
                        )
            
            elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                self.log('Order Canceled/Margin/Rejected')
            
            self.order = None
        
        def next(self):
            # Check if an order is pending
            if self.order:
                return
            
            # Check if we are in the market
            if not self.position:
                # Buy signal: RSI crosses above oversold level
                if self.rsi[0] > self.params.rsi_oversold and self.rsi[-1] <= self.params.rsi_oversold:
                    self.log(f'BUY CREATE, RSI: {self.rsi[0]:.2f}, Price: {self.datas[0].close[0]:.2f}')
                    self.order = self.buy()
            else:
                # Sell signal: RSI crosses below overbought level
                if self.rsi[0] < self.params.rsi_overbought and self.rsi[-1] >= self.params.rsi_overbought:
                    self.log(f'SELL CREATE, RSI: {self.rsi[0]:.2f}, Price: {self.datas[0].close[0]:.2f}')
                    self.order = self.sell()
        
        def log(self, txt, dt=None):
            if self.params.printlog:
                dt = dt or self.datas[0].datetime.date(0)
                print(f'{dt.isoformat()} {txt}')

else:
    # Fallback when backtrader is not available
    class RSICrossoverStrategy:
        def __init__(self):
            raise ImportError("backtrader not installed. Install with: pip install backtrader")