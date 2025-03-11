from __future__ import annotations

from functools import reduce, cached_property
from operator import mul
from typing import List, Optional, Set, Callable
from collections import defaultdict, Counter, namedtuple
from math import factorial, prod
from itertools import permutations, product
from subprocess import Popen, check_output, PIPE
from time import sleep
from tqdm import tqdm
import re

VERBOSE = True
MAX_ITER = 1_000_000_000
#MAX_ITER = -1

GAP_LOCATION = "/usr/bin/gap"
GAP_PROC = Popen(
	[GAP_LOCATION, "-b", "-q"],
	stdin=PIPE,
	stdout=PIPE,
	stderr=PIPE,
	text=True,
	bufsize=1,
)  # To avoid slow startup
if VERBOSE:
	print(f"[+] Starting GAP on pid {GAP_PROC.pid}")


# WARNING: This is not production-ready - does not have error-checking, etc.
# I am only using this for cross-compatibility with pypy
# if you want something like this - use Sage's interface with gap
def run_gap_code(gap_code_lines: List[str]):
	sentinel_str = "*" * 50
	gap_code = gap_code_lines + [f'Print("{sentinel_str}", "\\n");']
	for line in gap_code:
		if VERBOSE:
			print("[+] sending GAP code: ", line)
		GAP_PROC.stdin.write(line + "\n")
		GAP_PROC.stdin.flush()
	output = []
	while True:
		line = GAP_PROC.stdout.readline()
		if line.strip() == sentinel_str:
			break
		else:
			output.append(line.strip())
		sleep(0.2)
	return output


class GroupElement:
	def __init__(self, idx: int, name: Optional[str], group: Group):
		self.idx = idx
		self.name = name if name else f"x{idx}"
		self.group = group

	def __repr__(self):
		return repr(self.name)

	def __mul__(self, other) -> GroupElement:
		# Define x_i * x_j = x_( cayley_table[i][j] )
		new_idx = self.group.cayley_table[self.idx][other.idx]
		return self.group.elements[new_idx]

	def __pow__(self, exponent: int) -> GroupElement:
		if exponent == 0:
			return self.group.elements[0]
		elif exponent > 0:
			return (
				reduce(mul, [self for _ in range(exponent)])
				if exponent >= 1
				else self.group.elements[0]
			)
		else:  # negative exponent -> raise inverse to negative power
			return pow(self.group.inv[self], -exponent)

	@cached_property
	def cyclic_subgroup(self) -> List[GroupElement]:
		out = [self]
		while out[-1].idx != 0:
			out.append(out[-1] * self)
		return out

	@cached_property
	def order(self) -> int:
		return len(self.cyclic_subgroup)


def check_cayley_table(table: List[List[int]]) -> bool:
	# keep commented for safer code
	# return True
	table_t = list(map(list, zip(*table)))
	n = len(table)
	assert table_t[0] == table[0] == list(range(n)), "invalid first row/col!"
	for i in range(1, n):
		assert sorted(table[i]) == list(range(n)), f"invalid row {i}"
		assert sorted(table_t[i]) == list(range(n)), f"invalid col {i}"
	return True


def construct_group(
	G: Set, group_op: Callable, group_name: Optional[str] = None
) -> Group:
	# First, find identity element
	G = list(G)
	for i in range(len(G)):
		if all(
			[
				group_op(G[i], G[j]) == group_op(G[j], G[i]) == G[j]
				for j in range(len(G))
			]
		):
			break
	else:
		raise ValueError("no identity element!")
	G = [G[i]] + [G[j] for j in range(len(G)) if j != i]
	cayley_table = [[None for _ in range(len(G))] for __ in range(len(G))]
	for i, xi in enumerate(G):
		for j, xj in enumerate(G):
			try:
				cayley_table[i][j] = G.index(group_op(xi, xj))
			except:
				raise ValueError("group op is not closed!")
	return Group(
		cayley_table=cayley_table,
		element_names=[repr(i) for i in G],
		group_name=group_name,
	)


GroupInfo = namedtuple("GroupInfo", ["id", "desc"])


class Group:
	def __init__(
		self,
		cayley_table: List[List[int]],
		group_name: Optional[str] = None,
		element_names: Optional[List[str]] = None,
	):
		check_cayley_table(cayley_table)
		self.group_name = "G" if group_name is None else group_name
		self.cayley_table = cayley_table
		self.order = len(cayley_table)
		if element_names:
			assert len(element_names) == self.order, "invalid number of elements!"
		# Assuming elements[0] is identity element
		self.elements = [
			GroupElement(
				idx=i,
				name=(
					element_names[i] if element_names else ("e" if i == 0 else f"x{i}")
				),
				group=self,
			)
			for i in range(self.order)
		]
		self.inv = {
			self.elements[i]: self.elements[self.cayley_table[i].index(0)]
			for i in range(len(self.elements))
		}

	def __repr__(self):
		return f"Group {self.group_name} of {self.order} elements: {self.elements}"

	def __getitem__(self, idx):
		return [e for e in self.elements if e.idx == idx][0]

	def subgroup_from_elements(self, elements: List[GroupElement]) -> Group:
		# Define x_i * x_j = x_( cayley_table[i][j] )
		try:
			cayley_table = [
				[
					elements.index((elements[i] * elements[j]))
					for j in range(len(elements))
				]
				for i in range(len(elements))
			]
			return Group(
				cayley_table=cayley_table, element_names=[e.name for e in elements]
			)
		except ValueError:
			raise Exception("given elements do not form a subgroup!")

	@cached_property
	def center(self) -> List[GroupElement]:
		return [
			x for x in self.elements if all([x * y == y * x for y in self.elements])
		]

	@staticmethod
	def group_different(G: Group, H: Group) -> bool:
		# Returns True if G and H are non-isomorphic
		# NOTE: This will **not** return True if G and H are isomorphic
		# This is to just filter out groups that are non-isomorphic
		if G.order != H.order:
			return True
		if Counter([x.order for x in G]) != Counter([x.order for x in H]):
			return True
		if len(G.center) != len(H.center):
			return True
		return False

	@staticmethod
	def check_isomorphism(G: Group, H: Group, ϕ: Callable) -> bool:
		# Note here, we assume that ϕ is well-defined and sends elements from G to H
		# This function returns whether the function ϕ is a group isomorphism
		if G.order != H.order:
			return False
		# ϕ(x_i *_G x_j) = ϕ(x_i) *_H ϕ(x_j)
		for xi in G.elements:
			for xj in G.elements:
				if ϕ(xi * xj) != ϕ(xi) * ϕ(xj):
					return False
		return True

	@staticmethod
	def isomorphism_brute(G: Group, H: Group) -> bool:
		# Checks whether or not G and H are isomorphic via brute force
		# NOTE: This takes a long time - only works for small groups
		print(f"[+] Checking isomorphism between {G.group_name} and {H.group_name}")
		def gen_isomorphism_invariants(X: Group):
			# For each element in group, calculate an isomorphism invariant
			# x -> (order of x, x in center)
			C_X = X.center
			isom_invariants = [(x, (x.order, x in C_X)) for x in X]
			invariant_dict = defaultdict(list)
			for elem, invariant in isom_invariants:
				invariant_dict[invariant].append(elem)
			return invariant_dict

		G_invariants = gen_isomorphism_invariants(G)
		H_invariants = gen_isomorphism_invariants(H)
		if set(G_invariants) != set(H_invariants):
			return False
		invariants = G_invariants

		# Construct sets fixed by isomorphism
		# i.e. subsets G_i ⊆ G and H_i ⊆ H such that an isomorphism ϕ fixes each G_i and H_i
		# we have ϕ(G_i) = H_i for all i
		fixed_sets = [(G_invariants[i], H_invariants[i]) for i in invariants]
		domain = sum([i[0] for i in fixed_sets], [])
		codomain_iterator = product(*[permutations(i[1]) for i in fixed_sets])
		iterator_len = prod([factorial(len(i[0])) for i in fixed_sets])
		if iterator_len > MAX_ITER:
			raise ValueError(f"too many iterations!: {iterator_len} > {MAX_ITER}")
		for codomain_candidate in ( tqdm(codomain_iterator, total=iterator_len) if VERBOSE else codomain_iterator ):
			codomain = sum(map(list, codomain_candidate), [])
			mapping = dict(zip(domain, codomain))
			if Group.check_isomorphism(G, H, lambda g: mapping[g]):
				if VERBOSE:
					print(mapping)
				return True
		return False

	def _to_gap(self) -> str:
		return str([[i + 1 for i in row] for row in self.cayley_table])

	def get_group_description(self) -> GroupInfo:
		gap_code = [
			rf"G := GroupByMultiplicationTable( {self._to_gap() } );",
			r'Print("id:", IdGroup(G), "\n");'
			r'Print("desc:", StructureDescription(G), "\n");',
		]
		output = "\n".join( run_gap_code(gap_code_lines=gap_code) )
		return GroupInfo( 
			id = re.search("id:(.*)", output).group(1),
			desc = re.search("desc:(.*)", output).group(1)		
		)

	@staticmethod
	def isomorphism_gap(G: Group, H: Group) -> bool:
		# Check whether or not G and H are isomorphic via GAP
		# NOTE: Requires GAP to be installed
		gap_code = [
			f"G1 := GroupByMultiplicationTable( {G._to_gap() }  );",
			f"G2 := GroupByMultiplicationTable( {H._to_gap()} ); ",
			"IsomorphismGroups(G1, G2);",
		]
		gap_output = run_gap_code(gap_code_lines=gap_code)
		return gap_output[-1] != b"fail"

	def is_isomorphic(self, other: Group, method="brute") -> bool:
		if Group.group_different(self, other):
			return False
		try:
			return Group.isomorphism_brute(self, other)
		except Exception as e:
			if VERBOSE:
				print(f"[+] Isomorphism test failed!: {e}")
			return Group.isomorphism_gap(self, other)
