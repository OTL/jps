import jps
import time
import json

try:
    client = jps.ServiceClient()
    req = {'a': 1, 'b': 2}
    while True:
        print('a({a}) + b({b})'.format(a=req['a'], b=req['b']))
        print(client(json.dumps(req)))
        req['a'] += 1
        req['b'] *= 2
        time.sleep(1)
except KeyboardInterrupt:
    pass
