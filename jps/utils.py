import json

from .publisher import Publisher
from .common import DEFAULT_PUB_PORT
from .common import DEFAULT_HOST
from .env import get_master_host
from .json_utils import to_obj
from .json_utils import dict_to_obj


class JsonMultiplePublisher(object):

    '''publish multiple topics by one json message

    Example:

    >>> p = JsonMultiplePublisher()
    >>> p.publish('{"topic1": 1.0, "topic2": {"x": 0.1}}')
    '''

    def __init__(self):
        self._pub = Publisher('*')

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
            self._publishers[topic_suffix] = Publisher(
                self._base_topic_name + topic_suffix)
        self._publishers[topic_suffix].publish(msg)
