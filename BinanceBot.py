from binance.enums import *
from binance.exceptions import *
from binance.websockets import BinanceSocketManager
from binance.client import Client

from collections import namedtuple
from time import sleep
from types import SimpleNamespace
from urllib.error import URLError, HTTPError

import time
import re
import sys
import os
import shelve
import urllib.request


##########################################################################################################

Direction = ''
BinanceAccN = ''

api_key = ""
api_secret = ""

DefaultExternalIP = "xx.xx.xx.xx"

PositionType = ''
PositionAmount = 0.00
PositionPrice = 0.00
OrderAmountBTC = 0.00
OrderAmountUSDT = 0.00

OrderPrice = 0.00

balanceBTC = 0.00
balanceUSDT = 0.00
balanceLockedFlag = False

isLongPosition = False
LongPositionAmount = 0.00
LongPositionPrice = 0.00

isShortPosition = False
ShortPositionAmount = 0.00
ShortPositionPrice = 0.00

CurrentPrice = 0.00

##########################################################################################################      
def GetCurrentBalance(client):

   CurrentBalance = namedtuple ("CurrentBalance",["balanceBTC","balanceUSDT"])
   balanceBTC = 0.00
   balanceUSDT = 0.00

   global balanceLockedFlag    

   try:
      balanceBTC_dict = client.get_asset_balance(asset='BTC', requests_params={'timeout': 5})
      balanceUSDT_dict = client.get_asset_balance(asset='USDT', requests_params={'timeout': 5})

      if ( float(balanceBTC_dict['locked']) > 0 ) or ( float(balanceUSDT_dict['locked']) > 0 ):

          print('BalanceBTC locked', balanceBTC_dict['locked'])
          print('BalanceUSDT locked', balanceUSDT_dict['locked'])
          
          balanceLockedFlag = True
      else:
          balanceLockedFlag = False  

      balanceBTC = round(float(balanceBTC_dict['free']),6)
      balanceUSDT = round(float(balanceUSDT_dict['free']),1)

      if ( balanceBTC > 0 ) or ( balanceUSDT > 0 ):
          return CurrentBalance(balanceBTC,balanceUSDT)     
      else:
          return False    
          
   except BinanceAPIException as e:

       print (e.status_code)
       print (e.message)
       return False

   finally:
       sleep(1) # 1 secs delay here

##########################################################################################################              
def GetCurrentPosition(client):

   CurrentPosition = namedtuple ("CurrentPosition", ["PositionType", "PositionAmount", "PositionPrice"])
   PositionType = ''
   PositionAmount = 0.00
   PositionPrice = 0.00

   try:
      orders = client.get_all_orders(symbol='BTCUSDT',limit=2)

      if (len(orders) == 0  ):            
              print('No orders history found !') 
              return False
      else:
         PositionAmount = float(orders[1]['executedQty'])
         PositionPrice = float(orders[1]['price'])

         if (orders[1]['side'] == "BUY"):
            PositionType = 'Long'
         elif (orders[1]['side'] == "SELL"):
            PositionType = 'Short'
         
         return CurrentPosition(PositionType, PositionAmount, PositionPrice)       
         
   except BinanceAPIException as e:
       print (e.status_code)
       print (e.message)
       return False

   finally:
        sleep(1) # 1 secs delay here

##########################################################################################################
def GetPreviousPosition(client): # for PNL calc

   PreviousPosition = namedtuple ("PreviousPosition", ["PositionType", "PositionAmount", "PositionPrice"])
   PositionType = ''
   PositionAmount = 0.00
   PositionPrice = 0.00

   try:
      orders = client.get_all_orders(symbol='BTCUSDT',limit=2)

      if (len(orders) == 0  ):            
              print('No orders history found !') 
              return False
      else:
         PositionAmount = float(orders[0]['executedQty'])
         PositionPrice = float(orders[0]['price'])

         if (orders[0]['side'] == "BUY"):
            PositionType = 'Long'
         elif (orders[0]['side'] == "SELL"):
            PositionType = 'Short'
         
         return PreviousPosition(PositionType, PositionAmount, PositionPrice)       

   except BinanceAPIException as e:
       print (e.status_code)
       print (e.message)
       return False

   finally:
        sleep(1) # 1 secs delay here

##########################################################################################################
def GetOpenOrders(client):
   #OpenOrder = namedtuple ("OpenOrder", ["OrderType", "OrderAmount", "OrderPrice"])   
   sleep(1) 

   try:
          orders = client.get_open_orders(symbol='BTCUSDT')
          
          if (len(orders) < 1 ):
              print('No open orders found')
              return False
          else:
              print('Num of open orders: ', len(orders))  
              for i in range(len(orders)):              
                  print (orders[i]['orderId'],orders[i]['type'],orders[i]['status'],orders[i]['origQty'],orders[i]['price'])
              return True

   except BinanceAPIException as e:
       print (e.status_code)
       print (e.message)
       return False

   finally:
       sleep(1) # 1 secs delay here


##########################################################################################################         
def PlaceLimitOrder(client,OrderType,OrderAmount,OrderPrice):   
   
   Type=Client.ORDER_TYPE_LIMIT

   if ( OrderType == 'Long' ):
       Side = Client.SIDE_BUY
   elif ( OrderType == 'Short' ):
       Side = Client.SIDE_SELL

   try:   
     order = client.create_order(symbol='BTCUSDT',side=Side,type=Type,timeInForce=TIME_IN_FORCE_GTC,quantity=OrderAmount,price=str(OrderPrice))
     return order
   except BinanceAPIException as e:
       print (e.status_code)
       print (e.message)
       return False
   except BinanceOrderException as eo:          
       print (eo.message)
       return False
   finally:       
       sleep(10) # 1 secs delay here       

##########################################################################################################         
def PlaceMarketOrder(client,OrderType,OrderAmount):   

   Type=Client.ORDER_TYPE_MARKET

   try:

       if ( OrderType == 'Long' ):
          Side = Client.SIDE_BUY
          order = client.create_order(symbol='BTCUSDT',side=Side,type=Type,quoteOrderQty=OrderAmount)
          return order

       elif ( OrderType == 'Short' ):
          Side = Client.SIDE_SELL
          order = client.create_order(symbol='BTCUSDT',side=Side,type=Type,quantity=OrderAmount)
          return order
      
   except BinanceAPIException as e:
       print (e.status_code)
       print (e.message)
       return False
   except BinanceOrderException as eo:
       print (eo.message)
       return False
   finally:       
       sleep(10) # 1 secs delay here
       

##########################################################################################################         
##########################################################################################################
# run the app
if __name__ == '__main__':

    if (len(sys.argv) < 3):
       print ('Direction was not specified: Long/Short , Account # ?')       
       sys.exit()

    else:        
       Direction = sys.argv[1]
       BinanceAccN = sys.argv[2]

    try:
       CurrentExternalIP = urllib.request.urlopen('https://ident.me').read().decode('utf8')
       print('Checked current external IP:',CurrentExternalIP)

    except HTTPError as e:
       print('Error code: ', e.code) 

    if (CurrentExternalIP != DefaultExternalIP):
       print('CurrentExternalIP != DefaultExternalIP')
       sys.exit()

##########################################################################################################
    if (BinanceAccN == "xxx@hotmail.com"):
       api_key = "xxx"
       api_secret = "yyy"

    elif (BinanceAccN == "virtual@ujl2gs2rnoemail.com"):
       api_key = "zzz"
       api_secret = "www"

    client = Client(api_key, api_secret)

    print(' ==== Balances check is running ==== ') 
    
    if ( GetCurrentBalance(client) is not False ):       
       balanceBTC, balanceUSDT = GetCurrentBalance(client)       
       print('BalanceBTC & USDT:', balanceBTC, balanceUSDT) 
       sleep (1)

##########################################################################################################
    
    if (Direction == 'Short') and (balanceBTC > 0.00001):
       print(' ==== Submitting order SHORT ==== ')

       OrderAmountBTC = round(balanceBTC-0.000001,6)

       Response = PlaceMarketOrder(client, 'Short', OrderAmountBTC)
       sleep (5)
       
       if ( Response is not False ):       
          order_ID = Response['orderId']  
          print('Submitted Order ID: ', order_ID)          
          order = client.get_order(symbol='BTCUSDT', orderId=order_ID)
          print (order)          
       else:
          print('Order was not submitted')  

    else:
       print('Skipped order SHORT')
       pass

##########################################################################################################
    
    if (Direction == 'Long') and (balanceUSDT > 10):
       print(' ==== Submitting order LONG ==== ')

       OrderAmountUSDT = round(balanceUSDT-1,1)

       Response = PlaceMarketOrder(client, 'Long', OrderAmountUSDT)
       sleep (5)

       if ( Response is not False ):       
          order_ID = Response['orderId']          
          print('Submitted Order ID: ', order_ID)
          order = client.get_order(symbol='BTCUSDT', orderId=order_ID)
          print (order)          
       else:
          print('Order was not submitted')  

    else:
       print('Skipped Order LONG')
       pass

##########################################################################################################

    print(' ==== Current position ==== ')
    sleep (1)    

    if ( GetCurrentPosition(client) is not False ):
       
       PositionType, PositionAmount, PositionPrice =  GetCurrentPosition(client)

       if ( PositionType == 'Long' ):
          print('Found position LONG:', PositionAmount, PositionPrice)
          isLongPosition = True          
          LongPositionAmount = PositionAmount 
          LongPositionPrice = PositionPrice
          
       elif ( PositionType == 'Short' ):
          print('Found position SHORT:', PositionAmount, PositionPrice)
          isShortPosition = True          
          ShortPositionAmount = PositionAmount
          ShortPositionPrice = PositionPrice

    print(' ==== Previous position ==== ') # PNL
    
    if ( GetPreviousPosition(client) is not False ):
       
       PositionType, PositionAmount, PositionPrice =  GetPreviousPosition(client)

       if ( PositionType == 'Long' ):
          print('Found position LONG:', PositionAmount, PositionPrice)
          isLongPosition = True          
          LongPositionAmount = PositionAmount 
          LongPositionPrice = PositionPrice
          
       elif ( PositionType == 'Short' ):
          print('Found position SHORT:', PositionAmount, PositionPrice)
          isShortPosition = True          
          ShortPositionAmount = PositionAmount
          ShortPositionPrice = PositionPrice

##########################################################################################################
##
    if ( GetOpenOrders(client) is not False ):
         print(' ==== Found opened orders ==== ')

    time.sleep(1)   
   
##########################################################################################################
      
