import hashlib
import os
import time

from .publisher import Publisher
from .subscriber import Subscriber

REQUEST_SUFFIX = '/request'
RESPONSE_SUFFIX = '/response'
ID_MESSAGE_DIVIDER = ' '


def add_id_to_payload(id_str, payload_msg):
    return 'id={}{}{}'.format(id_str, ID_MESSAGE_DIVIDER, payload_msg)


def get_id_and_payload(msg_with_id):
    div_index = msg_with_id.index(ID_MESSAGE_DIVIDER)
    request_id = msg_with_id[3:div_index]
    payload = msg_with_id[div_index + 1:]
    return (request_id, payload)


class ActionServer(object):

    '''serve the service which takes some long time

    Example:

    >>> import jps
    >>> import time
    >>> def callback(req):
    ...   time.sleep(1)
    ...   return req + ' received'
    >>> s = jps.ActionServer('move_to', callback)
    # subscribe 'move_to/request', publish 'move_to/response'
    >>> s.spin()
    '''

    def __init__(self, base_topic_name, callback, host=None, pub_port=None,
                 sub_port=None, serializer='DEFAULT', deserializer='DEFAULT'):
        self._req_subscriber = Subscriber(base_topic_name + REQUEST_SUFFIX,
                                          self._request_callback,
                                          host=host, sub_port=sub_port,
                                          deserializer=deserializer)
        self._res_publisher = Publisher(base_topic_name + RESPONSE_SUFFIX,
                                        host=host, pub_port=pub_port, serializer=serializer)
        self._user_callback = callback

    def _request_callback(self, msg):
        request_id, payload = get_id_and_payload(msg)
        result = self._user_callback(payload)
        self._res_publisher.publish(add_id_to_payload(request_id, result))

    def spin(self, use_thread=False):
        self._req_subscriber.spin(use_thread=use_thread)

    def spin_once(self):
        self._req_subscriber.spin_once()


class ActionResponseWaiter(object):

    def __init__(self, target_id, subscriber):
        self._target_id = target_id
        self._subscriber = subscriber

    def wait(self):
        for msg in self._subscriber:
            request_id, payload = get_id_and_payload(msg)
            if request_id == self._target_id:
                return payload


class ActionClient(object):

    '''Call an action

    Example:

    >>> import jps
    >>> import json
    >>> c = jps.ActionClient('move_to')
    >>> future = c(json.dumps({'x': 10.0, 'y': 0.1}))
    # do something if you are busy to do something during waiting.
    >>> result = future.wait()
    '''

    def __init__(self, base_topic_name, host=None, pub_port=None,
                 sub_port=None, serializer='DEFAULT', deserializer='DEFAULT'):
        self._req_publisher = Publisher(base_topic_name + REQUEST_SUFFIX,
                                        host=host, pub_port=pub_port, serializer=serializer)
        self._res_subscriber = Subscriber(base_topic_name + RESPONSE_SUFFIX,
                                          host=host, sub_port=sub_port,
                                          deserializer=deserializer)
        self._str_for_hash = self.__str__()

    def _create_hash(self):
        return hashlib.md5('{}_{}'.format(self._str_for_hash,
                                          time.time())).hexdigest()

    def __call__(self, msg):
        hash_val = self._create_hash()
        self._req_publisher.publish(add_id_to_payload(hash_val, msg))
        return ActionResponseWaiter(hash_val, self._res_subscriber)
