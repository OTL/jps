import zmq
from zmq.eventloop import ioloop, zmqstream


class Subscriber(object):

    def __init__(self, topic_name, callback, master_host='localhost',
                 master_sub_port=54320):
        context = zmq.Context()
        self._socket = context.socket(zmq.SUB)
        self._socket.connect("tcp://{host}:{port}".format(host=master_host,
                                                          port=master_sub_port))
        self._topic = topic_name
        self._socket.setsockopt(zmq.SUBSCRIBE, self._topic)
        ioloop.install()
        self._stream = zmqstream.ZMQStream(self._socket)
        self._stream.on_recv(self._callback)
        self._user_callback = callback

    def _callback(self, raw_msg_list):
        for raw_msg in raw_msg_list:
            topic, _, msg = raw_msg.partition(' ')
            self._user_callback(msg)

    def spin(self):
        try:
            ioloop.IOLoop.instance().start()
        finally:
            self._socket.close()


if __name__ == '__main__':
    def callback(msg):
        print msg
    s = Subscriber('hoge1', callback)
    s.spin()
