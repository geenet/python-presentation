# -*- coding: utf-8 -*-
from meinheld import patch
patch.patch_all()
from bottle import Bottle, run, request
import json, time, datetime
app = Bottle()

@app.route('/')
@app.route("/:url#.+#")
def get_all(url_path=None):
    #if True:
    #    return "Hello"
    headers = get_headers()
    h=json.dumps(headers, sort_keys=True, indent=4)
    server_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    print "%s - %s => %s"%(server_time, url_path, h)

    server = "10.10.201:9000"
    request.url ()

    return """
<pre>bottle-hello
path:%s
server-time:<b>%s</b>
headers:%s
</pre>"""%(url_path, server_time, h)
def get_headers():
    h =  {}
    for a,k in request.headers.iteritems():
        h[a]=k
    return h
	
from meinheld import server
server.set_access_logger(None)
server.set_error_logger(None)	
run(app, host='0.0.0.0', port=8030, server='meinheld')
# ab -c 1000 -t 60 http://localhost:8080/

