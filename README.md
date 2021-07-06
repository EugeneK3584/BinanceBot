# BinanceBot

 1. TradingView strategy or signal calls the script via webhook using Pagekite service.
 2. flask_webhook_order.py runs in a background and will pass Direction to a BinanceBot.py along with strategy name (additionaly candle size is also provided)
 3. process repeats
 
