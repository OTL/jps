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


def test_multi_pubsub_once():
    holder1 = MessageHolder()
    holder2 = MessageHolder()
    holder3 = MessageHolder()
    sub1 = jps.Subscriber('test_utils1', holder1)
    sub2 = jps.Subscriber('test_utils2', holder2)
    sub3 = jps.Subscriber('test_utils3', holder3)
    pub = jps.utils.JsonMultiplePublisher()
    time.sleep(0.1)
    pub.publish('{"test_utils1": "hoge", "test_utils2": {"x": 3}, "test_utils3": 5}')
    time.sleep(0.1)
    sub1.spin_once()
    sub2.spin_once()
    sub3.spin_once()
    assert len(holder1.get_msg()) == 1
    assert json.loads(holder1.get_msg()[0]) == 'hoge'
    assert len(holder2.get_msg()) == 1
    obj = json.loads(holder2.get_msg()[0])
    assert obj['x'] == 3
    assert len(holder3.get_msg()) == 1
    assert json.loads(holder3.get_msg()[0]) == 5


def test_to_obj():
    msg = '{"aa": 1, "bb": ["hoge", "hogi"], "cc": {"cc1" : 50}}'
    converted = jps.utils.to_obj(msg)
    assert converted.aa == 1
    assert converted.bb[0] == 'hoge'
    assert converted.bb[1] == 'hogi'
    assert len(converted.bb) == 2
    assert converted.cc.cc1 == 50
