# -*- coding: utf-8 -*-

"""
sudo ab -n100000 -c5000 -r  http://localhost:8000/100

http://ziade.org/2012/06/28/wgsi-web-servers-bench/
http://pointlessramblings.com/posts/Lua_vs_Node_vs_LuaNginx.html

pypy wsgi-benchmark.py bjoern

"""
host,port="0.0.0.0", 8000
def cmd(cmd):
    import subprocess
    """from 
    http://www.saltycrane.com/blog/2009/10/how-capture-stdout-in-real-time-python/
    http://blog.kagesenshi.org/2008/02/teeing-python-subprocesspopen-output.html
    """
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = []
    while True:
        line = p.stdout.readline()
        stdout.append(line)
        print line,
        if line == '' and p.poll() != None:
            break
    return ''.join(stdout)
def hsize(data):
    '''
    print "Size:", hsize("Hello World!")
    '''
    if not data:
       raise ValueError('number must be non-negative')  
    size = len(str(data))
    unit = 1024 
    if size < unit:
        return str(size)+"bytes"
    for suffix in ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']:
        size /= unit
        if size < unit:
            return '{0:.1f} {1}'.format(size, suffix)
    raise ValueError('number too large')
data = {}
def get_data(n):
    global data
    res = data.get(n)
    if res:
       return res
    msg="Hello World 3000"
    if True:
       res = "a"*int(n*1024)
    else:
       res = msg*int(n*64)
    #print res
    print hsize(res)
    data[n]=res
    return res
def app(environ, start_response):
    status = '503 Error'
    txt = "Only /[KB_BTYTE_SIZE] supported"
    path = environ.get('PATH_INFO', '').strip()
    #print "path:"+str(path)
    path = path.replace("/","")
    #print "path:"+str(path)
    if path not in 'favicon.ico':
        n = float(path) if path else 1.0
        #print "n:"+str(n)
        txt = get_data(n)
        status = '200 OK'
    response_headers = [('Content-type','text/plain')]
    start_response(status, response_headers)
    return [txt]
application=app # the default application for uwsgi must be called "application". could not find a way to do this otherwise
def start(name):
    print "started server at "+str(host)+":"+str(port)
    if name =="meinheld":
        from meinheld import server
        server.set_access_logger(None)
        server.set_error_logger(None)
        server.listen((host, port))
        server.run(app)
    elif name =="gevent":
        #from gevent import wsgi 
        #wsgi.WSGIServer((host, port), application=app.application, log=None).serve_forever() 
        from gevent.pywsgi import WSGIServer
        WSGIServer((host, port), app, log=None).serve_forever()
    elif name =="bjoern":
        import bjoern
        bjoern.listen(app, host, port)
        bjoern.run() 
    elif name =="eventlet":
        import eventlet
        from eventlet import wsgi
        #worker_pool = eventlet.GreenPool(2000)
        #wsgi.server(eventlet.listen(('', port)), app, custom_pool=worker_pool, log=file('/dev/null', 'w'))
        # max_size
        wsgi.server(eventlet.listen(('', port)), app, max_size=10000, log=file('/dev/null', 'w'))
    elif name =="fapws":
        import fapws._evwsgi as evwsgi
        from fapws import base
        evwsgi.start(host, str(port)) 
        evwsgi.set_base_module(base)
        evwsgi.wsgi_cb(('/', app))
        evwsgi.set_debug(0)        
        evwsgi.run()
    elif name=="uwsgi":
        print ("""Enter this command in the console
                \nsudo uwsgi --http :8000 --master --disable-logging --pythonpath /home/a/g --wsgi-file w.py --listen 2  --buffer-size 2048 --async 10000 --ugreen -p 4
            """)
        #  http://osdir.com/ml/python-wsgi-uwsgi-general/2011-02/msg00136.html
        # 
        #  Re: strange SIGPIPE: writing to a closed pipe/socket/fd on image requested from facebook -msg#00136
        """
SIGPIPE: writing to a closed pipe/socket/fd (probably the client disconnected) on request /1 (ip 127.0.0.1) !!!
uwsgi_response_write_body_do(): Broken pipe [core/writer.c line 260]
IOError: write error
        """
        cmd_txt = "sudo uwsgi --http :8000 --master --harakiri 1 --harakiri-verbose --close-on-exec --disable-logging --pythonpath /home/a/todo/test --wsgi-file w2.py --listen 2  --buffer-size 2048 --async 10000 --ugreen -p 4"
        cmd(cmd_txt)
    elif name=="pycgi":
        from wsgiref.handlers import CGIHandler 
        CGIHandler().run(app)
    elif name=="pystandard":
        from wsgiref.simple_server import make_server
        make_server(host, port, app).serve_forever()
        
      
if __name__ == "__main__": 
    import sys
    from sys import argv
    print argv
    global default_size
    name = argv[1]
    #if len(argv) > 2:
    #    default_size = argv[2]
    #print default_size
    start(name)

