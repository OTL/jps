import jps
import time

def callback(req):
    time.sleep(1)
    print req + ' received'
    return True

s = jps.ActionServer('move_to', callback)
s.spin()
