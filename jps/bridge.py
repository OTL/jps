import functools

from .publisher import Publisher
from .subscriber import Subscriber

class SingleTopicBridge(object):
    def __init__(self, topic, remote_host,
                 remote_pub_port=None, remote_sub_port=None):
        self._local_publisher = Publisher(topic)
        self._local_subscriber = Subscriber(topic, self.local_to_remote)
        self._remote_publisher = Publisher(topic, host=remote_host,
                                           pub_port=remote_pub_port)
        self._remote_subscriber = Subscriber(topic, self.remote_to_local,
                                             host=remote_host,
                                             sub_port=remote_sub_port)

    def spin(self):
        self._local_subscriber.spin(use_thread=True)
        self._remote_subscriber.spin(use_thread=True)

    def local_to_remote(self, msg):
        self._remote_publisher.publish(msg)

    def remote_to_local(self, msg):
        self._local_publisher.publish(msg)


class Bridge(object):
    def __init__(self, target_topic_names, remote_host=None,
                 remote_pub_port=None, remote_sub_port=None):
        self._bridges = []
        for topic in target_topic_names:
            self._bridges.append(SingleTopicBridge(
                topic, remote_host, remote_pub_port=remote_pub_port,
                remote_sub_port=remote_sub_port))

    def spin(self):
        for b in self._bridges:
            b.spin()
