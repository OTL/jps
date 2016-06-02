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
                setattr(self, a, _to_obj(b))

        def to_json(self):
            return json.dumps(self.__dict__)

        def __str__(self):
            return self.to_json()

        def __repr__(self):
            return self.to_json()

    def _to_obj(json_dict_or_list):
        if isinstance(json_dict_or_list, (list, tuple)):
            return [_to_obj(x) for x in json_dict_or_list]
        if isinstance(json_dict_or_list, (dict)):
            return _obj(json_dict_or_list)
        return json_dict_or_list

    json_obj = json.loads(msg)
    return _to_obj(json_obj)
