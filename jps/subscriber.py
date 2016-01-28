import zmq
import time


class Subscriber(object):

    def __init__(self, topic_name, callback, master_host='localhost',
                 master_sub_port=54320):
        if topic_name.count(' '):
            raise Exception('you can\'t use " " for topic_name')
        context = zmq.Context()
        self._socket = context.socket(zmq.SUB)
        self._socket.connect("tcp://{host}:{port}".format(host=master_host,
                                                          port=master_sub_port))
        self._topic = topic_name
        self._socket.setsockopt(zmq.SUBSCRIBE, self._topic)
        self._user_callback = callback
        self._poller = zmq.Poller()
        self._poller.register(self._socket, zmq.POLLIN)

    def _callback(self, raw_msg):
        topic, _, msg = raw_msg.partition(' ')
        if topic == self._topic:
            self._user_callback(msg)

    def spin_once(self):
        # parse all data
        while True:
            socks = dict(self._poller.poll(10))
            if socks.get(self._socket) == zmq.POLLIN:
                msg = self._socket.recv()
                self._callback(msg)
            else:
                return

    def spin(self):
        try:
            while True:
                self.spin_once()
                time.sleep(0.0001)
        except KeyboardInterrupt:
            pass
