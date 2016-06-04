import json
import time

import jps


class MessageHolder(object):

    def __init__(self):
        self.saved_msg = []

    def __call__(self, msg):
        self.saved_msg.append(msg)

    
def test_pubsub_with_serialize_json():
    holder = MessageHolder()
    sub = jps.Subscriber('/serialize_hoge1', holder,
                         deserializer=json.loads)
    pub = jps.Publisher('/serialize_hoge1',
                        serializer=json.dumps)
    time.sleep(0.1)
    obj = {'da1': 1, 'name': 'hoge'}
    pub.publish(obj)
    time.sleep(0.1)
    sub.spin_once()
    assert len(holder.saved_msg) == 1
    assert holder.saved_msg[0]['da1'] == 1
    assert holder.saved_msg[0]['name'] == 'hoge'
