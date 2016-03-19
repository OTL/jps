import jps
import json

def add_one_callback(req):
    req = json.loads(req)
    sum=req['a'] + req['b']
    print('a({a}) + b({b}) = {sum}'.format(a=req['a'], b=req['b'], sum=sum))
    return bytes(sum)
    
service = jps.ServiceServer(add_one_callback)
try:
    service.spin()
except KeyboardInterrupt:
    pass
