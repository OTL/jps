from multiprocessing import Process
import threading
import os
import signal

from .args import ArgumentParser
from . import forwarder
from . import queue
from .common import DEFAULT_PUB_PORT
from .common import DEFAULT_SUB_PORT
from .common import DEFAULT_REQ_PORT
from .common import DEFAULT_RES_PORT


def command():
    parser = ArgumentParser(description='jps master', service=True)
    args = parser.parse_args()
    main(args.request_port, args.response_port,
         args.publisher_port, args.subscriber_port)
    
def main(req_port=DEFAULT_REQ_PORT, res_port=DEFAULT_RES_PORT,
         pub_port=DEFAULT_PUB_PORT, sub_port=DEFAULT_SUB_PORT):
    p1 = Process(target=queue.main, args=(req_port, res_port))
#    p2 = Process(target=forwarder.main, args=(pub_port, sub_port))
    p1.start()
    forwarder.main(pub_port, sub_port)
    p1.join()
#    p2.start()
#    try:
#        p1.join()
#        p2.join()
#    except:
#        pass
#    finally:
#        os.kill(p1.pid, signal.SIGINT)
#        os.kill(p2.pid, signal.SIGINT)
        
#    p1 = threading.Thread(target=queue.main, args=(req_port, res_port))
#    p1.setDaemon(True)
#    p1.start()
#    forwarder.main(pub_port, sub_port)
    
