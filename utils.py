# -*- coding: utf-8 -*-
"""
"""
import os, re,sys
re_flags=re.IGNORECASE|re.MULTILINE|re.DOTALL|re.UNICODE
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__) , '../utils/') ))
import json

def format_json(myobject):
    #response.headers['Content-Type'] = 'application/json; charset=UTF-8'
    #global response
    #response.content_type = "application/json; charset=UTF-8"
    return json.dumps(myobject, sort_keys=True, indent=4, separators=(',', ': '))

def rest(url, method, data, user=None, password=None):
    import httplib2
    h = httplib2.Http()
    if user and password:
        h.add_credentials(user, password)
    data = None if method=='GET' else data
    result = None
    try:
        response, content = h.request(url, method, data)
        result = content if content else format_json(response)
    except:
        import traceback
        result = str(traceback.format_exc())
    return result

def urllib2_rest_auth(url, method='GET', data=None, user=None, password=None, access_token=None, as_json=False):
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
    if access_token:
        request.add_header("access_token", access_token)
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



import collections
class TransformedDict(collections.MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys
    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]
    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value
    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]
    def __iter__(self):
        return iter(self.store)
    def __len__(self):
        return len(self.store)
    def __keytransform__(self, key):
        return key
def transformed_dict_test():
    class MyTransformedDict(TransformedDict):
        def __keytransform__(self, key):
            return key.lower()
    s = MyTransformedDict([('Test', 'test')])
    assert s.get('TEST') is s['test']   # free get
    assert 'TeSt' in s                  # free __contains__
                                        # free setdefault, __eq__, and so on
    import pickle
    assert pickle.loads(pickle.dumps(s)) == s
    # works too since we just use a normal dict
def dict2obj(d):
    if isinstance(d, list):
        d = [dict2obj(x) for x in d]
    if not isinstance(d, dict):
        return d
    class DictClass(dict):
        def __init__(self, *args, **kwargs):
            dict.__init__( self, *args, **kwargs )
            self.__dict__ = self
        def __getnewargs__(self):  # for cPickle.dump( d, file, protocol=-1)
            return tuple(self)
            pass
        def to_dict(self):
            return dict(self)
    o = DictClass()
    for k in d:
        o.__dict__[k] = dict2obj(d[k])
        o[k] = dict2obj(d[k])
    return o
def dict2obj_test():
    auth = {"auth":{"username" : "big@john.com","password" : "123"}}
    jdata = json.dumps(auth)
    doo = json.loads(jdata)
    print doo
    print jdata
    o = dict2obj(doo)
    print "yes:",o.auth
    print o.auth.username
def dict2obj_to_dict_(d):
    return dict(d)

class dbrec(object):
    #http://code.activestate.com/recipes/577186-accessing-cursors-by-field-name/
    def __init__(self, row, cursor=None, strip_underscore=False):
        
        if cursor:
            if strip_underscore:
                for (attr, val) in zip((d[0][d[0].find('_')+1:] for d in cursor.description), row) :
                    setattr(self, attr, val)
            else:
                for (attr, val) in zip((d[0] for d in cursor.description), row) :
                    setattr(self, attr, val)
        else:
            for (attr, val) in row.iteritems():
                self.__dict__[attr] = val
                setattr(self, attr, val)
                #self[attr]=val
    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return str(self.__dict__)
    def __getitem__(self, key, default=None):
        if key in self.__dict__:
            return self.__dict__[key]
        return default
    def get(self, key, default=None):
        return self.__getitem__(key, default)
    def iteritem(self):
        for a, b in self.__dict__.iteritems():
            yield a,b
    def iteritems(self):
        return iter(self.__dict__.iteritems())
    def to_dict(self):
        return self.__dict__
    """
    def dict(self):
        return self.__dict__
   """
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)
    def __ne__(self, other):
        return not self.__eq__(other)
    
class Bunch(dict):
    #def __init__(self, **kw):
    def __init__(self, in_dict):
        dict.__init__(self, in_dict)
        self.__dict__ = self
    def __getstate__(self):
        return self
    def __setstate__(self, state):
        self.update(state)
        self.__dict__ = self
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)
    def __ne__(self, other):
        return not self.__eq__(other)
    
def get_re_match(regex, url):
    matches = re.findall(regex, url, re_flags)
    if matches:
        matches=matches[0]
        return matches
    return None
import functools
def memoize_functools(obj):
    cache = obj.cache = {}
    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer

rd = None #redis
def memoize_redis(obj):
    obj.cache = {}
    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        val = rd.get(key)
        if not val:
            val = obj(*args, **kwargs)
            rd.set(key, val )
        return val
    return memoizer

def memoize_memory(f, cache={}):
    def g(*args, **kwargs):
        key = ( f, tuple(args), frozenset(kwargs.items()) )
        if not rd.get(key):
            val = f(*args, **kwargs)
            rd.set(str(key), val )
        return val
    return g

def memoize_original(f, cache={}):
    def g(*args, **kwargs):
        key = ( f, tuple(args), frozenset(kwargs.items()) )
        if key not in cache:
            cache[key] = f(*args, **kwargs)
        return cache[key]
    return g

def first_tuple_element(tpl):
    while(True):
        if not isinstance(tpl, (tuple,list)):
            return tpl
        tpl = tpl[0]

import os, errno
def mkdirs_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
def mkdirs_p_filepath(filepath):
    return mkdirs_p(os.path.dirname(filepath))

def yield_file(filepath, chunksize=8192):
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if chunk:
                yield chunk
            else:
                break

def read_textfile(filepath):
    with open(filepath, "r") as f:
        return f.read()
        
def main():
    pass

if __name__ == "__main__":
    main()