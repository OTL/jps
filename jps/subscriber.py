import zmq
from zmq.utils.strtypes import cast_bytes
from zmq.utils.strtypes import cast_unicode
import time
from .common import DEFAULT_SUB_PORT
from .common import DEFAULT_HOST


class Subscriber(object):

    '''Subscribe the topic and call the callback function

    Example:

    >>> def callback(msg):
    ...   print msg
    ...
    >>> sub = jps.Subscriber('topic_name', callback)
    >>> sub.spin()

    or you can use python generator style

    >>> import jps
    >>> for msg in jps.Subscriber('/hoge1'):
    ...   print msg

    :param topic_name: topic name
    :param host: host name of publisher/forwarder
    :param sub_port: port of publisher/forwarder
    '''

    def __init__(self, topic_name, callback=None, host=DEFAULT_HOST,
                 sub_port=DEFAULT_SUB_PORT):
        if topic_name.count(' '):
            raise Exception('you can\'t use " " for topic_name')
        context = zmq.Context()
        self._socket = context.socket(zmq.SUB)
        self._socket.connect('tcp://{host}:{port}'.format(host=host,
                                                          port=sub_port))
        self._topic = topic_name
        self._socket.setsockopt(zmq.SUBSCRIBE, cast_bytes(self._topic))
        self._user_callback = callback
        self._poller = zmq.Poller()
        self._poller.register(self._socket, zmq.POLLIN)

    def _strip_topic_name_if_not_wildcard(self, raw_msg):
        # for python3
        raw_msg = cast_unicode(raw_msg)
        topic, _, msg = raw_msg.partition(' ')
        # wildcard('')
        if self._topic == '':
            return raw_msg
        elif topic == self._topic:
            return msg
        return None

    def _callback(self, raw_msg):
        if self._user_callback is None:
            return
        msg = self._strip_topic_name_if_not_wildcard(raw_msg)
        if msg is not None:
            self._user_callback(msg)

    def spin_once(self):
        '''Read the queued data and call the callback for them.
        You have to handle KeyboardInterrupt (\C-c) manually.

        Example:

        >>> def callback(msg):
        ...   print msg
        >>> sub = jps.Subscriber('topic_name', callback)
        >>> try:
        ...   while True:
        ...     sub.spin_once():
        ...     time.sleep(0.1)
        ... except KeyboardInterrupt:
        ...   pass

        '''
        # parse all data
        while True:
            socks = dict(self._poller.poll(10))
            if socks.get(self._socket) == zmq.POLLIN:
                msg = self._socket.recv()
                self._callback(msg)
            else:
                return

    def spin(self):
        '''call callback for all data forever (until \C-c)'''
        for msg in self:
            self._user_callback(msg)

    def __iter__(self):
        return self

    def next(self):
        '''receive next data (block until next data)'''
        try:
            raw_msg = self._socket.recv()
        except KeyboardInterrupt:
            raise StopIteration()
        msg = self._strip_topic_name_if_not_wildcard(raw_msg)
        if msg is None:
            return self.next()
        return msg

    # for python3
    __next__ = next
