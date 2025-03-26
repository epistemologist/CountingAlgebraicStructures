from __future__ import annotations

from functools import reduce, cached_property
from operator import mul
from typing import List, Optional, Set, Callable
from collections import defaultdict, Counter, namedtuple
from math import factorial, prod
from subprocess import Popen, PIPE
from time import sleep
from itertools import permutations, product
from tqdm import tqdm
import re

VERBOSE = True
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

	def __eq__(self, other):
		# Groups are equal iff their Cayley tables are equal
		return self.cayley_table == other.cayley_table

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


	def _to_gap(self) -> str:
		return str([[i + 1 for i in row] for row in self.cayley_table])

	@cached_property
	def group_description(self) -> GroupInfo:
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
