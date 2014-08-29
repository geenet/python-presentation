# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
# <-- UTF-8 universal workaround done
default_host='0.0.0.0'
default_port=8080
"""
wsgi servers: gunicorn,gevent,uwsgi,meinheld,....
"""
import re
re_flags=re.IGNORECASE|re.MULTILINE|re.DOTALL|re.UNICODE
from gevent import monkey
monkey.patch_all()
from gevent.pywsgi import WSGIServer
from bottle import Bottle, run, request, response, HTTPResponse
import json, time, datetime

# start bottle application
app = Bottle()

def main():
    import optparse
    parser = optparse.OptionParser(conflict_handler="resolve",usage='%prog --port=PORT --host=HOST')
    parser.add_option('-p', '--port', default=default_port, dest='port', type='int', help='Port to serve on (default %s)'%default_port)
    parser.add_option('-h', '--host', default=default_host, dest='host', type='str', help='Host for the application (default %s)'%default_host)
    options, args = parser.parse_args()
    host, port = options.host, options.port
    # ab -c 1000 -t 60 http://localhost:8080/
    #run(app, host=host, port=port)
    print "Server started at %s:%s"%(host,port)
    #WSGIServer((host, port), app, log=None).serve_forever()
    WSGIServer((host, port), app).serve_forever()

@app.route('/')
@app.route("/<url_path:re:.+>")
def proxy(url_path=None):

    domain = request.headers.get('domain')
    if not domain or ('ilovevideo.tv' not in domain and 'zaporwatch.it' not in domain):
        domain = request.GET.get('domain') or 'de.ilovevideo.tv'

    url_path = '/' + (url_path or '')
    timeout = 3 if not request.fullpath.startswith('/url') else 10
    data = request.GET if request.method == 'GET' else request.POST

    # one request at a time - timeout early

    res = requests_rest_auth(domain=domain, url_path=url_path, data=data, timeout=timeout)
    print "status_code:",res.status_code
    page_path = request.fullpath

    content = res.content
    duration = int(res.elapsed.total_seconds() * 1000)
    headers = res.headers
    status_code = res.status_code
    url = request.url

    headers = get_response_header(headers, duration)
    r = HTTPResponse(status=status_code, body=content, headers=headers)

    check_response(url, page_path, content, status_code)

    return r


@app.route('/info')
@app.route('/info<url_path:re:.+>')
def get_all(info_path=None):
    url_path = request.fullpath
    headers = get_request_headers_()
    h=json.dumps(headers, sort_keys=True, indent=4)
    server_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    print "%s - %s => %s"%(server_time, url_path, h)
    return """
<pre>bottle-info
path:%s
server-time:<b>%s</b>
headers:%s
</pre>"""%(url_path, server_time, h)


def requests_rest_auth(domain, url_path=None, method='GET', data=None, user=None, password=None, timeout=30 ):
    import requests
    debug = False
    if debug:
        """  http://stackoverflow.com/questions/10588644/how-can-i-see-the-entire-request-thats-being-sent-to-paypal-in-my-python-applic  """
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
    method = method.strip().upper()
    auth = (user, password) if user and password else None
    if method in ['GET','DELETE']:  # just to ensure only valid request are sent
        if data and isinstance(data, dict):
            params = [ "%s=%s"%(a,b) for a,b in data.iteritems() ]
            params = '&'.join(params)
            url_path +='?'+params
        data = None
    headers = copy_request_headers(domain)
    url = 'http://%s%s'%(domain,url_path)
    print "domain:%s, url_path:%s, url:%s"%(domain,url_path,url)
    r = requests.request(method, url, headers=headers, data=data, auth=auth,allow_redirects=False, timeout=timeout)
    #print "status_code",r.status_code, "data",r.text
    return r

def copy_request_headers(domain):
    headers = {}
    for k, v in dict(request.headers).iteritems():
        if k in ['Host','Connection','Cache-Control','Accept',
                 'Accept-Encoding','Accept-Language','Cookie',
                 'Referer','User-Agent']:
            headers[k]=v
    # special for ilovevideo.tv
    from urlparse import urlparse
    #domain = urlparse(url).netloc
    headers.update(  {#"X-Proxy-Server": "pypxy",
                      "Host": domain} )
    return headers

def get_response_header(headers, duration):
    new_headers = {}
    exclude_headers = ['p3p','content-type', 'content-encoding']
    for k, v in headers.iteritems():
        print "HEADER",k, "is_hop_by_hop:", is_header_hoppish(k)
        if not is_header_hoppish(k) and k not in exclude_headers:
           print "SET-HEADER",k, "VALUE:", v
           new_headers[k] = v
    new_headers['X-Proxy-Duration'] = '%sms'%duration
    return new_headers

def check_response(url, page_path, content, status_code):
    if status_code!=200:
        return
    import  re
    mobile = True if (url in 'm.ilovevideo.tv' or url in 'm.skiporlike.it') else False
    content_length = len(content)
    if page_path.startswith('/url'):
        check_min_length(content_length, 12)
        return
    check_min_length(content_length, 512)

    if page_path.startswith('/assets') or page_path.startswith('/url'):
        return

    if mobile:
        # check minimum page content length
        check_min_length(content_length, 1024)
    else:
        # check minimum content length
        check_min_length(content_length, 1024*5)

        # detect page type
        page_type ="custom"
        if re.findall('^/$', page_path, re_flags) or re.findall('^/[a-z]+$', page_path, re_flags):
            page_type ="index"
        elif not re.findall('^/cpages', page_path, re_flags):
            #elif re.findall('^/.*?\-\d+\-\d+$', page_path, re_flags):
            page_type ="video"

        # navigation bar must always exist
        if page_type in ["video","index"] and 'class="castaclip-category' not in content:
            error_message(500,'missing_category_navigation'%content_length)

        # video/article page must contain the following data
        if page_type in "video":
            if not('window.firstClip = {"id":' in content and 'class="pull-right">' not in content):
                error_message(500,'missing_incorrect_data')

        # index page must contain the following data
        if page_type in "index":
            if not('class="pull-right">' in content and 'window.firstClip' not in content):
                error_message(500,'missing_incorrect_data')

    return content

def is_header_hoppish(header_name):
    """ function copied from wsgi file """
    _hoppish = {
        'connection':1, 'keep-alive':1, 'proxy-authenticate':1,
        'proxy-authorization':1, 'te':1, 'trailers':1, 'transfer-encoding':1,
        'upgrade':1
    }.__contains__
    """Return true if 'header_name' is an HTTP/1.1 "Hop-by-Hop" header"""
    return _hoppish(header_name.lower())


def error_message(code, message):
    import  bottle
    raise bottle.HTTPError(500, "Something went wrong. %s - %s"%(code,message))

def check_min_length(current_length, min_length):
    if current_length < min_length:
       message = "Something went wrong. content_too_short_%s - %s"%(str(min_length),str(current_length))
       error_message(500, message)

def get_request_headers_():
    h =  {}
    for a,k in request.headers.iteritems():
        h[a]=k
    return h

def urllib2_rest_auth(url, method='GET', data=None, user=None, password=None):
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
    if user and password:
        base64string = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
    urllib2._opener.handlers[1].set_http_debuglevel(100)
    #urllib2.install_opener(urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1)))
    response = urllib2.urlopen(request)
    data = response.read()
    return response.getcode(), response.headers, data


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

if __name__ == "__main__":
    main()

