import zmq


def main(sub_port=54321, pub_port=54320):
    try:
        context = zmq.Context(1)
        frontend = context.socket(zmq.SUB)
        backend = context.socket(zmq.PUB)

        frontend.bind('tcp://*:{sub_port}'.format(sub_port=sub_port))
        frontend.setsockopt(zmq.SUBSCRIBE, "")
        # Socket facing services
        backend.bind('tcp://*:{pub_port}'.format(pub_port=pub_port))
        zmq.device(zmq.FORWARDER, frontend, backend)
    except KeyboardInterrupt:
        pass
    finally:
        frontend.close()
        backend.close()
        context.term()


if __name__ == "__main__":
    main()
