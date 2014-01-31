Installation of Dependencies

sudo apt-get install -y python-dev python-pip apache2-utils libev-dev

sudo pip install -U -r requirements.txt

# Recursive Tests in sub directories
py.test

# WSGI Servers Benchmark 
python wsgi/wsgi-benchmark.py <server-name>

server-name: uwsgi, bjoern, eventlet, fapws, gevent, meinheld, pycgi, pystandard


# Example
python wsgi/wsgi-benchmark.py gevent

# URL structure - check in browser
http://localhost:8000/<bytes>

bytes: 10,100,...

# Run Apache Bench
# ! to avoid too many open files / socket issues - change the default server limits
# https://cs.uwaterloo.ca/~brecht/servers/openfiles.html
# ulimit -n 999999
# sudo su -c 'echo "999999" > /proc/sys/fs/file-max'
# etc ...
 
ab -n1000000 -c1000 -r http://localhost:8000/100
 
