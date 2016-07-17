import os

import zmq

from .args import ArgumentParser
from . import env
from .security import Authenticator
from .security import create_certificates


def command():
    parser = ArgumentParser(description='jps queue',
                            service=True, publisher=False, subscriber=False)
    args = parser.parse_args()
    main(args.request_port, args.response_port)


def main(req_port=None, res_port=None, use_security=False):
    '''main of queue

    :param req_port: port for clients
    :param res_port: port for servers
    '''
    if req_port is None:
        req_port = env.get_req_port()
    if res_port is None:
        res_port = env.get_res_port()
    auth = None
    try:
        context = zmq.Context()
        frontend_service = context.socket(zmq.XREP)
        backend_service = context.socket(zmq.XREQ)
        if use_security:
            if not os.path.exists(env.get_server_public_key_dir()):
                create_certificates(env.get_server_public_key_dir())
            auth = Authenticator(env.get_server_public_key_dir())
            auth.set_server_key(
                frontend_service, env.get_server_secret_key_path())
            auth.set_client_key(backend_service, env.get_client_secret_key_path(),
                                env.get_server_public_key_path())
        frontend_service.bind('tcp://*:{req_port}'.format(req_port=req_port))
        backend_service.bind('tcp://*:{res_port}'.format(res_port=res_port))
        zmq.device(zmq.QUEUE, frontend_service, backend_service)
    except KeyboardInterrupt:
        pass
    finally:
        frontend_service.close()
        backend_service.close()
        context.term()
        if use_security and auth is not None:
            auth.stop()


if __name__ == "__main__":
    main()
