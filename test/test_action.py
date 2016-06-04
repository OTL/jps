import time

import jps


class MessageHolder(object):

    def __init__(self):
        self.saved_msg = []

    def __call__(self, msg):
        self.saved_msg.append(msg)

        
def test_client():
    h = MessageHolder()
    c = jps.ActionClient('action0')
    req_sub = jps.Subscriber('action0/request', h)
    time.sleep(0.05)
    c('req1')
    req1 = req_sub.next()
    assert req1.startswith('id=')
    assert req1.endswith('req1')
    c('req2')
    req2 = req_sub.next()
    assert req2.startswith('id=')
    assert req2.endswith('req2')

    
def test_server():
    def callback(msg):
        return msg + 'hoge'
    s = jps.ActionServer('action1', callback)
    res_sub = jps.Subscriber('action1/response')
    req_pub = jps.Publisher('action1/request')
    time.sleep(0.1)
    req_pub.publish('id=dummyhash req0')
    time.sleep(0.1)
    s.spin_once()
    res = res_sub.next()
    assert res.startswith('id=')
    assert res.endswith('req0hoge')

    
def test_server_client():
    def callback(msg):
        return msg + 'hoge'
    s = jps.ActionServer('action2', callback)
    s.spin(use_thread=True)
    time.sleep(0.1)
    c = jps.ActionClient('action2')
    time.sleep(0.1)
    future = c('call1')
    # do something
    result = future.wait()
    assert result == 'call1hoge'


def test_server_multi_client():
    def callback(msg):
        return msg + '_hoge'
    s = jps.ActionServer('action3', callback)
    s.spin(use_thread=True)
    time.sleep(0.1)
    c1 = jps.ActionClient('action2')
    c2 = jps.ActionClient('action2')
    time.sleep(0.1)
    future1 = c1('call1')
    future2 = c2('call2')
    # do something
    result2 = future2.wait()
    result1 = future1.wait()
    assert result1 == 'call1_hoge'
    assert result2 == 'call2_hoge'
