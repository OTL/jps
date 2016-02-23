
import zmq
from zmq.utils.strtypes import cast_bytes
from .common import DEFAULT_PUB_PORT
from .common import DEFAULT_HOST


class Publisher(object):

    '''Publishes data for a topic.

    Example:

    >>> pub = jps.Publisher('special_topic')
    >>> pub.publish('{"name": "hoge"}')

    :param topic_name: Topic name
    :param host: host of subscriber/forwarder
    :param pub_port: port of subscriber/forwarder
    '''

    def __init__(self, topic_name, host=DEFAULT_HOST, pub_port=DEFAULT_PUB_PORT):
        if topic_name.count(' '):
            raise Exception('you can\'t use " " for topic_name')
        context = zmq.Context()
        self._socket = context.socket(zmq.PUB)
        self._socket.connect(
            'tcp://{host}:{port}'.format(host=host, port=pub_port))
        self._topic = cast_bytes(topic_name)

    def publish(self, json_msg):
        '''Publish json_msg to the topic

        .. note:: If you publishes just after creating Publisher instance, it will causes
           lost of message. You have to add sleep if you just want to publish once.

           >>> pub = jps.Publisher('topic')
           >>> time.sleep(0.1)
           >>> pub.publish('{data}')

        :param json_msg: data to be published. This is ok if the data is not json.
        '''
        if self._topic == '':
            # special case for publish everything
            msg = json_msg
        else:
            msg = '{topic} {json}'.format(topic=self._topic, json=json_msg)
        self._socket.send(cast_bytes(msg))
