import traceback
log = open("cogs/p_util/plog.txt", "w")
try:
	import time
	i = 0
	while i<10:
	    print(i)
	    time.sleep(0.5)
	    i+=1
except Exception as e:
	traceback.print_exc(file=log)
log.close()