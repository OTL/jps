import zmq


class Publisher(object):
    '''Publishes data for a topic.

    Example:

    >>> pub = jps.Publisher('special_topic')
    >>> pub.publish('{"name": "hoge"}')

    :param topic_name: Topic name
    :param master_host: host of subscriber/forwarder
    :param master_pub_port: port of subscriber/forwarder
    '''

    def __init__(self, topic_name, master_host='localhost',
                 master_pub_port=54321):
        if topic_name.count(' '):
            raise Exception('you can\'t use " " for topic_name')
        self._port = master_pub_port
        context = zmq.Context()
        self._socket = context.socket(zmq.PUB)
        self._socket.connect(
            "tcp://{host}:{port}".format(host=master_host, port=master_pub_port))
        self._topic = topic_name

    def publish(self, json_msg):
        '''Publish json_msg to the topic

        :param json_msg: data to be published. This is ok if the data is not json.
        '''
        if self._topic == '':
            # special case for publish everything
            msg = json_msg
        else:
            msg = '{topic} {json}'.format(topic=self._topic, json=json_msg)
        self._socket.send(msg)
