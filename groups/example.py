from enumerate import *

small_groups = dict()
for order in range(2, 32):
	small_groups[order] = [ g.get_group_description() for g in toss_out_nonisomorphic( enumerate_group(order) ) ]

for order, groups in small_groups.items():
	print(order, groups)
