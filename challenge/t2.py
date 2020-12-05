import traceback
log = open("challenge/log.txt", "w")
try:
	import math
	for i in range(int(input())):
	    print(math.factorial(int(input())))
except Exception as e:
	traceback.print_exc(file=log)
log.close()