from multiprocessing import Process
import threading
import os
import signal

from .args import ArgumentParser
from . import forwarder
from . import queue
from .env import get_pub_port
from .env import get_sub_port
from .env import get_req_port
from .env import get_res_port
from .env import get_use_service_security


def command():
    parser = ArgumentParser(description='jps master', service=True)
    args = parser.parse_args()
    main(args.request_port, args.response_port,
         args.publisher_port, args.subscriber_port)


def main(req_port=None, res_port=None,
         pub_port=None, sub_port=None):
    if req_port is None:
        req_port = get_req_port()
    if res_port is None:
        res_port = get_res_port()
    if pub_port is None:
        pub_port = get_pub_port()
    if sub_port is None:
        sub_port = get_sub_port()
    p1 = Process(target=queue.main, args=(
        req_port, res_port, get_use_service_security()))
    p1.start()
    forwarder.main(pub_port, sub_port)
    p1.join()
