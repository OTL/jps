import jps

def callback(msg):
    print 'hoge2 = {}'.format(msg)

sub2 = jps.Subscriber('/hoge2', callback)

for msg in jps.Subscriber('/hoge1'):
    print 'hoge1 is here!{}'.format(msg)
    sub2.spin_once()
