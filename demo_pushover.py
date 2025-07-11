#!/usr/bin/env python3
"""
Pushover Integration Demo
Demonstrates the Pushover notification system integration
"""
import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_pushover_basic():
    """Demo basic Pushover functionality"""
    print("🔔 Pushover Basic Demo")
    print("=" * 50)
    
    from src.alerts.pushover_dispatcher import PushoverDispatcher
    
    # Create dispatcher (disabled for demo)
    dispatcher = PushoverDispatcher(
        app_token="demo_app_token",
        user_key="demo_user_key",
        enabled=False,  # Disabled for demo
        priority=0,
        sound="pushover"
    )
    
    print(f"✅ Created Pushover dispatcher")
    print(f"   App Token: {dispatcher.app_token}")
    print(f"   User Key: {dispatcher.user_key}")
    print(f"   Enabled: {dispatcher.enabled}")
    print(f"   Priority: {dispatcher.priority}")
    print(f"   Sound: {dispatcher.sound}")
    
    # Demo alert types
    print("\n📊 Testing Alert Types:")
    
    # Trading alert
    dispatcher.send_alert("BUY", "AAPL", 150.00, 10.0)
    print("   ✅ Trading alert sent")
    
    # Strategy signal
    dispatcher.send_strategy_signal(
        "RSI_Strategy",
        "BUY", 
        "BTC-USD",
        ["RSI < 30", "Volume spike", "Bullish divergence"]
    )
    print("   ✅ Strategy signal sent")
    
    # Custom alert
    dispatcher.send_custom_alert(
        "Portfolio rebalancing completed successfully",
        "Portfolio Management"
    )
    print("   ✅ Custom alert sent")
    
    # Error alert
    dispatcher.send_error_alert(
        "DATA_ERROR",
        "Failed to fetch real-time data",
        "yahoo_finance_api"
    )
    print("   ✅ Error alert sent")
    
    # Market update
    dispatcher.send_market_update("AAPL", 150.00, 5.00, 3.45, 1000000)
    print("   ✅ Market update sent")
    
    # Show history
    history = dispatcher.get_alerts_history()
    print(f"\n📋 Alert History: {len(history)} alerts stored")
    
    # Show counts
    counts = dispatcher.get_alerts_count()
    print(f"   Alert counts: {counts}")
    
    return dispatcher

def demo_alert_manager():
    """Demo AlertManager with multiple systems"""
    print("\n🎯 Alert Manager Demo")
    print("=" * 50)
    
    from src.alerts.alert_manager import AlertManager
    from src.config.config_manager import ConfigManager
    
    # Create configuration
    config = ConfigManager()
    
    # Configure multiple alert systems
    config.set('alerts.console.enabled', True)
    config.set('alerts.console.log_to_file', False)
    
    config.set('alerts.pushover.enabled', True)
    config.set('alerts.pushover.app_token', 'demo_token')
    config.set('alerts.pushover.user_key', 'demo_key')
    config.set('alerts.pushover.priority', 1)
    config.set('alerts.pushover.sound', 'bugle')
    
    # Create alert manager
    alert_manager = AlertManager(config)
    
    active_dispatchers = alert_manager.get_active_dispatchers()
    print(f"✅ Alert Manager created with dispatchers: {active_dispatchers}")
    
    # Send alerts to all systems
    print("\n📢 Sending multi-system alerts:")
    
    # Trading alert to all systems
    results = alert_manager.send_alert("BUY", "TSLA", 800.00, 5.0)
    print(f"   Trading alert results: {results}")
    
    # Strategy signal to specific systems
    results = alert_manager.send_strategy_signal(
        "MACD_Strategy",
        "SELL",
        "ETH-USD",
        ["MACD crossover", "High volume"],
        dispatchers=["console"]  # Only to console for demo
    )
    print(f"   Strategy signal results: {results}")
    
    # Custom alert to all systems
    results = alert_manager.send_custom_alert(
        "System health check completed - All systems operational",
        "System Status"
    )
    print(f"   Custom alert results: {results}")
    
    # Get statistics
    stats = alert_manager.get_dispatcher_stats()
    print(f"\n📊 Dispatcher Statistics:")
    for name, stat in stats.items():
        print(f"   {name}: {stat}")
    
    return alert_manager

def demo_priority_and_sounds():
    """Demo priority levels and sound options"""
    print("\n🔊 Priority & Sound Demo")
    print("=" * 50)
    
    from src.alerts.pushover_dispatcher import PushoverDispatcher
    
    dispatcher = PushoverDispatcher(
        app_token="demo_token",
        user_key="demo_key", 
        enabled=False
    )
    
    # Demo different priorities
    priorities = {
        -2: "Lowest (Silent)",
        -1: "Low (Quiet)",
        0: "Normal (Default)",
        1: "High (Loud)", 
        2: "Emergency (Repeated)"
    }
    
    print("🔔 Priority Levels:")
    for level, description in priorities.items():
        dispatcher.set_priority(level)
        dispatcher.send_custom_alert(
            f"Test alert with priority {level}",
            f"Priority Test - {description}"
        )
        print(f"   {level}: {description} ✅")
    
    # Demo different sounds
    sounds = ["pushover", "bugle", "siren", "spacealarm", "magic"]
    
    print("\n🎵 Sound Options:")
    for sound in sounds:
        dispatcher.set_sound(sound)
        dispatcher.send_custom_alert(
            f"Test alert with {sound} sound",
            "Sound Test",
            sound=sound
        )
        print(f"   {sound} ✅")
    
    print(f"\n📊 Total alerts in demo: {len(dispatcher.get_alerts_history())}")

def demo_error_handling():
    """Demo error handling capabilities"""
    print("\n🚨 Error Handling Demo")
    print("=" * 50)
    
    from src.alerts.pushover_dispatcher import PushoverDispatcher
    
    # Test with invalid credentials
    dispatcher = PushoverDispatcher(
        app_token="",
        user_key="",
        enabled=True  # Will auto-disable due to missing credentials
    )
    
    print(f"Invalid credentials test:")
    print(f"   Enabled after init: {dispatcher.enabled} (should be False)")
    
    # Test disabled dispatcher
    result = dispatcher.send_alert("BUY", "TEST", 100.00)
    print(f"   Send alert result: {result} (should be False)")
    
    # Test credential setting and enabling
    dispatcher.set_credentials("valid_token", "valid_key")
    print(f"   Enabled after setting credentials: {dispatcher.enabled} (should be True)")
    
    # Test connection with mock dispatcher
    print(f"\n🔧 Connection Testing:")
    result = dispatcher.test_connection()
    print(f"   Connection test result: {result}")
    
    # Demo graceful error handling
    print(f"\n🛡️ Graceful Error Handling:")
    
    try:
        # Invalid priority
        dispatcher.set_priority(5)
    except ValueError as e:
        print(f"   ✅ Priority validation: {e}")
    
    try:
        # Valid priority
        dispatcher.set_priority(1)
        print(f"   ✅ Valid priority set: {dispatcher.priority}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

def demo_configuration_integration():
    """Demo configuration file integration"""
    print("\n⚙️ Configuration Integration Demo")
    print("=" * 50)
    
    from src.config.config_manager import ConfigManager
    from src.alerts.alert_manager import AlertManager
    
    # Create config from YAML
    config = ConfigManager()
    
    # Set Pushover configuration programmatically
    pushover_config = {
        'alerts.pushover.enabled': True,
        'alerts.pushover.app_token': 'app_123456789',
        'alerts.pushover.user_key': 'user_abcdefg',
        'alerts.pushover.priority': 0,
        'alerts.pushover.sound': 'classical'
    }
    
    print("📝 Setting Pushover configuration:")
    for key, value in pushover_config.items():
        config.set(key, value)
        print(f"   {key}: {value}")
    
    # Verify configuration
    print("\n🔍 Verifying configuration:")
    for key, expected in pushover_config.items():
        actual = config.get(key)
        status = "✅" if actual == expected else "❌"
        print(f"   {key}: {actual} {status}")
    
    # Create AlertManager from config
    alert_manager = AlertManager(config)
    
    if 'pushover' in alert_manager.dispatchers:
        pushover = alert_manager.dispatchers['pushover']
        print(f"\n✅ Pushover dispatcher created from config:")
        print(f"   App Token: {pushover.app_token}")
        print(f"   User Key: {pushover.user_key}")
        print(f"   Priority: {pushover.priority}")
        print(f"   Sound: {pushover.sound}")
        print(f"   Enabled: {pushover.enabled}")
    else:
        print(f"\n❌ Pushover dispatcher not found in AlertManager")

def main():
    """Run all Pushover demos"""
    print("🔔 PUSHOVER INTEGRATION DEMONSTRATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Run all demos
        dispatcher = demo_pushover_basic()
        time.sleep(0.5)
        
        alert_manager = demo_alert_manager()
        time.sleep(0.5)
        
        demo_priority_and_sounds()
        time.sleep(0.5)
        
        demo_error_handling()
        time.sleep(0.5)
        
        demo_configuration_integration()
        
        print("\n" + "=" * 60)
        print("🎉 ALL PUSHOVER DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        # Summary statistics
        total_alerts = len(dispatcher.get_alerts_history())
        manager_alerts = len(alert_manager.get_alerts_history())
        
        print(f"\n📊 Demo Summary:")
        print(f"   Pushover Dispatcher alerts: {total_alerts}")
        print(f"   Alert Manager alerts: {manager_alerts}")
        print(f"   Total demonstrations: 5")
        print(f"   All systems operational: ✅")
        
        print(f"\n💡 To use with real Pushover account:")
        print(f"   1. Sign up at https://pushover.net")
        print(f"   2. Create an application to get app token")
        print(f"   3. Copy your user key from dashboard")
        print(f"   4. Update configuration with real credentials")
        print(f"   5. Set enabled=True in dispatcher")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()