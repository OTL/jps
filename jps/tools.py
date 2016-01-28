import argparse
import jps
import sys
import time


def pub(topic_name, json_msg, repeat_rate=None):
    pub = jps.Publisher(topic_name)
    time.sleep(0.1)
    if repeat_rate is None:
        pub.publish(json_msg)
    else:
        try:
            while True:
                pub.publish(json_msg)
                time.sleep(1.0 / repeat_rate)
        except KeyboardInterrupt:
            pass


def echo(topic_name):
    def callback(msg):
        print msg
    sub = jps.Subscriber(topic_name, callback)
    sub.spin()


def show_list(timeout_in_sec):
    class TopicNameStore(object):
        def __init__(self):
            self._topic_names = set()

        def callback(self, raw_msg):
            topic, _, msg = raw_msg.partition(' ')
            self._topic_names.add(topic)

        def get_topic_names(self):
            return list(self._topic_names)
    store = TopicNameStore()
    sub = jps.Subscriber('', store.callback)
    time.sleep(timeout_in_sec)
    sub.spin_once()
    print store.get_topic_names()


def topic_command():
    parser = argparse.ArgumentParser(description='json pub/sub tool')
    command_parsers = parser.add_subparsers(dest='command', help='command')

    pub_parser = command_parsers.add_parser('pub', help='publish topic from command line')
    pub_parser.add_argument('topic_name', type=str, help='name of topic')
    pub_parser.add_argument('data', type=str, help='json string data to be published')
    pub_parser.add_argument('--repeat', '-r', help='repeat in hz', type=float)

    echo_parser = command_parsers.add_parser('echo', help='show topic data')
    echo_parser.add_argument('topic_name', type=str, help='name of topic')

    list_parser = command_parsers.add_parser('list', help='show topic list')
    list_parser.add_argument('--time_out', '-t', help='timeout in sec', type=float,
                             default=1.0)
    args = parser.parse_args()

    if args.command == 'pub':
        pub(args.topic_name, args.data, repeat_rate=args.repeat)
    elif args.command == 'echo':
        echo(args.topic_name)
    elif args.command == 'list':
        show_list(args.time_out)
    else:
        parser.print_help()
