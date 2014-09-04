# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
# <-- UTF-8 universal workaround done
default_host='0.0.0.0'
default_port= 8000

from gevent import monkey
monkey.patch_all()
from gevent.pywsgi import WSGIServer
from bottle import Bottle, request
import json, datetime

app = Bottle()

@app.route('/')
@app.route("/<url_path:re:.+>")
def get_all(url_path=None):
    url_path = request.fullpath
    headers =  {}
    for a,k in request.headers.iteritems():
        headers[a]=k
    h=json.dumps(headers, sort_keys=True, indent=4)
    server_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    print "%s - %s => %s"%(server_time, url_path, h)
    return """
<pre>bottle-info
path:%s
server-time:<b>%s</b>
headers:%s
</pre>"""%(url_path, server_time, h)

def main():
    import optparse
    parser = optparse.OptionParser(conflict_handler="resolve",usage='%prog --port=PORT --host=HOST')
    parser.add_option('-p', '--port', default=default_port, dest='port', type='int', help='Port to serve on (default %s)'%default_port)
    parser.add_option('-h', '--host', default=default_host, dest='host', type='str', help='Host for the application (default %s)'%default_host)
    options, args = parser.parse_args()
    host, port = options.host, options.port
    print "Server started at %s:%s"%(host,port)
    WSGIServer((host, port), app).serve_forever()

if __name__ == "__main__":
    main()

