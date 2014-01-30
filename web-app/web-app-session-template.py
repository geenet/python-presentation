# -*- coding: utf-8 -*-
from bottle import run, request, Bottle
import jinja2
import beaker.middleware

session_opts = {
    'session.type': 'file',
   # 'session.cookie_expires': 300,
    'session.data_dir': '/tmp/sessions/beaker/',
    'session.auto': True
}

app=Bottle()
newapp = beaker.middleware.SessionMiddleware(app, session_opts)

def main():
    host, port = '0.0.0.0', 9040
    run(newapp, host=host, port=port, debug=1)

@app.get("/")
def index():
    template = load_template("./template.html")
    data = { "navigation" :  ["one","two", "three"],
             "myvariable" : " World"}
    html = template.render( data )
    return html

def load_template(template_file_name):
    searchpath ="./"
    loader = jinja2.FileSystemLoader( searchpath=searchpath)
    env = jinja2.Environment( loader=loader )
    template = env.get_template( template_file_name )
    return template


@app.get("/session")
def session_write():
    session = request.environ.get('beaker.session')
    if request.GET: # write session /session?a=b
        for k, v in request.GET.iteritems():
            session[k]=v
        return "done"
    # read sesssion
    mydict = dict()
    for k, v in session.iteritems():
        mydict[k]=v
    return mydict

if __name__ == "__main__":
    main()
