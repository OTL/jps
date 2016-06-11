jps
=============

jps is simple pub/sub system for python(v2.7 is supported now).
It is very easy to install and it is easy to understand if you have experience of ROS(Robot Operating System).

see http://jps.readthedocs.org/

[![Build Status](https://travis-ci.org/OTL/jps.svg?branch=master)](https://travis-ci.org/OTL/jps)


Install
------------------

```bash
$ sudo pip install jps
```

If it fails, try below.

```bash
sudo apt-get install python2.7-dev
```

Publisher
---------------
`publisher.py`

```python
import jps
import time

pub = jps.Publisher('/hoge1')
i = 0
while True:
    pub.publish('hello! jps{0}'.format(i))
    i += 1
    time.sleep(0.5)
```

Subscriber
----------------------
`subscriber.py`

```python
import jps
for msg in jps.Subscriber('/hoge1'):
    print msg
```


How to Run
---------------
You need three consoles.

```bash
$ jps_master
```

```bash
$ python publisher.py
```

```bash
$ python subscriber.py
```

