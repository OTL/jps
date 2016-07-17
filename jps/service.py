import zmq
from zmq.utils.strtypes import cast_bytes
import threading
from . import env
from .security import Authenticator


class ServiceServer(object):

    '''
    Example:

    >>> def callback(req):
    ...   return 'req = {req}'.format(req=req)
    ...
    >>> service = jps.ServiceServer(callback)
    >>> service.spin()
    '''

    def __init__(self, callback, host=None, res_port=None, use_security=False):
        if host is None:
            host = env.get_master_host()
        context = zmq.Context()
        self._socket = context.socket(zmq.REP)
        self._auth = None
        if use_security:
            self._auth = Authenticator(env.get_server_public_key_dir())
            self._auth.set_server_key(
                self._socket, env.get_server_secret_key_path())

        if res_port is None:
            res_port = env.get_res_port()
        self._socket.connect(
            'tcp://{host}:{port}'.format(host=host, port=res_port))
        self._callback = callback
        self._thread = None

    def spin(self, use_thread=False):
        '''call callback for all data forever (until \C-c)

        :param use_thread: use thread for spin (do not block)
        '''
        if use_thread:
            if self._thread is not None:
                raise 'spin called twice'
            self._thread = threading.Thread(target=self._spin_internal)
            self._thread.setDaemon(True)
            self._thread.start()
        else:
            self._spin_internal()

    def _spin_internal(self):
        while True:
            self.spin_once()

    def spin_once(self):
        request = self._socket.recv()
        self._socket.send(cast_bytes(self._callback(request)))

    def __del__(self):
        if self._auth is not None:
            self._auth.stop()


class ServiceClient(object):

    def __init__(self, host=None, req_port=None, use_security=False):
        if host is None:
            host = env.get_master_host()
        context = zmq.Context()
        self._socket = context.socket(zmq.REQ)
        self._auth = None
        if use_security:
            self._auth = Authenticator(env.get_server_public_key_dir())
            self._auth.set_client_key(self._socket, env.get_client_secret_key_path(),
                                      env.get_server_public_key_path())

        if req_port is None:
            req_port = env.get_req_port()
        self._socket.connect(
            'tcp://{host}:{port}'.format(host=host, port=req_port))

    def call(self, request):
        self._socket.send(request)
        return self._socket.recv()

    __call__ = call

    def __del__(self):
        if self._auth is not None:
            self._auth.stop()
