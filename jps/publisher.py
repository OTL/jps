import zmq
from zmq.utils.strtypes import cast_bytes

from .env import get_master_host
from .env import get_pub_port
from .env import get_topic_suffix
from .env import get_default_serializer
from .env import get_remapped_topic_name


class Publisher(object):

    '''Publishes data for a topic.

    Example:

    >>> pub = jps.Publisher('special_topic')
    >>> pub.publish('{"name": "hoge"}')

    :param topic_name: Topic name
    :param host: host of subscriber/forwarder
    :param pub_port: port of subscriber/forwarder
    :param serializer: this function is applied before publish (default: None)
    '''

    def __init__(self, topic_name, host=None, pub_port=None,
                 serializer='DEFAULT'):
        topic_name = get_remapped_topic_name(topic_name)
        if topic_name.count(' '):
            raise Exception('you can\'t use " " for topic_name')
        if host is None:
            host = get_master_host()
        if pub_port is None:
            pub_port = get_pub_port()
        if serializer is 'DEFAULT':
            serializer = get_default_serializer()
        self._serializer = serializer
        context = zmq.Context()
        self._socket = context.socket(zmq.PUB)
        self._socket.connect(
            'tcp://{host}:{port}'.format(host=host, port=pub_port))
        self._topic = cast_bytes(topic_name + get_topic_suffix())

    def publish(self, payload):
        '''Publish payload to the topic

        .. note:: If you publishes just after creating Publisher instance, it will causes
           lost of message. You have to add sleep if you just want to publish once.

           >>> pub = jps.Publisher('topic')
           >>> time.sleep(0.1)
           >>> pub.publish('{data}')

        :param payload: data to be published. This is ok if the data is not json.
        '''
        if self._serializer is not None:
            payload = self._serializer(payload)
        if self._topic == '*':
            # special case for publish everything
            msg = payload
        else:
            msg = '{topic} {data}'.format(topic=self._topic, data=payload)
        self._socket.send(cast_bytes(msg))
