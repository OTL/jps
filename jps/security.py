import os

import zmq
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator


def load_and_set_key(zmq_socket, key_path):
    public, secret = zmq.auth.load_certificate(key_path)
    zmq_socket.curve_secretkey = secret
    zmq_socket.curve_publickey = public


class Authenticator(object):
    _authenticators = {}

    @classmethod
    def instance(cls, public_keys_dir):
        '''Please avoid create multi instance'''
        if public_keys_dir in cls._authenticators:
            return cls._authenticators[public_keys_dir]
        new_instance = cls(public_keys_dir)
        cls._authenticators[public_keys_dir] = new_instance
        return new_instance

    def __init__(self, public_keys_dir):
        self._auth = ThreadAuthenticator(zmq.Context.instance())
        self._auth.start()
        self._auth.allow('*')
        self._auth.configure_curve(domain='*', location=public_keys_dir)

    def set_server_key(self, zmq_socket, server_secret_key_path):
        '''must call before bind'''
        load_and_set_key(zmq_socket, server_secret_key_path)
        zmq_socket.curve_server = True

    def set_client_key(self, zmq_socket, client_secret_key_path, server_public_key_path):
        '''must call before bind'''
        load_and_set_key(zmq_socket, client_secret_key_path)
        server_public, _ = zmq.auth.load_certificate(server_public_key_path)
        zmq_socket.curve_serverkey = server_public

    def stop(self):
        self._auth.stop()


def create_certificates(keys_dir='certificates'):
    if not os.path.exists(keys_dir):
        os.mkdir(keys_dir)
    server_public_file, server_secret_file = zmq.auth.create_certificates(
        keys_dir, "server")
    client_public_file, client_secret_file = zmq.auth.create_certificates(
        keys_dir, "client")


if __name__ == '__main__':
    keys_dir = 'certificates'
    import sys
    if len(sys.argv) > 1:
        keys_dir = sys.argv[1]
    create_certificates(keys_dir)
