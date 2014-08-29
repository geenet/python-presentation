import bottle
from wsgiproxy.app import WSGIProxyApp
app = bottle.Bottle()
proxy_app = WSGIProxyApp("http://google.com/")
app.mount(proxy_app,"/proxy")
app.run(host='0.0.0.0', port=8080)
