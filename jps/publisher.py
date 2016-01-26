import zmq


class Publisher(object):

    def __init__(self, topic_name, master_host='localhost',
                 master_pub_port=54321):
        self._port = master_pub_port
        context = zmq.Context()
        self._socket = context.socket(zmq.PUB)
        self._socket.connect(
            "tcp://{host}:{port}".format(host=master_host, port=master_pub_port))
        self._topic = topic_name

    def publish(self, json_msg):
        msg = '{topic} {json}'.format(topic=self._topic, json=json_msg)
        self._socket.send(msg)

if __name__ == '__main__':
    import json
    import time
    p1 = Publisher('hoge1')
    p1_2 = Publisher('hoge1')
    p2 = Publisher('hoge2')
    dat = {'aa': 0, 'bb': 2}
    for r in range(10):
        dat['aa'] = r
        p1.publish(json.dumps(dat))
        p1.publish(json.dumps(dat))
        p1_2.publish(json.dumps(dat))
        p2.publish(json.dumps(dat))
        time.sleep(1.0)
