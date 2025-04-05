from group import Group, run_gap_code, VERBOSE
from collections import Counter, defaultdict, deque
from typing import Callable
from itertools import permutations, product
from math import prod, factorial
from tqdm import tqdm

MAX_ITER = 1_000_000_000

class Isomorphism:
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
	def are_isomorphic(G: Group, H: Group, method="brute") -> bool:
		if Isomorphism.group_different(G, H):
			return False
		if method == "brute":
			return Isomorphism.isomorphism_brute(G, H)
		elif method == "gap":
			return Isomorphism.isomorphism_gap(G, H)
		elif method == "generators":
			raise NotImplementedError()
		else:
			raise NotImplementedError(f"method {method} not implemented!")
  
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
			if Isomorphism.check_isomorphism(G, H, lambda g: mapping[g]):
				if VERBOSE:
					print(mapping)
				return True
		return False

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

