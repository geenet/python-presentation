# -*- coding: utf-8 -*-
#from meinheld import patch
#patch.patch_all()
from bottle import Bottle, run, request
import json, time, datetime
app = Bottle()

@app.route('/')
@app.route("/:url_path#.+#")
def get_all(url_path=None):
    #if True:
    #    return "Hello"
    headers = get_headers()
    h=json.dumps(headers, sort_keys=True, indent=4)
    server_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    print "%s - %s => %s"%(server_time, url_path, h)

    #server = "10.10.201:9000"
    #request.url()

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


def rest(url, method, data, user=None, password=None):
    import httplib2
    h = httplib2.Http()
    if user and password:
        h.add_credentials(user, password)
    data = None if method=='GET' else data
    result = None
    try:
        response, content = h.request(url, method, data)
        result = content #if content else format_json(response)
    except:
        import traceback
        result = str(traceback.format_exc())
    return result

def urllib2_rest_auth(url, method='GET', data=None, user=None, password=None#,
                    #  access_token=None, as_json=False
):
    import urllib2, base64, json
    method = method.strip().upper()
    data = None if method in ['GET','DELETE'] else data # just to ensure only valid request are sent

    #httpHandler = urllib2.HTTPHandler()
    #httpHandler.set_http_debuglevel(1)

    #Instead of using urllib2.urlopen, create an opener, and pass the HTTPHandler
    #and any other handlers... to it.
    #opener = urllib2.build_opener(httpHandler)

    #import urllib2
    #urllib2.urlopen(url)

    request = urllib2.Request(url, data=data)
    request.get_method = lambda: method
    base64string = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    request.add_header("User-Agent", "Mozilla/5.0 (iPhone)")
    #if access_token:
    #    request.add_header("access_token", access_token)
    #urllib2._opener.handlers[1].set_http_debuglevel(100)
    urllib2.install_opener(urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1)))
    response = urllib2.urlopen(request)
    data = response.read()
    data =  json.loads(data) if as_json else data
    return response.getcode(), response.headers, data

def requests_rest_auth(url, method='GET', data=None, user=None, password=None, access_token=None,
                        as_json=False, data2json=True):
    import requests
    from bottle import request
    import logging
    # these two lines enable debugging at httplib level (requests->urllib3->httplib)
    # you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # the only thing missing will be the response.body which is not logged.
    import httplib
    httplib.HTTPConnection.debuglevel = 1
    # add debugging
    logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
    """
    http://stackoverflow.com/questions/10588644/how-can-i-see-the-entire-request-thats-being-sent-to-paypal-in-my-python-applic
    """
    method = method.strip().upper()
    auth = (user, password) if user and password else None
    if method in ['GET','DELETE']:  # just to ensure only valid request are sent
        if data and isinstance(data, dict):
            params = [ "%s=%s"%(a,b) for a,b in data.iteritems() ]
            params = '&'.join(params)
            url +='?'+params
        data = None
    elif data is not None and data2json:
        data = json.dumps(data)
    print "'"*1000
    print "URL:",url
    headers = dict(request.headers) # add all client headers
    headers.update(  {"Roboto-User-Agent": "Mozilla/5.0 (iPhone) Requests",
                      "X-Client-User-Agent": request.headers['User-Agent'],
                      "X-Client-IP": request['REMOTE_ADDR'] } )

    if access_token:
        headers["access_token"] = access_token
    r = requests.request(method, url, headers=headers, data=data, auth=auth)
    #data =  r.json() if as_json else r.text
    #print "status_code",r.status_code, "data",r.text
    return r




#from meinheld import server
#server.set_access_logger(None)
#server.set_error_logger(None)

#run(app, host='0.0.0.0', port=8030, server='meinheld')
# ab -c 1000 -t 60 http://localhost:8080/
run(app, host='0.0.0.0', port=8080)
