import json
from wsgiref import simple_server
def app(env, resp):
    resp('200 OK', [('Content-type', 'text/html')])
    #print pprint.pformat(env) # alternatively: pprint.pprint(env)
    header_list = ["<b>%s</b>=%s"%(k,v) for k,v in env.iteritems() if 'HTTP_' in k]
    env_list = ["<b>%s</b>=%s"%(k,v) for k,v in env.iteritems() ]
    header_text=  json.dumps(header_list, indent=4, sort_keys=True)
    env_text=  json.dumps(env_list, indent=4, sort_keys=True)
    html = '<h2>Headers</h2><pre>%s</pre><h2>Server Environment</h2><pre>%s</pre>'
    html = html%(header_text,env_text)
    return [html]
host,port='localhost',8000
print 'server at %s:%s'%(host,port)
server=simple_server.make_server('', port, app)
server.serve_forever()
