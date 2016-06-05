import time
import threading

import jps

class MessageHolder(object):

    def __init__(self):
        self.saved_msg = []

    def __call__(self, msg):
        self.saved_msg.append(msg)


def test_bridge():
    t = threading.Thread(target=jps.forwarder.main, args=(55322, 55323))
    t.setDaemon(True)
    t.start()
    time.sleep(0.1)
    b = jps.Bridge(('bridge1', 'bridge2', 'bridge3', 'bridge4'),
                   remote_pub_port=55322, remote_sub_port=55323)
    b.spin()
    # local to remote
    lp1 = jps.Publisher('bridge1')
    lp2 = jps.Publisher('bridge2')
    time.sleep(0.1)
    rs1 = jps.Subscriber('bridge1', sub_port=55323)
    rs2 = jps.Subscriber('bridge2', sub_port=55323)
    time.sleep(0.1)
    lp1.publish('hoge1')
    lp2.publish('hoge2')
    assert rs1.next() == 'hoge1'
    assert rs2.next() == 'hoge2'

    # remote to local
    rp1 = jps.Publisher('bridge3', pub_port=55322)
    rp2 = jps.Publisher('bridge4', pub_port=55322)
    time.sleep(0.1)
    ls1 = jps.Subscriber('bridge3')
    ls2 = jps.Subscriber('bridge4')
    time.sleep(0.1)
    rp1.publish('hoge3')
    rp2.publish('hoge4')
    assert ls1.next() == 'hoge3'
    assert ls2.next() == 'hoge4'
