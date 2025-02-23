from collections import deque, Counter
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from hashlib import sha1
from itertools import cycle, count, islice,  product, permutations
from math import isqrt
from multiprocessing import cpu_count
from random import shuffle
from typing import *
from tqdm import tqdm

# Represent magma as dict of tuples
Magma = Dict[Tuple[int,int], int]

# GAP and other software uses tables to represent semigroups and other algebraic structures
# So we use this method to convert between their representations and ours
def table_to_magma(table: List[List[int]]) -> Magma:
    # See https://docs.gap-system.org/doc/ref/chap35.html#X85CD1E7678295CA6
    N = len(table)
    magma = dict()
    for i in range(N):
        for j in range(N):
            magma[(i,j)] = table[i][j]
    return magma

SHA1 = lambda s: sha1(s.encode()).hexdigest()

def propagate(model, length):
    curr_len = len(model)
    while True:
        to_add = []
        for x in range(length):
            for (y,z) in model:
                y_op_z = model[(y,z)]
                if (x,y) in model:
                    x_op_y = model[(x,y)]
                    # x op (y op z) = (x op y) op z
                    if (x_op_y,z) in model and (x, y_op_z) not in model:
                        to_add.append( ( (x, y_op_z), model[(x_op_y, z)] ) )
                    if (x,y_op_z) in model and (x_op_y, z) not in model:
                        to_add.append( ( (x_op_y, z), model[(x, y_op_z)] ) )
        if len(to_add) == 0:
            break
        else:
            for k,v in to_add:
                model[k] = v
    return model


class PartialModel:
    def __init__(self,
        curr_model: Magma,
        length: int,
        unassigned_pairs: Optional[List] = None
    ):
        self.model = curr_model
        self.N = length
        self.unassigned_pairs = unassigned_pairs if unassigned_pairs is not None else [(i,j) for i in range(self.N) for j in range(self.N) if (i,j) not in curr_model ]

    def to_table(self):
        # Return array s.t. arr[i,j] = i op j
        return [
            [
            self.model[ (i,j) ] if (i,j) in self.model else None
            for j in range(self.N)
            ]
            for i in range(self.N)
        ]

    def __repr__(self):
        return repr(self.to_table())

    def check_model(self) -> bool:
        for x,y,z in product(range(self.N), repeat=3):
            # (x.y).z = x.(y.z)
            if (x,y) not in self.model or (y,z) not in self.model:
                continue
            x_op_y = self.model[(x,y)]
            y_op_z = self.model[(y,z)]
            if (x_op_y, z) not in self.model or (x, y_op_z) not in self.model:
                continue
            if self.model[(x_op_y, z)] != self.model[(x, y_op_z)]:
                return False
        return True

    def gen_next_models(self):
        if len(self.unassigned_pairs) == 0:
            return []
        x,y = self.unassigned_pairs[0]
        new_unassigned_pairs = self.unassigned_pairs[1:]
        # Assign new value to x op y
        new_models = []
        for x_op_y in range(self.N):
            # Propagate to enforce associativity
            curr_model = propagate( deepcopy(self.model) | {(x,y): x_op_y} , self.N )
            new_models.append(PartialModel(
                curr_model=curr_model,
                length=self.N,
                unassigned_pairs=[(i,j) for i in range(self.N) for j in range(self.N) if (i,j) not in curr_model]
            ))
        return [ model for model in new_models if model.check_model() ]

# Class to represent a complete magma
# i.e. a complete dict {(x,y): z} of size n^2 for some order n
class CompleteMagma(PartialModel): 
                    # Only really subclassing for the repr method
    def __init__(self, magma: Magma):
        order = isqrt(len(magma))
        assert len(magma) == order**2 
        super().__init__(
            curr_model = magma,
            length = order,
            unassigned_pairs = []
            )

    def __hash__(self) -> int:
       # Note that magma can be represented as a list of integers of length order^2 each in [0..order-1]
        out = 0
        for i, (_, val) in enumerate( sorted(self.model.items()) ):
            out += val * pow(self.N, i)
        return out

    def __iter__(self):
        return iter(self.model)

    def __getitem__(self, key):
        return self.model[key]

    def __setitem__(self, key, item):
        self.model[key] = item
    
    def __len__(self):
        return len(self.model)

# Generate all equivalent magmas up to permutation of entries
def gen_equivalent_magmas(magma: Magma, n: int) -> List[Magma]:
    return [
        CompleteMagma( { (p[x], p[y]): p[x_op_y]
            for (x,y), x_op_y in magma.items()
        })
        for p in permutations(range(n))
    ]

def gen_isomorphism_invariant(S: CompleteMagma) -> Tuple[int]:
    # See https://iopscience.iop.org/article/10.1088/1757-899X/862/5/052047/pdf
    # Number of each element in the table
    return tuple(sorted( Counter( S.model.values() ).values() ))

def are_isomorphic(S1: CompleteMagma, S2: CompleteMagma, n: int) -> bool:
    if gen_isomorphism_invariant(S1) != gen_isomorphism_invariant(S2):
        return False
    def is_isomorphism(S1, S2, perm):
        return all(
            perm[ S1[(a,b)] ]  == S2[(perm[a], perm[b])]
            for a in range(n)
            for b in range(n)
        )
    return any(is_isomorphism(S1, S2, perm) for perm in permutations(range(n)))

# Generate all semigroups of certain order (not up to isomorphism)
def gen_all_semigroups(order: int):
    # WLOG, we can let 0 op 0 = 0 up to isomorphism
    model = PartialModel(curr_model = {(0,0): 0}, length = order)
    # Do BFS
    queue = deque([model])
    out = []
    for _ in tqdm(count(1)):
        if len(queue) == 0: break
        curr_model = queue.popleft()
        if len(curr_model.unassigned_pairs) == 0:
            out.append(curr_model)
        for new_model in curr_model.gen_next_models():
            queue.append(new_model)
    return out

def gen_isomorphic_semigroups(order: int):
    print("[+] Generating possible Cayley tables...")
    semigroups = [CompleteMagma(i.model) for i in gen_all_semigroups(order) ]
    candidates = []
    equivalent_semigroups = set() # Store as hashes to reduce memory
    print("[+] Filtering out some isomorphic models")
    for semigroup in tqdm( semigroups ):
        if hash(semigroup) not in equivalent_semigroups:
            candidates.append(semigroup)
            equivalent_semigroups |= {
                    hash(semigroup) 
                    for semigroup in gen_equivalent_magmas(
                        semigroup.model, order
                    )}
    print("[+] Final isomorphism check")
    out = [candidates[0]]
    for i in tqdm(range(1, len(candidates))):
        if not any([are_isomorphic(
            j,
            candidates[i],
            order
        ) for j in out]):
            out.append(candidates[i])
    return [CompleteMagma(i) for i in out]

def number_of_semigroups(n: int, suppress_output: bool) -> int:
    import os, sys
    from contextlib import nullcontext, redirect_stdout, redirect_stderr
    from datetime import timedelta
    from time import time
    start = time()
    with open(os.devnull, 'w') as dev_null:
        with redirect_stdout(dev_null) if suppress_output else nullcontext(sys.stdout):
            with redirect_stderr(dev_null) if suppress_output else nullcontext(sys.stderr):
                semigroups = gen_isomorphic_semigroups(n)
    end = time()
    print(f"Counted {len(semigroups)} semigroups of order {n} in {str(timedelta(seconds=(int( end-start ) if end-start > 1 else end-start)))}")
    return len(semigroups)

for i in range(1, 7):
    number_of_semigroups(i, suppress_output=i<5)
