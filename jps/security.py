import os

import zmq
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator


class Authenticator(object):

    def __init__(self, public_keys_dir):
        self._auth = ThreadAuthenticator(zmq.Context.instance())
        self._auth.start()
        self._auth.allow('*')
        self._auth.configure_curve(domain='*', location=public_keys_dir)

    def set_server_key(self, zmq_socket, server_secret_key_path):
        '''must call before bind'''
        server_public, server_secret = zmq.auth.load_certificate(
            server_secret_key_path)
        zmq_socket.curve_secretkey = server_secret
        zmq_socket.curve_publickey = server_public
        zmq_socket.curve_server = True

    def set_client_key(self, zmq_socket, client_secret_key_path, server_public_key_path):
        '''must call before bind'''
        client_public, client_secret = zmq.auth.load_certificate(
            client_secret_key_path)
        zmq_socket.curve_secretkey = client_secret
        zmq_socket.curve_publickey = client_public
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
