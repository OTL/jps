Simple Subscriber
====================

If your subscriber is simple you can write it easier than ROS style.
Simple means below here.

- subscribe only one topic
- just while loop main function

simple_subscriber::

  import jps
  
  
  for msg in jps.Subscriber('/hoge1'):
      print msg


This prints /hoge1 messages.

You can mix the two style if you want. ::


  import jps
  
  def callback(msg):
      print 'hoge2 = {}'.format(msg)
  
  sub2 = jps.Subscriber('/hoge2', callback)
  for msg in jps.Subscriber('/hoge1'):
      print 'hoge1 is here!{}'.format(msg)
      sub2.spin_once()

