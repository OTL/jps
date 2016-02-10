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

    def callback(self, msg):
        self._saved_msg.append(msg)

    def get_msg(self):
        return self._saved_msg

    def clear_msg(self):
        self._saved_msg = []


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


def test_recordplay():
    import tempfile
    import os
    file_path_all = tempfile.gettempdir() + '/record_all.json'
    file_path = tempfile.gettempdir() + '/record2.json'
    print(file_path_all)
    print(file_path)
    record_all = Process(target=jps.tools.record, args=(file_path_all, []))
    record_all.start()
    record = Process(target=jps.tools.record, args=(file_path, ['/test_rec2']))
    record.start()

    time.sleep(0.1)

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

    with open(file_path_all) as f:
        json.loads(f.read())
    with open(file_path) as f:
        json.loads(f.read())

    holder1 = MessageHolder()
    sub1 = jps.Subscriber('/test_rec1', holder1.callback)
    holder2 = MessageHolder()
    sub2 = jps.Subscriber('/test_rec2', holder2.callback)
    time.sleep(0.1)
    play_all = Process(target=jps.tools.play, args=[file_path_all])
    play_all.start()
    time.sleep(0.1)
    play_all.join(2.0)
    time.sleep(0.1)
    sub1.spin_once()
    sub2.spin_once()

    assert holder1.get_msg() == ['a']
    assert holder2.get_msg() == ['b']

    holder1.clear_msg()
    holder2.clear_msg()

    play = Process(target=jps.tools.play, args=[file_path])
    play.start()
    time.sleep(0.1)
    play.join(2.0)
    time.sleep(0.1)
    sub1.spin_once()
    sub2.spin_once()

    assert holder1.get_msg() == []
    assert holder2.get_msg() == ['b']

    os.remove(file_path_all)
    os.remove(file_path)
