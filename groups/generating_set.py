from __future__ import annotations
from group import Group, GroupElement
from typing import List, Dict, Set, Optional
from collections import deque


class SearchNode:
    def __init__(
        self,
        products: Dict[
            GroupElement, List[int]
        ],  # Group element, list of idxs representing product
        elements_left: List[GroupElement],
        generators: Optional[List[GroupElement]],
    ):
        self.products = products
        self.elements_left = elements_left
        self.generators = generators

    def __repr__(self):
        return f"SearchNode(products={self.products}, elements_left={self.elements_left}, generators={self.generators})"

    @staticmethod
    def gen_init_node(G: Group) -> SearchNode:
        return SearchNode(
            products={G[0]: []},
            elements_left=[G[i] for i in range(1, len(G))],
            generators=[],
        )

    def gen_neighbors(self) -> List[SearchNode]:
        out = []
        for g in self.elements_left:
            # Pick off g
            new_products = self.products.copy()
            # Generate new products
            for h, product in self.products.items():
                if (g * h) not in new_products:
                    new_products[g * h] = product + [g.idx]
            out.append(
                SearchNode(
                    products=new_products,
                    elements_left=[
                        i for i in self.elements_left if i not in new_products
                    ],
                    generators=self.generators + [g],
                )
            )
        return out


def sanity_test():
    Q8 = Group(
        [
            [0, 1, 2, 3, 4, 5, 6, 7],
            [1, 2, 3, 0, 7, 4, 5, 6],
            [2, 3, 0, 1, 6, 7, 4, 5],
            [3, 0, 1, 2, 5, 6, 7, 4],
            [4, 5, 6, 7, 2, 3, 0, 1],
            [5, 6, 7, 4, 1, 2, 3, 0],
            [6, 7, 4, 5, 0, 1, 2, 3],
            [7, 4, 5, 6, 3, 0, 1, 2],
        ]
    )
    queue = deque([SearchNode.gen_init_node(Q8)])
    while queue:
        tmp = queue.popleft()
        print(tmp)
        for neighbor in tmp.gen_neighbors():
            queue.append(neighbor)


from tqdm import tqdm
from itertools import count


def find_generating_set(G: Group):
    # Do BFS
    queue = deque([SearchNode.gen_init_node(G)])
    for _ in tqdm(count(1)):
        if len(queue) == 0:
            break
        curr_node = queue.popleft()
        if curr_node.elements_left == []:
            break
        for neighbor in curr_node.gen_neighbors():
            queue.append(neighbor)
    return curr_node.generators


table = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12, 15, 14],
    [2, 3, 0, 1, 6, 7, 4, 5, 10, 11, 8, 9, 14, 15, 12, 13],
    [3, 2, 1, 0, 7, 6, 5, 4, 11, 10, 9, 8, 15, 14, 13, 12],
    [4, 5, 6, 7, 0, 1, 2, 3, 12, 13, 14, 15, 8, 9, 10, 11],
    [5, 4, 7, 6, 1, 0, 3, 2, 13, 12, 15, 14, 9, 8, 11, 10],
    [6, 7, 4, 5, 2, 3, 0, 1, 14, 15, 12, 13, 10, 11, 8, 9],
    [7, 6, 5, 4, 3, 2, 1, 0, 15, 14, 13, 12, 11, 10, 9, 8],
    [8, 9, 10, 11, 12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7],
    [9, 8, 11, 10, 13, 12, 15, 14, 1, 0, 3, 2, 5, 4, 7, 6],
    [10, 11, 8, 9, 14, 15, 12, 13, 2, 3, 0, 1, 6, 7, 4, 5],
    [11, 10, 9, 8, 15, 14, 13, 12, 3, 2, 1, 0, 7, 6, 5, 4],
    [12, 13, 14, 15, 8, 9, 10, 11, 4, 5, 6, 7, 0, 1, 2, 3],
    [13, 12, 15, 14, 9, 8, 11, 10, 5, 4, 7, 6, 1, 0, 3, 2],
    [14, 15, 12, 13, 10, 11, 8, 9, 6, 7, 4, 5, 2, 3, 0, 1],
    [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]

G = Group(table)

import cProfile
cProfile.run("find_generating_set(G)")