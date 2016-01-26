import jps
import sys
import time


def pub(topic_name, json_msg):
    pub = jps.Publisher(topic_name)
    time.sleep(0.1)
    pub.publish(json_msg)


def echo(topic_name):
    def callback(msg):
        print msg
    sub = jps.Subscriber(topic_name, callback)
    sub.spin()


def echo_command():
    echo(sys.argv[1])


def pub_command():
    pub(sys.argv[1], sys.argv[2])
