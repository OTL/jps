import jps


def test_args():
    parser = jps.ArgumentParser(description='my program')
    args = parser.parse_args(['--host', '192.168.0.3'])
    assert args.host == '192.168.0.3'

    args = parser.parse_args(['--host', '192.168.0.2', '--publisher_port', '100', '--subscriber_port', '200'])
    assert args.host == '192.168.0.2'
    assert args.publisher_port == 100
    assert args.subscriber_port == 200
