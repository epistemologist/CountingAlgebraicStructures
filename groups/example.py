from enumerate import *
from time import time

small_groups = dict()

for order in range(2, 16):
	start = time()
	Gs = [ 
		g.group_description 
		for g in toss_out_nonisomorphic( 
			enumerate_group(order),
			method = "brute" if order < 16 else "gap"
		)
	]
	small_groups[order] = (Gs, time()-start)

for order, (groups, time_elapsed) in small_groups.items():
	print(f"Groups of order {order}: {groups}, in time {time_elapsed} s")
