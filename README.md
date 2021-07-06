# BinanceBot

 1. TradingView strategy or signal calls the script via webhook using Pagekite service.
 2. flask_webhook_order.py runs in a background and passes Direction to a BinanceBot.py along with Strategy Name (additionaly candle size is also provided)
 3. Process repeats
 
