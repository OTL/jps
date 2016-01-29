Introduction
================

jps(json pub/sub) is small wrapper of `zeromq <http://zeromq.org/>`_.
It provides simple Pub/Sub system and command line tools, which is
strongly inspired by `ROS(Robot Operating System) <http://ros.org>`_.
jps is easier to install than ROS, and it does not have serialization.
Let's use json format.

How to install
---------------

You can use pip to install jps ::

  $ sudo pip install jps

It installs jps python module, ``jps_fowarder`` and :ref:`jps_topic` command.

How to write pub/sub
--------------------

publisher.py ::

  import jps
  import time
  
  pub = jps.Publisher('/hoge1')
  i = 0
  while True:
    pub.publish('hello! jps{0}'.format(i))
    i += 1
    time.sleep(0.5)

subscriber.py ::

  import jps
  
  def callback(msg):
    print msg

  sub = jps.Subscriber('/hoge1', callback)
  sub.spin()


How to run and use tools
--------------------------

You need three consoles to test the program. ::

  $ jps_forwarder
  $ python publisher.py
  $ python subscriber.py

To get the list of the topics, you can use jps_topic list ::

  $ jps_topic list

If you want to see the data in /hoge1 topic, ::

  $ jps_topic echo /hoge1
  