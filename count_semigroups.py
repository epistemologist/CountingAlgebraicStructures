from typing import *
from tqdm import tqdm
from itertools import count, product, permutations
from collections import deque
from copy import deepcopy


# Represent magma as dict of tuples
Magma = Dict[Tuple[int,int], int]

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

# Some utilities
def dict_to_frozenset(d: dict) -> frozenset:
    return frozenset(
        (k,v) for k,v in d.items()
    )

def frozenset_to_dict(s: frozenset) -> dict:
    return dict(s)

# Generate all equivalent magmas up to permutation of entries
def gen_equivalent_magmas(magma: Magma, n: int) -> List[Magma]:
    return [
        { (p[x], p[y]): p[x_op_y]
            for (x,y), x_op_y in magma.items()
        }
        for p in permutations(range(n))
    ]


def are_isomorphic(S1: Magma, S2: Magma, n: int) -> bool:
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
    semigroups = [dict_to_frozenset(i.model) for i in gen_all_semigroups(order) ]
    candidates = []
    equivalent_semigroups = set()
    print("[+] Filtering out some isomorphic models")
    for semigroup in tqdm( semigroups ):
        if semigroup not in equivalent_semigroups:
            candidates.append(semigroup)
            equivalent_semigroups|= {
                dict_to_frozenset(m) for m in gen_equivalent_magmas(
                    frozenset_to_dict(semigroup), order
                )}
    print("[+] Final isomorphism check")
    out = [candidates[0]]
    for i in tqdm(range(1, len(candidates))):
        if not any([are_isomorphic(
            frozenset_to_dict(j),
            frozenset_to_dict(candidates[i]),
            order
        ) for j in out]):
            out.append(candidates[i])
    return [PartialModel(
        curr_model=frozenset_to_dict(i),
        length=order,
        unassigned_pairs=None
        ) for i in out
    ]

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
    print(f"Counted {len(semigroups)} of order {n} in {str(timedelta(seconds=(int( end-start ) if end-start > 1 else end-start)))}")
    return len(semigroups)
