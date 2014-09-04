DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
cd ..
echo $1
python ilv-proxy.py -p $1 ":-)" > ./logs/access-$1.log 2>&1&
