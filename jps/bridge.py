from .publisher import Publisher
from .subscriber import Subscriber


class UploadSingleTopicBridge(object):

    def __init__(self, topic, remote_host=None, remote_pub_port=None):
        self._local_subscriber = Subscriber(topic, self.local_to_remote)
        self._remote_publisher = Publisher(topic, host=remote_host,
                                           pub_port=remote_pub_port)

    def spin(self):
        self._local_subscriber.spin(use_thread=True)

    def local_to_remote(self, msg):
        self._remote_publisher.publish(msg)


class DownloadSingleTopicBridge(object):

    def __init__(self, topic, remote_host=None, remote_sub_port=None):
        self._local_publisher = Publisher(topic)
        self._remote_subscriber = Subscriber(topic, self.remote_to_local,
                                             host=remote_host,
                                             sub_port=remote_sub_port)

    def spin(self):
        self._remote_subscriber.spin(use_thread=True)

    def remote_to_local(self, msg):
        self._local_publisher.publish(msg)


class Bridge(object):

    def __init__(
        self, upload_topic_names, download_topic_names, remote_host=None,
                 remote_pub_port=None, remote_sub_port=None):
        '''
        Pub/Sub in different jps network

        upload_topic_names and download_topic_names should not
        contain same names. It causes infinity loop.
        '''
        if len(set(set(upload_topic_names) & set(download_topic_names))) > 0:
            raise Exception('upload_topic_names and download_topic_names should not' +
                            'contain same names')
        self._bridges = []
        for topic in upload_topic_names:
            self._bridges.append(UploadSingleTopicBridge(
                topic, remote_host, remote_pub_port=remote_pub_port))
        for topic in download_topic_names:
            self._bridges.append(DownloadSingleTopicBridge(
                topic, remote_host, remote_sub_port=remote_sub_port))

    def spin(self):
        for b in self._bridges:
            b.spin()
