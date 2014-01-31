import os,multiprocessing
from time import sleep

result_list = multiprocessing.Manager().list()

def process_square(num):
    pid = os.getpid()
    print('PPID:%s - PID:%s - NUM:%s - begin'%(os.getppid(), pid, str(num)))

    square = num * num
    sleep(2)
   
    print('PPID:%s - PID:%s - NUM:%s - SQUARE = %s'%(os.getppid(), pid, str(num), str(square) ) )
    result_list.append( {"PID %s"%pid: square} )

pool = multiprocessing.Pool(4) # 4 workers
for i in xrange(10): # 10 jobs
    pool.apply_async(process_square, (i,))
pool.close()
pool.join()
print(result_list)

# check running processes
# ps -o pid,ppid,cmd ax | grep -i "[m]ulti-processing.py"

