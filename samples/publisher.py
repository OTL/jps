import jps
import time

pub = jps.Publisher('/hoge1')
i = 0
while True:
  pub.publish('hello! jps{0}'.format(i))
  i += 1
  time.sleep(0.5)
