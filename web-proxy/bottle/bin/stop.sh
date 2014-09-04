ps -ef|grep "[i]lv-proxy.py -p $1"|awk '{print $2}'|xargs kill -KILL
