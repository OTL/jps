import jps

def callback(msg):
  print msg

sub = jps.Subscriber('/hoge1', callback)
sub.spin()
