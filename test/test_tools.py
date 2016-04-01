from __future__ import print_function
import jps
import json
import time
import signal
import os
from multiprocessing import Process
from threading import Thread
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class MessageHolder(object):

    def __init__(self):
        self._saved_msg = []

    def __call__(self, msg):
        self._saved_msg.append(msg)

    def get_msg(self):
        return self._saved_msg


def test_pubecho():
    echo_output = StringIO()
    echo_thread = Thread(target=jps.tools.echo,
                         args=('/test1', 1, echo_output))
    echo_thread.daemon = True
    echo_thread.start()
    time.sleep(0.01)
    jps.tools.pub('/test1', '{"json_msg1": 1.0}')
    echo_thread.join(5.0)
    assert echo_output.getvalue() == '{"json_msg1": 1.0}\n'
    echo_output.close()


def test_pubecho_repeat():
    echo_output = StringIO()
    echo_thread = Thread(target=jps.tools.echo,
                         args=('/test2', 2, echo_output))
    echo_thread.daemon = True
    echo_thread.start()
    time.sleep(0.01)
    pub_process = Process(target=jps.tools.pub, args=('/test2', 'a', 1.0))
    pub_process.start()
    time.sleep(1.5)
    os.kill(pub_process.pid, signal.SIGINT)
    pub_process.join(1.0)
    echo_thread.join(5.0)
    assert echo_output.getvalue() == 'a\na\n'
    echo_output.close()


def test_show_list():
    list_output = StringIO()
    show_thread = Thread(target=jps.tools.show_list, args=(0.5, list_output))
    show_thread.daemon = True
    show_thread.start()
    time.sleep(0.1)
    p1 = jps.Publisher('/test_topic1')
    p2 = jps.Publisher('/test_topic2')
    time.sleep(0.1)
    p1.publish('{a}')
    p2.publish('{b}')

    show_thread.join(2.0)
    assert list_output.getvalue() == '/test_topic1\n/test_topic2\n'
    list_output.close()

def atest_show_list_with_suffix():
    orig_suffix = jps.env.get_topic_suffix()
    os.environ['JPS_SUFFIX'] = '.r123'
    list_output = StringIO()
    show_thread = Thread(target=jps.tools.show_list, args=(0.5, list_output))
    show_thread.daemon = True
    show_thread.start()
    time.sleep(0.1)
    p1 = jps.Publisher('/test_topic1')
    p2 = jps.Publisher('/test_topic2')
    time.sleep(0.1)
    p1.publish('{a}')
    p2.publish('{b}')

    show_thread.join(2.0)
    assert list_output.getvalue() == '/test_topic1.r123\n/test_topic2.r123\n'
    list_output.close()
    os.environ['JPS_SUFFIX'] = orig_suffix

def test_recordplay():
    import tempfile
    import os
    file_path_all = '{0}/{1}{2}'.format(
        tempfile.gettempdir(), os.getpid(), 'record_all.json')
    file_path = '{0}/{1}{2}'.format(
        tempfile.gettempdir(), os.getpid(), 'record2.json')
    print(file_path_all)
    print(file_path)
    record_all = Process(target=jps.tools.record, args=(file_path_all, []))
    record_all.daemon = True
    record_all.start()
    record = Process(target=jps.tools.record, args=(file_path, ['/test_rec2']))
    record.daemon = True
    record.start()

    time.sleep(0.5)

    p1 = jps.Publisher('/test_rec1')
    p2 = jps.Publisher('/test_rec2')
    time.sleep(0.1)
    p1.publish('a')
    p2.publish('b')
    time.sleep(0.1)

    os.kill(record_all.pid, signal.SIGINT)
    os.kill(record.pid, signal.SIGINT)
    record_all.join(1.0)
    record.join(1.0)

    assert os.path.exists(file_path_all)
    assert os.path.exists(file_path)

    def print_file_and_check_json(path):
        with open(path) as f:
            data = f.read()
            print(data)
            json.loads(data)

    print_file_and_check_json(file_path_all)
    print_file_and_check_json(file_path)
    holder1 = MessageHolder()
    sub1 = jps.Subscriber('/test_rec1', holder1)
    sub2 = jps.Subscriber('/test_rec2')
    time.sleep(0.1)
    play_all = Process(target=jps.tools.play, args=[file_path_all])
    play_all.daemon = True
    play_all.start()
    time.sleep(0.1)
    play_all.join(2.0)

    assert sub1.next() == 'a'
    assert sub2.next() == 'b'

    play = Process(target=jps.tools.play, args=[file_path])
    play.daemon = True
    play.start()
    time.sleep(0.1)
    play.join(2.0)
    sub1.spin_once()

    assert holder1.get_msg() == []
    assert sub2.next() == 'b'

    os.remove(file_path_all)
    os.remove(file_path)
