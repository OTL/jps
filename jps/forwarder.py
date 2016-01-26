import zmq


def main():
    try:
        context = zmq.Context(1)
        frontend = context.socket(zmq.SUB)
        frontend.bind("tcp://*:54321")
        frontend.setsockopt(zmq.SUBSCRIBE, "")

        # Socket facing services
        backend = context.socket(zmq.PUB)
        backend.bind("tcp://*:54320")
        zmq.device(zmq.FORWARDER, frontend, backend)
    except Exception, e:
        print e
        print "bringing down zmq device"
    finally:
        frontend.close()
        backend.close()
        context.term()


if __name__ == "__main__":
    main()
