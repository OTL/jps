import jps
import json
import time

    
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
    time.sleep(0.1)
    client = jps.ServiceClient()
    req1 = {'type': 'a', 'data': 'yyy'}
    req2 = {'type': 'b', 'add': '2'}
    assert client(json.dumps(req1)) == 'xxxyyyxxx'
    assert client(json.dumps(req2)) == '3'
    

test_json_service()
        
