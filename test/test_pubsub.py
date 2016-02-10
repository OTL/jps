import jps
import time


class MessageHolder(object):

    def __init__(self):
        self._saved_msg = []

    def callback(self, msg):
        self._saved_msg.append(msg)

    def get_msg(self):
        return self._saved_msg


def test_pubsub_once():
    holder = MessageHolder()
    sub = jps.Subscriber('/hoge1', holder.callback)
    pub = jps.Publisher('/hoge1')
    time.sleep(0.1)
    pub.publish('hoge')
    time.sleep(0.1)
    sub.spin_once()
    assert len(holder.get_msg()) == 1
    assert holder.get_msg()[0] == 'hoge'


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
    sub_normal = jps.Subscriber('/hoge1', holder.callback)
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
    sub = jps.Subscriber('/hoge', holder.callback)
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
    sub = jps.Subscriber('/hoge1', holder.callback)
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
