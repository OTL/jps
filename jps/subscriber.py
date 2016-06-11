import threading
import time
import types

import zmq
from zmq.utils.strtypes import cast_bytes

from .common import Error
from .env import get_master_host
from .env import get_sub_port
from .env import get_topic_suffix
from .env import get_default_deserializer
from .env import get_remapped_topic_name


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
    :param deserializer: this function is applied after received (default: None)
    '''

    def __init__(self, topic_name, callback=None, host=None, sub_port=None,
                 deserializer='DEFAULT'):
        topic_name = get_remapped_topic_name(topic_name)
        if topic_name.count(' '):
            raise Error('you can\'t use " " for topic_name')
        if topic_name == '':
            raise Error('empty topic name is not supported')
        if host is None:
            host = get_master_host()
        if sub_port is None:
            sub_port = get_sub_port()
        if deserializer is 'DEFAULT':
            deserializer = get_default_deserializer()
        self._deserializer = deserializer
        context = zmq.Context()
        self._socket = context.socket(zmq.SUB)
        self._socket.connect('tcp://{host}:{port}'.format(host=host,
                                                          port=sub_port))
        self._topic = cast_bytes(topic_name + get_topic_suffix())
        self._topic_without_star = self._topic.rstrip('*')
        self._socket.setsockopt(zmq.SUBSCRIBE, self._topic_without_star)
        self._user_callback = callback
        if type(callback) == types.MethodType:
            self._user_callback_takes_topic_name = callback.im_func.func_code.co_argcount == 3  # arg=[self, message, topic_name]
        elif type(callback) == types.FunctionType:
            self._user_callback_takes_topic_name = callback.func_code.co_argcount == 2  # arg=[message, topic_name]
        elif hasattr(callback, '__call__'):
            self._user_callback_takes_topic_name = callback.__call__.im_func.func_code.co_argcount == 3  # arg=[self, message, topic_name]
        else:
            self._user_callback_takes_topic_name = False
        if type(callback) == types.InstanceType:
            print 'argcoutn = ' + callback.func_code.co_argcount
        self._thread = None
        self._poller = zmq.Poller()
        self._poller.register(self._socket, zmq.POLLIN)

    def _strip_topic_name_if_not_wildcard(self, raw_msg):
        topic, _, msg = raw_msg.partition(' ')
        if self._topic != self._topic_without_star:
            return (msg, topic)
        elif topic == self._topic:
            return (msg, topic)
        return (None, topic)

    def deserialize(self, msg):
        if self._deserializer is not None:
            return self._deserializer(msg)
        return msg

    def _callback(self, raw_msg):
        if self._user_callback is None:
            return
        msg, topic_name = self._strip_topic_name_if_not_wildcard(raw_msg)
        if msg is not None:
            if self._user_callback_takes_topic_name:
                self._user_callback(self.deserialize(msg), topic_name)
            else:
                self._user_callback(self.deserialize(msg))

    def spin_once(self, polling_sec=0.010):
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
            socks = dict(self._poller.poll(polling_sec * 1000))
            if socks.get(self._socket) == zmq.POLLIN:
                msg = self._socket.recv()
                self._callback(msg)
            else:
                return

    def spin(self, use_thread=False):
        '''call callback for all data forever (until \C-c)

        :param use_thread: use thread for spin (do not block)
        '''
        if use_thread:
            if self._thread is not None:
                raise Error('spin called twice')
            self._thread = threading.Thread(target=self._spin_internal)
            self._thread.setDaemon(True)
            self._thread.start()
        else:
            self._spin_internal()

    def _spin_internal(self):
        for msg in self:
            if self._user_callback_takes_topic_name:
                self._user_callback(*msg)
            else:
                self._user_callback(self.deserialize(msg))

    def __iter__(self):
        return self

    def next(self):
        '''receive next data (block until next data)'''
        try:
            raw_msg = self._socket.recv()
        except KeyboardInterrupt:
            raise StopIteration()
        msg, topic_name = self._strip_topic_name_if_not_wildcard(raw_msg)
        if msg is None:
            return self.next()
        if self._user_callback_takes_topic_name:
            return (self.deserialize(msg), topic_name)
        else:
            return self.deserialize(msg)

    # for python3
    __next__ = next
