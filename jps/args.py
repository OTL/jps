import argparse
from .common import DEFAULT_HOST
from .common import DEFAULT_PUB_PORT
from .common import DEFAULT_SUB_PORT
from .common import DEFAULT_RES_PORT
from .common import DEFAULT_REQ_PORT


class ArgumentParser(argparse.ArgumentParser):

    '''
    Create ArgumentParser with args (host/subscriber_port/publisher_port)

    Example:

    >>> parser = jps.ArgumentParser(description='my program')
    >>> args = parser.parse_args()
    >>> args.host
    'localhost'
    >>> args.subscriber_port
    54321
    >>> args.publisher_port
    54320

    :param subscriber add subscriber_port (default: True)
    :param publisher add publisher_port (default: True)

    '''

    def __init__(self, subscriber=True, publisher=True,
                 service=False, *args, **kwargs):
        super(ArgumentParser, self).__init__(*args, **kwargs)
        self.add_argument(
            '--host', type=str, help='fowarder host', default=DEFAULT_HOST)
        if subscriber:
            self.add_argument('--subscriber_port', type=int,
                              help='subscriber port', default=DEFAULT_SUB_PORT)
        if publisher:
            self.add_argument(
                '--publisher_port', type=int, help='publisher port', default=DEFAULT_PUB_PORT)
        if service:
            self.add_argument(
                '--request_port', type=int, help='request port', default=DEFAULT_REQ_PORT)
            self.add_argument(
                '--response_port', type=int, help='response port', default=DEFAULT_RES_PORT)
