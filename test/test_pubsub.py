import jps
import json
import time


class MessageHolder(object):

    def __init__(self):
        self._saved_msg = []

    def __call__(self, msg):
        self._saved_msg.append(msg)

    def get_msg(self):
        return self._saved_msg


def test_pubsub_once():
    holder = MessageHolder()
    sub = jps.Subscriber('/hoge1', holder)
    pub = jps.Publisher('/hoge1')
    time.sleep(0.1)
    pub.publish('hoge')
    time.sleep(0.1)
    sub.spin_once()
    assert len(holder.get_msg()) == 1
    assert holder.get_msg()[0] == 'hoge'


def test_pubsub_thread():
    holder = MessageHolder()
    sub = jps.Subscriber('thread1', holder)
    pub = jps.Publisher('thread1')
    sub.spin(use_thread=True)
    time.sleep(0.1)
    pub.publish('hoge')
    time.sleep(0.1)
    assert len(holder.get_msg()) == 1
    assert holder.get_msg()[0] == 'hoge'


def test_pubsub_direct_number():
    holder = MessageHolder()
    sub = jps.Subscriber('num1', holder)
    pub = jps.Publisher('num1')
    time.sleep(0.1)
    pub.publish(1)
    time.sleep(0.1)
    sub.spin_once()
    assert len(holder.get_msg()) == 1
    # number will be converted to string, because it is json
    assert holder.get_msg()[0] == '1'

    
def test_pubsub_indirect_number():
    holder = MessageHolder()
    sub = jps.Subscriber('num1', holder)
    pub = jps.Publisher('num1')
    time.sleep(0.1)
    pub.publish('{"x": 1}')
    time.sleep(0.1)
    sub.spin_once()
    assert len(holder.get_msg()) == 1
    assert json.loads(holder.get_msg()[0])['x'] == 1


def test_pubsub_iterator():
    sub = jps.Subscriber('/hoge1')
    pub = jps.Publisher('/hoge1')
    time.sleep(0.1)
    for a in range(5):
        pub.publish('hoge{}'.format(a))
    time.sleep(0.1)
    i = 0
    for msg in sub:
        assert msg == 'hoge{}'.format(i)
        i += 1
        if i == 5:
            return


def test_pubsub_iterator_with_normal():
    holder = MessageHolder()
    sub_normal = jps.Subscriber('/hoge1', holder)
    sub = jps.Subscriber('/hoge1')
    pub = jps.Publisher('/hoge1')
    time.sleep(0.1)
    for a in range(5):
        pub.publish('hoge{}'.format(a))
    time.sleep(0.1)
    i = 0
    for msg in sub:
        assert msg == 'hoge{}'.format(i)
        i += 1
        if i == 5:
            return
    sub_normal.spin_once()
    assert len(holder.get_msg()) == 5
    for a in range(5):
        assert holder.get_msg()[a] == 'hoge{}'.format(a)


def test_pubsub_near_names():
    holder = MessageHolder()
    sub = jps.Subscriber('/hoge', holder)
    pub1 = jps.Publisher('/hoge1')
    time.sleep(0.01)
    pub1.publish('aaa')
    sub.spin_once()
    assert len(holder.get_msg()) == 0

    pub2 = jps.Publisher('/hoge2')
    time.sleep(0.01)
    pub2.publish('bbb')
    sub.spin_once()
    assert len(holder.get_msg()) == 0

    pub3 = jps.Publisher('hoge')
    time.sleep(0.01)
    pub3.publish('ccc')
    sub.spin_once()
    assert len(holder.get_msg()) == 0


def test_pubsub_multi():
    holder = MessageHolder()
    sub = jps.Subscriber('/hoge1', holder)
    pub = jps.Publisher('/hoge1')
    time.sleep(0.01)
    pub.publish('hoge0')
    pub.publish('hoge1')
    pub.publish('hoge2')
    sub.spin_once()
    assert len(holder.get_msg()) == 3
    assert holder.get_msg()[0] == 'hoge0'
    assert holder.get_msg()[1] == 'hoge1'
    assert holder.get_msg()[2] == 'hoge2'
