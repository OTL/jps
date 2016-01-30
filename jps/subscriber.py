import zmq
from zmq.utils.strtypes import cast_bytes
from zmq.utils.strtypes import cast_unicode
import time


class Subscriber(object):

    '''Subscribe the topic and call the callback function

    Example:

    >>> def callback(msg):
    ...   print msg
    ...
    >>> sub = jps.Subscriber('topic_name', callback)
    >>> sub.spin()

    :param topic_name: topic name
    :param master_host: host name of publisher/forwarder
    :param master_sub_port: port of publisher/forwarder
    '''

    def __init__(self, topic_name, callback, master_host='localhost',
                 master_sub_port=54320):
        if topic_name.count(' '):
            raise Exception('you can\'t use " " for topic_name')
        context = zmq.Context()
        self._socket = context.socket(zmq.SUB)
        self._socket.connect('tcp://{host}:{port}'.format(host=master_host,
                                                          port=master_sub_port))
        self._topic = topic_name
        self._socket.setsockopt(zmq.SUBSCRIBE, cast_bytes(self._topic))
        self._user_callback = callback
        self._poller = zmq.Poller()
        self._poller.register(self._socket, zmq.POLLIN)

    def _callback(self, raw_msg):
        topic, _, msg = raw_msg.partition(' ')
        if self._topic == '':
            self._user_callback(raw_msg)
        elif topic == self._topic:
            self._user_callback(msg)

    def spin_once(self):
        '''Read the queued data and call the callback for them.
        '''
        # parse all data
        while True:
            socks = dict(self._poller.poll(10))
            if socks.get(self._socket) == zmq.POLLIN:
                msg = self._socket.recv_string()
                self._callback(msg)
            else:
                return

    def spin(self):
        '''call spin_once() forever'''
        try:
            while True:
                self.spin_once()
                time.sleep(0.0001)
        except KeyboardInterrupt:
            pass
