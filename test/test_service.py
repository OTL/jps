import json
import os
import signal
import time

import jps


def test_json_service():
    def json_callback(req):
        req = json.loads(req)
        type = req['type']
        if type == 'a':
            data = bytes(req['data'])
            return 'xxx' + data + 'xxx'
        elif type == 'b':
            add = req['add']
            return bytes(int(add) + 1)

    service = jps.ServiceServer(json_callback)
    service.spin(use_thread=True)
    client = jps.ServiceClient()
    req1 = {'type': 'a', 'data': 'yyy'}
    req2 = {'type': 'b', 'add': '2'}
    assert client(json.dumps(req1)) == 'xxxyyyxxx'
    assert client(json.dumps(req2)) == '3'


def test_json_service_with_security():
    def json_callback(req):
        req = json.loads(req)
        type = req['type']
        if type == 'a':
            data = bytes(req['data'])
            return 'xxx' + data + 'xxx'
        elif type == 'b':
            add = req['add']
            return bytes(int(add) + 1)
    res_port = jps.env.get_res_port() + 10
    req_port = jps.env.get_req_port() + 10
    use_security = True
    import threading
    p = threading.Thread(target=jps.queue.main,
                         args=(req_port, res_port, use_security))
    p.daemon = True
    p.start()
    service = jps.ServiceServer(json_callback, res_port=res_port, use_security=use_security)
    service.spin(use_thread=True)
    client = jps.ServiceClient(req_port=req_port, use_security=use_security)
    req1 = {'type': 'a', 'data': 'yyy'}
    req2 = {'type': 'b', 'add': '2'}
    assert client(json.dumps(req1)) == 'xxxyyyxxx'
    assert client(json.dumps(req2)) == '3'
    p.join(1.0)
