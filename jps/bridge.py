import json
import threading
import time

from .common import Error
from .publisher import Publisher
from .subscriber import Subscriber
from .service import ServiceServer
from .service import ServiceClient


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
            raise Error('upload_topic_names and download_topic_names should not' +
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


class BridgeServiceBase(object):
    PAYLOAD_KEY = 'bridge_topics'

    def __init__(self, topics, sub_port=None, pub_port=None):
        '''convert subscribed topic to service call and publish the return value as topic'''
        self._received_data = {}
        self._subscribers = {}
        self._publishers = {}
        self._pub_port = pub_port
        for topic in topics:
            self._subscribers[topic] = Subscriber(
                topic, self.callback_with_name, sub_port=sub_port)
            self._subscribers[topic].spin(use_thread=True)

    def callback_with_name(self, msg, topic_name):
        self._received_data[topic_name] = msg

    def publish_topic_data(self, topic_data):
        for topic, data in topic_data.iteritems():
            if topic not in self._publishers:
                self._publishers[topic] = Publisher(
                    topic, pub_port=self._pub_port)
                time.sleep(0.1)
            self._publishers[topic].publish(data)


class BridgeServiceClient(BridgeServiceBase):

    def __init__(self, upload_topics, frequency=10.0, sub_port=None, pub_port=None,
                 host=None, req_port=None, use_security=False):
        BridgeServiceBase.__init__(
            self, upload_topics, sub_port=sub_port, pub_port=pub_port)
        self._service_client = ServiceClient(
            host=host, req_port=req_port, use_security=use_security)
        self._thread = None
        self._frequency = frequency

    def spin(self, use_thread=False):
        if use_thread:
            if self._thread is not None:
                raise 'spin called twice'
            self._thread = threading.Thread(target=self._spin_internal)
            self._thread.setDaemon(True)
            self._thread.start()
        else:
            self._spin_internal()

    def _spin_internal(self):
        sleep_sec = 1.0 / self._frequency
        while True:
            self.spin_once()
            time.sleep(sleep_sec)

    def spin_once(self):
        ret = self._service_client(json.dumps(
            {BridgeServiceBase.PAYLOAD_KEY: self._received_data}))
        topic_data = json.loads(ret)
        # {"led": {"r": 5, "g": 10, "b": 255}, ...}
        self.publish_topic_data(topic_data)


class BridgeServiceServer(BridgeServiceBase):

    def __init__(self, download_topics, sub_port=None, pub_port=None,
                 res_port=None, use_security=False):
        BridgeServiceBase.__init__(
            self, download_topics, sub_port=sub_port, pub_port=pub_port)
        self._service_server = ServiceServer(
            self.callback, res_port=res_port, use_security=use_security)

    def callback(self, request):
        req_dict = json.loads(request)
        if BridgeServiceBase.PAYLOAD_KEY not in req_dict:
            return ''
        self.publish_topic_data(req_dict[BridgeServiceBase.PAYLOAD_KEY])
        return json.dumps(self._received_data)

    def spin(self, use_thread=False):
        self._service_server.spin(use_thread=use_thread)

    def close(self):
        self._service_server.close()
