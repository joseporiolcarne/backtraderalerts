import backtrader as bt
import backtrader.indicators as btind
from typing import Dict, List, Any

class MultiTimeframeStrategy(bt.Strategy):
    params = (
        ('timeframe_configs', {}),  # Dict of timeframe configurations
        ('conditions', []),  # List of conditions with timeframe info
        ('printlog', True),
    )
    
    def __init__(self):
        self.indicators = {}  # Store indicators by timeframe and name
        self.dataclose = {}  # Store close prices by timeframe
        
        # Initialize indicators for each timeframe
        for tf_name, tf_config in self.params.timeframe_configs.items():
            self.indicators[tf_name] = {}
            data_feed = tf_config.get('data', self.datas[0])
            self.dataclose[tf_name] = data_feed.close
            
            # Create indicators for this timeframe
            for ind_name, ind_config in tf_config.get('indicators', {}).items():
                indicator_class = getattr(btind, ind_config['type'])
                params = ind_config.get('params', {})
                
                # Create indicator instance
                if ind_config['type'] in ['BollingerBands', 'BBands']:
                    self.indicators[tf_name][ind_name] = indicator_class(data_feed, **params)
                elif ind_config['type'] in ['SMA', 'EMA', 'WMA']:
                    self.indicators[tf_name][ind_name] = indicator_class(data_feed.close, **params)
                elif ind_config['type'] in ['RSI', 'CCI', 'Stochastic', 'MACD', 'ADX', 'ATR']:
                    self.indicators[tf_name][ind_name] = indicator_class(data_feed, **params)
                else:
                    self.indicators[tf_name][ind_name] = indicator_class(data_feed, **params)
        
        self.order = None
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
                
                if hasattr(self, 'alert_dispatcher') and self.alert_dispatcher:
                    # Get triggered conditions for alert message
                    triggered_conditions = self.get_triggered_conditions()
                    message = f"BUY {self.datas[0]._name}\nPrice: {order.executed.price:.2f}\n"
                    message += f"Size: {order.executed.size:.4f}\n"
                    if triggered_conditions:
                        message += "\nTriggered conditions:\n"
                        for cond in triggered_conditions:
                            message += f"- {cond}\n"
                    
                    self.alert_dispatcher.send_custom_alert(message)
            else:
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
                
                if hasattr(self, 'alert_dispatcher') and self.alert_dispatcher:
                    message = f"SELL {self.datas[0]._name}\nPrice: {order.executed.price:.2f}\n"
                    message += f"Size: {order.executed.size:.4f}"
                    self.alert_dispatcher.send_custom_alert(message)
        
        self.order = None
    
    def next(self):
        if self.order:
            return
        
        # Check all conditions
        triggered = self.check_all_conditions()
        
        if triggered:
            if not self.position:
                self.log(f'BUY CREATE, {self.dataclose[list(self.dataclose.keys())[0]][0]:.2f}')
                self.order = self.buy()
            else:
                self.log(f'SELL CREATE, {self.dataclose[list(self.dataclose.keys())[0]][0]:.2f}')
                self.order = self.sell()
    
    def check_all_conditions(self):
        """Check if any condition group is met"""
        for condition_group in self.params.conditions:
            if self.check_condition_group(condition_group):
                return True
        return False
    
    def check_condition_group(self, condition_group):
        """Check if all conditions in a group are met"""
        conditions = condition_group.get('conditions', [])
        operator = condition_group.get('operator', 'AND')
        action = condition_group.get('action', 'BUY')
        
        # Check if we're in the right position state for this action
        if action == 'BUY' and self.position:
            return False
        elif action == 'SELL' and not self.position:
            return False
        
        results = []
        for condition in conditions:
            try:
                result = self.evaluate_condition(condition)
                results.append(result)
            except Exception as e:
                self.log(f'Error evaluating condition: {e}')
                return False
        
        if not results:
            return False
        
        if operator == 'AND':
            return all(results)
        elif operator == 'OR':
            return any(results)
        else:
            return results[0]
    
    def evaluate_condition(self, condition):
        """Evaluate a single condition"""
        timeframe = condition.get('timeframe', list(self.dataclose.keys())[0])
        condition_type = condition.get('type', 'indicator')
        
        if condition_type == 'price':
            return self.evaluate_price_condition(condition, timeframe)
        elif condition_type == 'indicator':
            return self.evaluate_indicator_condition(condition, timeframe)
        elif condition_type == 'crossover':
            return self.evaluate_crossover_condition(condition, timeframe)
        
        return False
    
    def evaluate_price_condition(self, condition, timeframe):
        """Evaluate price-based conditions"""
        operator = condition['operator']
        value = condition['value']
        price_type = condition.get('price_type', 'close')
        
        # Get the appropriate price
        if price_type == 'close':
            current_price = self.dataclose[timeframe][0]
        elif price_type == 'open':
            data_feed = self.get_data_feed(timeframe)
            current_price = data_feed.open[0]
        elif price_type == 'high':
            data_feed = self.get_data_feed(timeframe)
            current_price = data_feed.high[0]
        elif price_type == 'low':
            data_feed = self.get_data_feed(timeframe)
            current_price = data_feed.low[0]
        else:
            current_price = self.dataclose[timeframe][0]
        
        # Evaluate condition
        if operator == '>':
            return current_price > value
        elif operator == '<':
            return current_price < value
        elif operator == '>=':
            return current_price >= value
        elif operator == '<=':
            return current_price <= value
        elif operator == '==':
            return current_price == value
        elif operator == 'crosses_above':
            prev_price = self.dataclose[timeframe][-1]
            return prev_price <= value and current_price > value
        elif operator == 'crosses_below':
            prev_price = self.dataclose[timeframe][-1]
            return prev_price >= value and current_price < value
        
        return False
    
    def evaluate_indicator_condition(self, condition, timeframe):
        """Evaluate indicator-based conditions"""
        ind_name = condition['indicator']
        operator = condition['operator']
        value = condition['value']
        
        if timeframe not in self.indicators or ind_name not in self.indicators[timeframe]:
            return False
        
        indicator = self.indicators[timeframe][ind_name]
        
        # Get indicator value
        if hasattr(indicator, 'lines'):
            line_name = condition.get('line', None)
            if line_name and hasattr(indicator, line_name):
                ind_value = getattr(indicator, line_name)[0]
            else:
                ind_value = indicator.lines[0][0]
        else:
            ind_value = indicator[0]
        
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
            if hasattr(indicator, 'lines'):
                prev_value = indicator.lines[0][-1]
            else:
                prev_value = indicator[-1]
            return prev_value <= value and ind_value > value
        elif operator == 'crosses_below':
            if hasattr(indicator, 'lines'):
                prev_value = indicator.lines[0][-1]
            else:
                prev_value = indicator[-1]
            return prev_value >= value and ind_value < value
        
        return False
    
    def evaluate_crossover_condition(self, condition, timeframe):
        """Evaluate crossover between indicators or price"""
        ind1_name = condition['indicator1']
        ind2_name = condition['indicator2']
        operator = condition.get('operator', 'crosses_above')
        
        # Get first value (indicator or price)
        if ind1_name == 'price':
            ind1_value = self.dataclose[timeframe][0]
            ind1_prev = self.dataclose[timeframe][-1]
        elif timeframe in self.indicators and ind1_name in self.indicators[timeframe]:
            ind1 = self.indicators[timeframe][ind1_name]
            if hasattr(ind1, 'lines'):
                ind1_value = ind1.lines[0][0]
                ind1_prev = ind1.lines[0][-1]
            else:
                ind1_value = ind1[0]
                ind1_prev = ind1[-1]
        else:
            return False
        
        # Get second value (indicator or price)
        if ind2_name == 'price':
            ind2_value = self.dataclose[timeframe][0]
            ind2_prev = self.dataclose[timeframe][-1]
        elif timeframe in self.indicators and ind2_name in self.indicators[timeframe]:
            ind2 = self.indicators[timeframe][ind2_name]
            if hasattr(ind2, 'lines'):
                ind2_value = ind2.lines[0][0]
                ind2_prev = ind2.lines[0][-1]
            else:
                ind2_value = ind2[0]
                ind2_prev = ind2[-1]
        else:
            # Try to parse as a number
            try:
                ind2_value = float(ind2_name)
                ind2_prev = ind2_value
            except:
                return False
        
        # Check crossover
        if operator == 'crosses_above' or operator == 'above':
            return ind1_prev <= ind2_prev and ind1_value > ind2_value
        elif operator == 'crosses_below' or operator == 'below':
            return ind1_prev >= ind2_prev and ind1_value < ind2_value
        
        return False
    
    def get_data_feed(self, timeframe):
        """Get data feed for a specific timeframe"""
        for tf_name, tf_config in self.params.timeframe_configs.items():
            if tf_name == timeframe:
                return tf_config.get('data', self.datas[0])
        return self.datas[0]
    
    def get_triggered_conditions(self):
        """Get list of conditions that are currently triggered"""
        triggered = []
        
        for condition_group in self.params.conditions:
            conditions = condition_group.get('conditions', [])
            action = condition_group.get('action', 'BUY')
            
            # Only check BUY conditions when not in position
            if action == 'BUY' and not self.position:
                for condition in conditions:
                    if self.evaluate_condition(condition):
                        tf = condition.get('timeframe', 'default')
                        cond_type = condition.get('type', 'indicator')
                        
                        if cond_type == 'price':
                            desc = f"{tf}: Price {condition['operator']} {condition['value']}"
                        elif cond_type == 'indicator':
                            desc = f"{tf}: {condition['indicator']} {condition['operator']} {condition['value']}"
                        elif cond_type == 'crossover':
                            desc = f"{tf}: {condition['indicator1']} crosses {condition['operator']} {condition['indicator2']}"
                        
                        triggered.append(desc)
        
        return triggered
    
    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()} {txt}')