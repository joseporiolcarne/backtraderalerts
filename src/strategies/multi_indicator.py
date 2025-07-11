import backtrader as bt
import backtrader.indicators as btind

class MultiIndicatorStrategy(bt.Strategy):
    params = (
        ('indicators', {}),  # Dict of indicator configurations
        ('entry_conditions', []),  # List of entry conditions
        ('exit_conditions', []),  # List of exit conditions
        ('printlog', True),
    )
    
    def __init__(self):
        self.indicators = {}
        self.dataclose = self.datas[0].close
        
        # Initialize configured indicators
        for ind_name, ind_config in self.params.indicators.items():
            indicator_class = getattr(btind, ind_config['type'])
            params = ind_config.get('params', {})
            
            # Create indicator instance
            if ind_config['type'] in ['BollingerBands', 'BBands']:
                self.indicators[ind_name] = indicator_class(self.datas[0], **params)
            elif ind_config['type'] in ['SMA', 'EMA', 'WMA']:
                self.indicators[ind_name] = indicator_class(self.datas[0].close, **params)
            elif ind_config['type'] in ['RSI', 'CCI', 'Stochastic', 'MACD', 'ADX', 'ATR']:
                self.indicators[ind_name] = indicator_class(self.datas[0], **params)
            else:
                # Generic indicator creation
                self.indicators[ind_name] = indicator_class(self.datas[0], **params)
        
        # Keep track of pending orders
        self.order = None
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
                
                # Send Telegram alert
                if hasattr(self, 'alert_dispatcher') and self.alert_dispatcher:
                    self.alert_dispatcher.send_alert(
                        'BUY',
                        self.datas[0]._name,
                        order.executed.price,
                        order.executed.size
                    )
            else:
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
                
                # Send Telegram alert
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
            # Check entry conditions
            if self.check_conditions(self.params.entry_conditions):
                self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')
                self.order = self.buy()
        else:
            # Check exit conditions
            if self.check_conditions(self.params.exit_conditions):
                self.log(f'SELL CREATE, {self.dataclose[0]:.2f}')
                self.order = self.sell()
    
    def check_conditions(self, conditions):
        """Check if all conditions in the list are met"""
        if not conditions:
            return False
        
        results = []
        for condition in conditions:
            try:
                result = self.evaluate_condition(condition)
                results.append(result)
            except Exception as e:
                self.log(f'Error evaluating condition: {e}')
                return False
        
        # Check logical operator
        if len(results) == 0:
            return False
        elif len(results) == 1:
            return results[0]
        else:
            # Default to AND logic, can be extended to support OR
            return all(results)
    
    def evaluate_condition(self, condition):
        """Evaluate a single condition"""
        ind_name = condition['indicator']
        operator = condition['operator']
        value = condition['value']
        
        # Get indicator value
        if ind_name == 'price':
            ind_value = self.dataclose[0]
        elif ind_name in self.indicators:
            indicator = self.indicators[ind_name]
            
            # Handle different indicator types
            if hasattr(indicator, 'lines'):
                # For indicators with multiple lines (like Bollinger Bands)
                line_name = condition.get('line', None)
                if line_name and hasattr(indicator, line_name):
                    ind_value = getattr(indicator, line_name)[0]
                else:
                    # Default to first line
                    ind_value = indicator.lines[0][0]
            else:
                ind_value = indicator[0]
        else:
            # Handle special cases
            if ind_name == 'crossover':
                # Handle crossover conditions
                ind1_name = condition['indicator1']
                ind2_name = condition['indicator2']
                
                ind1 = self.get_indicator_value(ind1_name)
                ind2 = self.get_indicator_value(ind2_name)
                
                if operator == 'above':
                    return ind1[0] > ind2[0] and ind1[-1] <= ind2[-1]
                elif operator == 'below':
                    return ind1[0] < ind2[0] and ind1[-1] >= ind2[-1]
            
            return False
        
        # Evaluate condition
        if operator == '>':
            return ind_value > value
        elif operator == '<':
            return ind_value < value
        elif operator == '>=':
            return ind_value >= value
        elif operator == '<=':
            return ind_value <= value
        elif operator == '==':
            return ind_value == value
        elif operator == 'crosses_above':
            # Check if indicator crosses above value
            if ind_name in self.indicators:
                indicator = self.indicators[ind_name]
                if hasattr(indicator, 'lines'):
                    prev_value = indicator.lines[0][-1]
                else:
                    prev_value = indicator[-1]
                return prev_value <= value and ind_value > value
        elif operator == 'crosses_below':
            # Check if indicator crosses below value
            if ind_name in self.indicators:
                indicator = self.indicators[ind_name]
                if hasattr(indicator, 'lines'):
                    prev_value = indicator.lines[0][-1]
                else:
                    prev_value = indicator[-1]
                return prev_value >= value and ind_value < value
        
        return False
    
    def get_indicator_value(self, ind_name):
        """Get indicator value or price"""
        if ind_name == 'price':
            return self.dataclose
        elif ind_name in self.indicators:
            return self.indicators[ind_name]
        else:
            # Try to parse as a number (constant value)
            try:
                return float(ind_name)
            except:
                return None
    
    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()} {txt}')


class SimpleIndicatorStrategy(bt.Strategy):
    """Simplified strategy for single indicator usage"""
    params = (
        ('indicator_type', 'RSI'),
        ('indicator_params', {}),
        ('entry_value', 30),
        ('exit_value', 70),
        ('entry_operator', '<'),
        ('exit_operator', '>'),
        ('printlog', True),
    )
    
    def __init__(self):
        # Get indicator class
        indicator_class = getattr(btind, self.params.indicator_type)
        
        # Create indicator
        if self.params.indicator_type in ['SMA', 'EMA', 'WMA']:
            self.indicator = indicator_class(self.datas[0].close, **self.params.indicator_params)
        else:
            self.indicator = indicator_class(self.datas[0], **self.params.indicator_params)
        
        self.order = None
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
                if hasattr(self, 'alert_dispatcher') and self.alert_dispatcher:
                    self.alert_dispatcher.send_alert(
                        'BUY',
                        self.datas[0]._name,
                        order.executed.price,
                        order.executed.size
                    )
            else:
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
                if hasattr(self, 'alert_dispatcher') and self.alert_dispatcher:
                    self.alert_dispatcher.send_alert(
                        'SELL',
                        self.datas[0]._name,
                        order.executed.price,
                        order.executed.size
                    )
        
        self.order = None
    
    def next(self):
        if self.order:
            return
        
        # Get indicator value
        if hasattr(self.indicator, 'lines'):
            ind_value = self.indicator.lines[0][0]
        else:
            ind_value = self.indicator[0]
        
        if not self.position:
            # Check entry condition
            if self.check_condition(ind_value, self.params.entry_value, self.params.entry_operator):
                self.log(f'BUY CREATE, {self.datas[0].close[0]:.2f}')
                self.order = self.buy()
        else:
            # Check exit condition
            if self.check_condition(ind_value, self.params.exit_value, self.params.exit_operator):
                self.log(f'SELL CREATE, {self.datas[0].close[0]:.2f}')
                self.order = self.sell()
    
    def check_condition(self, ind_value, threshold, operator):
        if operator == '>':
            return ind_value > threshold
        elif operator == '<':
            return ind_value < threshold
        elif operator == '>=':
            return ind_value >= threshold
        elif operator == '<=':
            return ind_value <= threshold
        elif operator == '==':
            return ind_value == threshold
        return False
    
    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()} {txt}')