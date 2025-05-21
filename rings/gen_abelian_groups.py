from sage.all import *
from itertools import product

def gen_abelian_groups(N):
	for subgroup_lengths in product(*[[(p, part) for part in Partitions(e)] for p,e in factor(N)]):
		yield AbelianGroup( sum([[p**l for l in lens] for p, lens in subgroup_lengths], []) ) 

def gen_ladr_input(G):
	out = "\n".join([
	f"assign(domain_size, {len(G)}).",
	f"assign(max_models, -1).",
	"formulas(assumptions).",
	"\t(x*y)*z=x*(y*z). % multiplication is semigroup",
	"\tx*(y+z)=(x*y)+(x*z). % left distributive",
	"\t(y+z)*x=(y*x)+(z*x). % right distributive",
	]) + "\n"
	elems = list(G)
	for i in range(len(elems)):
		for j in range(len(elems)):
			k = elems.index( elems[i] * elems[j] )
			out += f"\t{i}+{j}={k}.\n"
	out += "end_of_list."
	return out

Gs = list( gen_abelian_groups(16) )
print( gen_ladr_input( Gs[-1] ) )
