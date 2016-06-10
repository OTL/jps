ActionServer and ActionClient
=========================================

Do you know about actionlib of ROS? jps provide simple ActionServer and ActionClient.
If you want to provide some action which takes long time, how about using these classes.
It is made by pub/sub only, but it is possible to handle the response correctly,
because it manage what is the response of the request.

Below is a sample of ActionServer ::

  import jps
  import time
  
  def callback(req):
      time.sleep(1)
      print req + ' received'
      return True
  
  s = jps.ActionServer('move_to', callback)
  s.spin()


Below is a sample of ActionClient ::

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


It does not contain feedback topic, it is the difference between ROS.
