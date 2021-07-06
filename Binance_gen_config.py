import shelve
import os
import sys

api_key_30m = ""
api_secret_30m = ""
api_key_3m = ""
api_secret_3m = ""

conf_file_30m ="./binance_conf_30m.db"
conf_file_3m ="./binance_conf_3m.db"

if (len(sys.argv) < 2):
   print ('action not specified')       
   sys.exit()
      
else:
   action = sys.argv[1]
   if (action == "save"): 
      ######## save conf
      try:
        p=os.path.abspath(conf_file_30m)
        print('Using Config file for 30min: ',p)
        shelfFile = shelve.open(conf_file_30m)
        shelfFile['api'] = { 'api_key':'xxx', 'api_secret':'zzz' }
 
      finally:
        shelfFile.close()

      try:
        p=os.path.abspath(conf_file_3m)      
        print('Using Config file for 3min: ',p)          
        shelfFile = shelve.open(conf_file_3m)
        shelfFile['api'] = { 'api_key':'yyy', 'api_secret':'www' }
    
      finally:
        shelfFile.close()      

   if (action == "load"): 
      ######## load conf
      try:
        p=os.path.abspath(conf_file_30m)      
        print('Loading Config file for 30min: ',p)
        shelfFile = shelve.open(conf_file_30m)
    
        api_key_30m = shelfFile['api']['api_key']
        api_secret_30m = shelfFile['api']['api_secret']
        print ('api_key_30m=',api_key_30m)
        print ('api_secret_30m=',api_secret_30m)

      finally:
        shelfFile.close()

      try:
        p=os.path.abspath(conf_file_3m)      
        print('Loading Config file for 3min: ',p)
        shelfFile = shelve.open(conf_file_3m)
    
        api_key_3m = shelfFile['api']['api_key']
        api_secret_3m = shelfFile['api']['api_secret']
        print ('api_key_3m=',api_key_3m)
        print ('api_secret_3m=',api_secret_3m)

      finally:
        shelfFile.close()
      ## 
