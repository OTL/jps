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


def test_bridge_with_launcher():
    # Use launcher for the test of launcher
    processes = jps.launcher.launch_modules(['jps.forwarder'],
                                            {'jps.forwarder': (55322, 55323)},
                                            kill_before_launch=True)
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

    os.kill(processes[0].pid, signal.SIGINT)
    processes[0].join(1.0)


def test_bridge_server():
    processes = jps.launcher.launch_modules(['jps.forwarder', 'jps.queue'],
                                            {'jps.forwarder': (56322, 56323),
                                             'jps.queue': (56324, 56325)},
                                            kill_before_launch=True)

    s = jps.BridgeServiceServer(('bridge_s3', 'bridge_s4'),
                                pub_port=56322, sub_port=56323, res_port=56325)
    c = jps.BridgeServiceClient(('bridge_s1', 'bridge_s2'), req_port=56324)

    s.spin(use_thread=True)
    c.spin(use_thread=True)
    # local to remote
    lp1 = jps.Publisher('bridge_s1')
    lp2 = jps.Publisher('bridge_s2')
    time.sleep(0.1)
    rs1 = jps.Subscriber('bridge_s1', sub_port=56323)
    rs2 = jps.Subscriber('bridge_s2', sub_port=56323)
    h3 = MessageHolder()
    rs3 = jps.Subscriber('bridge_s3', h3, sub_port=56323)

    time.sleep(0.1)
    lp1.publish('{"hoge1" : 2}')
    lp2.publish('{"hoge2" : 3}')

    assert rs1.next() == '{"hoge1" : 2}'
    assert rs2.next() == '{"hoge2" : 3}'
    rs3.spin_once()
    assert len(h3.saved_msg) == 0

    # remote to local
    rp1 = jps.Publisher('bridge_s1', pub_port=56322)
    rp3 = jps.Publisher('bridge_s3', pub_port=56322)
    rp4 = jps.Publisher('bridge_s4', pub_port=56322)
    time.sleep(0.1)
    h1 = MessageHolder()
    ls1 = jps.Subscriber('bridge_s1', h1)
    ls3 = jps.Subscriber('bridge_s3')
    ls4 = jps.Subscriber('bridge_s4')
    time.sleep(0.1)
    rp1.publish('hoge1')
    rp3.publish('hoge3')
    rp4.publish('hoge4')
    assert ls3.next() == 'hoge3'
    assert ls4.next() == 'hoge4'
    ls1.spin_once()
    assert len(h1.saved_msg) == 0
    s.close()
    for p in processes:
        os.kill(p.pid, signal.SIGINT)
        p.join(1.0)
