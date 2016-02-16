import zmq
from .args import ArgumentParser
from .common import DEFAULT_PUB_PORT
from .common import DEFAULT_SUB_PORT


def command():
    import argparse
    parser = ArgumentParser(description='jps forwarder')
    args = parser.parse_args()
    main(args.publisher_port, args.subscriber_port)


def main(pub_port=DEFAULT_PUB_PORT, sub_port=DEFAULT_SUB_PORT):
    '''main of forwarder

    :param sub_port: port for subscribers
    :param pub_port: port for publishers
    '''
    try:
        context = zmq.Context(1)
        frontend = context.socket(zmq.SUB)
        backend = context.socket(zmq.PUB)

        frontend.bind('tcp://*:{pub_port}'.format(pub_port=pub_port))
        frontend.setsockopt(zmq.SUBSCRIBE, b'')
        backend.bind('tcp://*:{sub_port}'.format(sub_port=sub_port))
        zmq.device(zmq.FORWARDER, frontend, backend)
    except KeyboardInterrupt:
        pass
    finally:
        frontend.close()
        backend.close()
        context.term()


if __name__ == "__main__":
    main()
