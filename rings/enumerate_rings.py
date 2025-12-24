from __future__ import annotations
from itertools import product
from typing import List, Dict, Tuple
from dataclasses import dataclass
from itertools import product
from math import isqrt

from sympy import factorint
from sympy.utilities.iterables import partitions
from sympy.combinatorics.partitions import IntegerPartition
from sympy.combinatorics.permutations import Permutation
from sympy.combinatorics.named_groups import AbelianGroup as SympyAbelianGroup

LADR_LOCATION="../LADR-2009-11A"

@dataclass
class AbelianGroup:
	name: str
	group: SympyAbelianGroup 
	elements: List[Permutation]
	
	def __repr__(self):
		return self.name

	def gen_multiplication_table(self) -> Dict[Tuple[int,int], int]:
		out = dict()
		for i in range(len(self.elements)):
			for j in range(len(self.elements)):
				assert self.elements[i] * self.elements[j] == self.elements[j] * self.elements[i]
				out[(i,j)] = self.elements.index( self.elements[i] * self.elements[j] ) 
				out[(j,i)] = self.elements.index( self.elements[i] * self.elements[j] )
		return out

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

@dataclass
class Ring:
	name: str
	additive_group: AbelianGroup
	mult_table: Dict[Tuple[int,int], int]

	# Sanity check to make sure generation of models went ok
	def check_axioms(self):
		N = isqrt( len( self.mult_table ) )
		ADD = self.additive_group.gen_multiplication_table()
		MUL = self.mult_table
		for x,y,z in product(range(N), repeat=3):
			assert MUL[ MUL[x,y], z ] == MUL[x, MUL[y,z] ] # associative
			assert MUL[ x, ADD[y, z] ] == ADD[ MUL[x,y], MUL[x,z] ]
			assert MUL[ ADD[y,z], x ] == ADD[ MUL[y,x], MUL[z,x] ]

	@staticmethod
	def gen_models(additive_group: AbelianGroup) -> List[Ring]:
		import subprocess, tempfile, os, re
		from ast import literal_eval
		mace_input = "\n".join([
			f"assign(domain_size, {len(additive_group.elements)}).",
			f"assign(max_models, -1).",
			f"set(verbose)."
			"formulas(assumptions).",
			"\t(x*y)*z=x*(y*z). % multiplication is semigroup",
			"\tx*(y+z)=(x*y)+(x*z). % left distributive",
			"\t(y+z)*x=(y*x)+(z*x). % right distributive",
		]) + "\n"
		addition_table = additive_group.gen_multiplication_table()
		N = len(additive_group.elements)
		for i in range(N):
			for j in range(N):
				mace_input += f"\t{i}+{j}={addition_table[(i,j)]}.\n"
		mace_input += "end_of_list."
		tmp_file = tempfile.mktemp()
		proc = subprocess.Popen(
			f"{LADR_LOCATION}/bin/mace4 | {LADR_LOCATION}/bin/interpformat portable | tee {tmp_file}", 
			stdin=subprocess.PIPE, 
			shell=True
		)
		proc.communicate(mace_input.encode())
		mace_output = literal_eval( open(tmp_file, 'r').read() )
		os.remove(tmp_file)
		mult_tables = [
			(re.match("=\(number,(\d+)\)", model[1][0]).group(1), model[2][1][3])
			for model in mace_output
		]
		return [
			Ring(
				name = f"R_{number}",
				additive_group = additive_group,
				mult_table = {(i, j): table[i][j] for i in range(N) for j in range(N) }
			)
			for number, table in mult_tables
		]


