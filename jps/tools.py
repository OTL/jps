import argparse
import datetime
import jps
import json
import os
import signal
import sys
import time


def pub(topic_name, json_msg, repeat_rate=None):
    '''publishes the data to the topic

    :param topic_name: name of the topic
    :param json_msg: data to be published
    :param repeat_rate: if None, publishes once. if not None, it is used as [Hz].
    '''
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


def echo(topic_name, num_print=None, out=sys.stdout):
    '''print the data for the given topic forever
    '''
    class PrintWithCount(object):

        def __init__(self, out):
            self._printed = 0
            self._out = out

        def print_and_increment(self, msg):
            self._out.write('{}\n'.format(msg))
            self._printed += 1

        def get_count(self):
            return self._printed

    counter = PrintWithCount(out)
    sub = jps.Subscriber(topic_name, counter.print_and_increment)
    try:
        while num_print is None or counter.get_count() < num_print:
            sub.spin_once()
            time.sleep(0.0001)
    except KeyboardInterrupt:
        pass


def show_list(timeout_in_sec, out=sys.stdout):
    '''get the name list of the topics, and print it
    '''
    class TopicNameStore(object):

        def __init__(self):
            self._topic_names = set()

        def callback(self, raw_msg):
            topic, _, msg = raw_msg.partition(' ')
            self._topic_names.add(topic)

        def get_topic_names(self):
            names = list(self._topic_names)
            names.sort()
            return names

    store = TopicNameStore()
    sub = jps.Subscriber('', store.callback)
    sleep_sec = 0.01
    for i in range(int(timeout_in_sec / sleep_sec)):
        sub.spin_once()
        time.sleep(sleep_sec)
    for name in store.get_topic_names():
        out.write('{}\n'.format(name))


def record(file_path, topic_names=[]):
    '''record the topic data to the file
    '''
    class TopicRecorder(object):

        def __init__(self, file_path, topic_names):
            self._topic_names = topic_names
            self._file_path = file_path
            self._output = open(self._file_path, 'w')
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)
            header = {}
            header['topic_names'] = topic_names
            header['start_date'] = str(datetime.datetime.today())
            header_string = json.dumps({'header':header})
            tail_removed_header = header_string[0:-1]
            self._output.write(tail_removed_header + ',\n')
            self._output.write(' "data": [\n')
            self._has_no_data = True

        def callback(self, raw_msg):
            if self._output.closed:
                return
            topic, _, msg = raw_msg.partition(' ')
            if not self._topic_names or topic in self._topic_names:
                if not self._has_no_data:
                    self._output.write(',\n')
                else:
                    self._has_no_data = False
                self._output.write(json.dumps([time.time(), raw_msg]))
        def close(self):
            if not self._output.closed:
                self._output.write('\n]}')
                self._output.close()

        def _handle_signal(self, signum, frame):
            self.close()
            sys.exit(0)

    writer = TopicRecorder(file_path, topic_names)
    sub = jps.Subscriber('', writer.callback)
    sub.spin()
    writer.close()


def play(file_path):
    '''replay the recorded data by record()
    '''
    pub = jps.Publisher('')
    time.sleep(0.1)
    last_time = None
    with open(file_path, 'r') as f:
        # super hack to remove header
        f.readline()
        f.readline()
        for line in f:
            if line.startswith(']}'):
                break
            publish_time, raw_msg = json.loads(line.rstrip(',\n'))
            if last_time is not None:
                time.sleep(publish_time - last_time)
            pub.publish(raw_msg.rstrip())
            last_time = publish_time


def topic_command():
    '''command line tool for jps
    '''
    parser = argparse.ArgumentParser(description='json pub/sub tool')
    command_parsers = parser.add_subparsers(dest='command', help='command')

    pub_parser = command_parsers.add_parser(
        'pub', help='publish topic from command line')
    pub_parser.add_argument('topic_name', type=str, help='name of topic')
    pub_parser.add_argument(
        'data', type=str, help='json string data to be published')
    pub_parser.add_argument('--repeat', '-r', help='repeat in hz', type=float)

    echo_parser = command_parsers.add_parser('echo', help='show topic data')
    echo_parser.add_argument('topic_name', type=str, help='name of topic')
    echo_parser.add_argument(
        '--num', '-n', help='print N times and exit', type=int,
                             default=None)

    list_parser = command_parsers.add_parser('list', help='show topic list')
    list_parser.add_argument(
        '--timeout', '-t', help='timeout in sec', type=float,
                             default=1.0)

    record_parser = command_parsers.add_parser(
        'record', help='record topic data')
    record_parser.add_argument('topic_names', nargs='*',
                               help='topic names to be recorded', type=str)
    record_parser.add_argument(
        '--file', '-f', help='output file name (default: record.json)',
                               type=str, default='record.json')

    play_parser = command_parsers.add_parser(
        'play', help='play recorded topic data')
    play_parser.add_argument(
        '--file', '-f', help='input file name (default: record.json)',
                             type=str, default='record.json')

    args = parser.parse_args()

    if args.command == 'pub':
        pub(args.topic_name, args.data, repeat_rate=args.repeat)
    elif args.command == 'echo':
        echo(args.topic_name, args.num)
    elif args.command == 'list':
        show_list(args.timeout)
    elif args.command == 'record':
        record(args.file, args.topic_names)
    elif args.command == 'play':
        play(args.file)
    else:
        parser.print_help()
