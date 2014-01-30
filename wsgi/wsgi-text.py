import pprint
from wsgiref import simple_server
host,port='localhost',8000
def app(env, resp):
    resp('200 OK', [('Content-type', 'text/plain')])
    return [ pprint.pformat(env) ]
print 'server at %s:%s'%(host,port)
server=simple_server.make_server('', port, app)
server.serve_forever()
