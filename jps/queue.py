import zmq
from .args import ArgumentParser
from .env import get_res_port
from .env import get_req_port


def command():
    parser = ArgumentParser(description='jps queue',
                            service=True, publisher=False, subscriber=False)
    args = parser.parse_args()
    main(args.request_port, args.response_port)


def main(req_port=None, res_port=None):
    '''main of queue

    :param req_port: port for clients
    :param res_port: port for servers
    '''
    if req_port is None:
        req_port = get_req_port()
    if res_port is None:
        res_port = get_res_port()

    try:
        context = zmq.Context(1)
        frontend_service = context.socket(zmq.XREP)
        backend_service = context.socket(zmq.XREQ)
        frontend_service.bind('tcp://*:{req_port}'.format(req_port=req_port))
        backend_service.bind('tcp://*:{res_port}'.format(res_port=res_port))
        zmq.device(zmq.QUEUE, frontend_service, backend_service)
    except KeyboardInterrupt:
        pass
    finally:
        frontend_service.close()
        backend_service.close()
        context.term()


if __name__ == "__main__":
    main()
