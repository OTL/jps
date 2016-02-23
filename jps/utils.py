import json
from .publisher import Publisher
from .common import DEFAULT_PUB_PORT
from .common import DEFAULT_HOST


class JsonMultiplePublisher(object):

    '''publish multiple topics by one json message

    Example:

    >>> p = JsonMultiplePublisher()
    >>> p.publish('{"topic1": 1.0, "topic2": {"x": 0.1}}')
    '''

    def __init__(self, host=DEFAULT_HOST, pub_port=DEFAULT_PUB_PORT):
        self._pub = Publisher('', host=host, pub_port=pub_port)

    def publish(self, json_msg):
        '''
        json_msg = '{"topic1": 1.0, "topic2": {"x": 0.1}}'
        '''
        pyobj = json.loads(json_msg)
        for topic, value in pyobj.items():
            msg = '{topic} {data}'.format(topic=topic, data=json.dumps(value))
            self._pub.publish(msg)
