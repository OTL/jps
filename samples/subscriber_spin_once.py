import jps
import time


def callback(msg):
    print(msg)

sub = jps.Subscriber('/hoge1', callback)
try:
    while True:
        sub.spin_once()
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
