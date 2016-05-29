import json

from .publisher import Publisher
from .common import DEFAULT_PUB_PORT
from .common import DEFAULT_HOST
from .env import get_master_host


class JsonMultiplePublisher(object):

    '''publish multiple topics by one json message

    Example:

    >>> p = JsonMultiplePublisher()
    >>> p.publish('{"topic1": 1.0, "topic2": {"x": 0.1}}')
    '''

    def __init__(self, host=get_master_host(), pub_port=DEFAULT_PUB_PORT):
        self._pub = Publisher('*', host=host, pub_port=pub_port)

    def publish(self, json_msg):
        '''
        json_msg = '{"topic1": 1.0, "topic2": {"x": 0.1}}'
        '''
        pyobj = json.loads(json_msg)
        for topic, value in pyobj.items():
            msg = '{topic} {data}'.format(topic=topic, data=json.dumps(value))
            self._pub.publish(msg)


class MultiplePublisher(object):
    def __init__(self, base_topic_name):
        self._publishers = {}
        self._base_topic_name = base_topic_name

    def publish(self, msg, topic_suffix=''):
        if topic_suffix not in self._publishers:
            self._publishers[topic_suffix] = Publisher(self._base_topic_name + topic_suffix)
        self._publishers[topic_suffix].publish(msg)


def to_obj(msg):
    class _obj(object):
        def __init__(self, d):
            for a, b in d.iteritems():
                if isinstance(b, (list, tuple)):
                    setattr(self, a, [_obj(x) if isinstance(x, dict) else x for x in b])
                else:
                    setattr(self, a, _obj(b) if isinstance(b, dict) else b)
        def to_json(self):
            return json.dumps(self.__dict__)

    json_obj = json.loads(msg)
    if isinstance(json_obj, (list)):
        return [_obj(x) for x in json_obj]
    return _obj(json_obj)
