from __future__ import annotations
from itertools import product
from typing import List, Dict, Tuple
from dataclasses import dataclass

from sympy import factorint
from sympy.utilities.iterables import partitions
from sympy.combinatorics.partitions import IntegerPartition
from sympy.combinatorics.permutations import Permutation
from sympy.combinatorics.named_groups import AbelianGroup as SympyAbelianGroup


@dataclass
class AbelianGroup:
	name: str
	group: SympyAbelianGroup 
	elements: List[Permutation]

	def gen_multiplication_table(self) -> Dict[Tuple[int,int], int]:
		out = dict()
		for i in range(len(self.elements)):
			for j in range(len(self.elements)):
				assert G.elements[i] * G.elements[j] == G.elements[j] * G.elements[i]
				out[(i,j)] = G.elements.index( G.elements[i] * G.elements[j] ) 
				out[(j,i)] = G.elements.index( G.elements[i] * G.elements[j] )
		return out

	def gen_ladr_input(self) -> str:
		ladr_input = "\n".join([
			f"assign(domain_size, {len(self.elements)}).",
			f"assign(max_models, -1).",
			"formulas(assumptions).",
			"\t(x*y)*z=x*(y*z). % multiplication is semigroup",
			"\tx*(y+z)=(x*y)+(x*z). % left distributive",
			"\t(y+z)*x=(y*x)+(z*x). % right distributive",
		]) + "\n"
		multiplication_table = self.gen_multiplication_table()
		for i in range(len(self.elements)):
			for j in range(len(self.elements)):
				ladr_input += f"\t{i}+{j}={multiplication_table[(i,j)]}.\n"
		ladr_input += "end_of_list."
		return ladr_input

def gen_partitions(N) -> List[List[int]]:
	return [IntegerPartition(p).partition for p in partitions(N)]

def gen_abelian_groups(N) -> List[AbelianGroup]:
	for subgroup_lengths in product(* [ [(p, part) for part in gen_partitions(e)] for p,e in factorint(N).items() ] ):
		subgroup_orders = sum( [[p**l for l in lengths] for p, lengths in subgroup_lengths] , [] )
		G = SympyAbelianGroup(*subgroup_orders)
		yield AbelianGroup(
			name = "x".join([f"Z_{order}" for order in subgroup_orders]),
			group = G,
			elements = sorted(G.elements, key = lambda perm: perm.order()) # necessary so identity element is index 0 
		)
