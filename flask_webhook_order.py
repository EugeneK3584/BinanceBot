from flask import Flask, request, abort
from types import SimpleNamespace
from time import sleep

import json
import subprocess
import time
import re

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    Dir = ""
    Strat = ""
    if request.method == 'POST':
        
        
        #print(request.json) #raw
        jtopy = json.dumps(request.json)
        dict_json = json.loads(jtopy, object_hook=lambda d: SimpleNamespace(**d))
        Dir = dict_json.ORDER.DIRECTION
        Strat = dict_json.ORDER.STRATEGY
        print("=====================================================")
        print(time.strftime("%Y-%m-%d %H:%M"))
        print(Strat, Dir)
        print("=====================================================")

        if (Dir == 'sell') and (Strat == 'BTCUSD_SUPERTREND_30'):
           subprocess.call("python3 BinanceBot.py Short virtual@ujl2gs2rnoemail.com", shell=True)           
        elif (Dir == 'buy') and (Strat == 'BTCUSD_SUPERTREND_30'):
           subprocess.call("python3 BinanceBot.py Long virtual@ujl2gs2rnoemail.com", shell=True)

        sleep(1)

        return Strat+' '+Dir+'\n', 200

    else:
        abort(400)


# run the app
if __name__ == '__main__':
   
    app.run(host='0.0.0.0',port='5000',debug=False, use_debugger=False, use_reloader=True)
    
