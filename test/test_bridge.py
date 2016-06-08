import multiprocessing
import os
import signal
import time

import jps

class MessageHolder(object):

    def __init__(self):
        self.saved_msg = []

    def __call__(self, msg):
        self.saved_msg.append(msg)


def test_bridge():
    forwarder_process = multiprocessing.Process(
        target=jps.forwarder.main, args=(55322, 55323))
    forwarder_process.start()
    time.sleep(0.1)
    b = jps.Bridge(('bridge1', 'bridge2'), ('bridge3', 'bridge4'),
                   remote_pub_port=55322, remote_sub_port=55323)
    b.spin()
    # local to remote
    lp1 = jps.Publisher('bridge1')
    lp2 = jps.Publisher('bridge2')
    time.sleep(0.1)
    rs1 = jps.Subscriber('bridge1', sub_port=55323)
    rs2 = jps.Subscriber('bridge2', sub_port=55323)
    h3 = MessageHolder()
    rs3 = jps.Subscriber('bridge3', h3, sub_port=55323)
    
    time.sleep(0.1)
    lp1.publish('hoge1')
    lp2.publish('hoge2')
    assert rs1.next() == 'hoge1'
    assert rs2.next() == 'hoge2'
    rs3.spin_once()
    assert len(h3.saved_msg) == 0

    # remote to local
    rp1 = jps.Publisher('bridge1', pub_port=55322)
    rp3 = jps.Publisher('bridge3', pub_port=55322)
    rp4 = jps.Publisher('bridge4', pub_port=55322)
    time.sleep(0.1)
    h1 = MessageHolder()
    ls1 = jps.Subscriber('bridge1', h1)
    ls3 = jps.Subscriber('bridge3')
    ls4 = jps.Subscriber('bridge4')
    time.sleep(0.1)
    rp1.publish('hoge1')
    rp3.publish('hoge3')
    rp4.publish('hoge4')
    assert ls3.next() == 'hoge3'
    assert ls4.next() == 'hoge4'
    ls1.spin_once()
    assert len(h1.saved_msg) == 0
    
    os.kill(forwarder_process.pid, signal.SIGINT)
    forwarder_process.join(1.0)
