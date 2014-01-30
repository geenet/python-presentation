
import multiprocessing
newlist = multiprocessing.Manager().list()
def addto(val):
    newlist.append(val)

pool = multiprocessing.Pool()
for i in xrange(10):
    pool.apply_async(addto, (i,))
pool.close()
pool.join()
print(newlist)

# save code to multi-processing.py
# python multi-processing.py
