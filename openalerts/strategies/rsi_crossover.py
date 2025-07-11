import backtrader as bt
from datetime import datetime


class RSICrossover(bt.Strategy):
    params = dict(
        period=14,
        rsi_low=30,
        rsi_high=70,
        symbol='',  # For alert messages
    )
    
    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=self.p.period)
        self.last_rsi_state = None  # Track RSI state to avoid duplicate alerts
        
    def next(self):
        current_rsi = self.rsi[0]
        
        # Check for RSI oversold condition
        if current_rsi < self.p.rsi_low:
            if self.last_rsi_state != 'oversold':
                self.notify_alert(
                    f"🔴 RSI OVERSOLD Alert!\n"
                    f"Symbol: {self.p.symbol}\n"
                    f"RSI: {current_rsi:.2f} (< {self.p.rsi_low})\n"
                    f"Price: {self.data.close[0]:.4f}\n"
                    f"Time: {self.data.datetime.datetime(0)}"
                )
                self.last_rsi_state = 'oversold'
                
        # Check for RSI overbought condition
        elif current_rsi > self.p.rsi_high:
            if self.last_rsi_state != 'overbought':
                self.notify_alert(
                    f"🟢 RSI OVERBOUGHT Alert!\n"
                    f"Symbol: {self.p.symbol}\n"
                    f"RSI: {current_rsi:.2f} (> {self.p.rsi_high})\n"
                    f"Price: {self.data.close[0]:.4f}\n"
                    f"Time: {self.data.datetime.datetime(0)}"
                )
                self.last_rsi_state = 'overbought'
                
        # Reset state when RSI returns to normal range
        elif self.p.rsi_low < current_rsi < self.p.rsi_high:
            self.last_rsi_state = 'normal'
    
    def notify_alert(self, msg):
        """Hook to alert system"""
        print(f"[ALERT] {msg}")
        
        # Add message to cerebro's telegram queue if it exists
        if hasattr(self.env, 'telegram_messages'):
            self.env.telegram_messages.append(msg)


class MultiIndicatorAlert(bt.Strategy):
    """Extended strategy with multiple indicators"""
    params = dict(
        rsi_period=14,
        rsi_low=30,
        rsi_high=70,
        macd_fast=12,
        macd_slow=26,
        macd_signal=9,
        bb_period=20,
        bb_devs=2,
        symbol='',
    )
    
    def __init__(self):
        # RSI
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=self.p.rsi_period)
        
        # MACD
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.p.macd_fast,
            period_me2=self.p.macd_slow,
            period_signal=self.p.macd_signal
        )
        
        # Bollinger Bands
        self.bb = bt.indicators.BollingerBands(
            self.data.close,
            period=self.p.bb_period,
            devfactor=self.p.bb_devs
        )
        
        # Track states
        self.last_macd_cross = None
        self.last_bb_state = None
        
    def next(self):
        # RSI alerts (same as RSICrossover)
        current_rsi = self.rsi[0]
        if current_rsi < self.p.rsi_low:
            self.notify_alert(f"📊 RSI Oversold: {current_rsi:.2f}")
        elif current_rsi > self.p.rsi_high:
            self.notify_alert(f"📊 RSI Overbought: {current_rsi:.2f}")
        
        # MACD crossover alerts
        if len(self) > 1:  # Need at least 2 bars
            macd_cross = None
            if self.macd.macd[0] > self.macd.signal[0] and self.macd.macd[-1] <= self.macd.signal[-1]:
                macd_cross = 'bullish'
            elif self.macd.macd[0] < self.macd.signal[0] and self.macd.macd[-1] >= self.macd.signal[-1]:
                macd_cross = 'bearish'
            
            if macd_cross and macd_cross != self.last_macd_cross:
                self.notify_alert(
                    f"📈 MACD {macd_cross.upper()} Crossover!\n"
                    f"Symbol: {self.p.symbol}\n"
                    f"Price: {self.data.close[0]:.4f}"
                )
                self.last_macd_cross = macd_cross
        
        # Bollinger Bands alerts
        bb_state = None
        if self.data.close[0] > self.bb.lines.top[0]:
            bb_state = 'above'
        elif self.data.close[0] < self.bb.lines.bot[0]:
            bb_state = 'below'
        
        if bb_state and bb_state != self.last_bb_state:
            self.notify_alert(
                f"📉 Bollinger Band Break {'UP' if bb_state == 'above' else 'DOWN'}!\n"
                f"Symbol: {self.p.symbol}\n"
                f"Price: {self.data.close[0]:.4f}\n"
                f"Band: {self.bb.lines.top[0] if bb_state == 'above' else self.bb.lines.bot[0]:.4f}"
            )
            self.last_bb_state = bb_state
    
    def notify_alert(self, msg):
        """Hook to alert system"""
        print(f"[ALERT] {msg}")
        
        if hasattr(self.env, 'telegram_messages'):
            self.env.telegram_messages.append(msg)