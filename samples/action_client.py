import jps
import json
import time

c = jps.ActionClient('move_to')
time.sleep(0.1) # need this sleep
future = c(json.dumps({'x': 10.0, 'y': 0.1}))
print 'do something during waiting response'
time.sleep(1)
result = future.wait()
print result
