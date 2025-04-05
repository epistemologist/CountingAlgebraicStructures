from ast import literal_eval
from pathlib import Path
from typing import List
import subprocess, sys, os, re

from group import Group
from isomorphism import Isomorphism

LADR_LOCATION = "../LADR-2009-11A"  # Main directory of LADR

def toss_out_nonisomorphic(groups: List[Group], method: str) -> List[Group]:
    if len(groups) == 1: return groups
    isomorphism_classes = [ [groups[0]] ]
    for G in groups[1:]:
        for i in range(len(isomorphism_classes)):
            if Isomorphism.are_isomorphic(G, isomorphism_classes[i][0], method=method):
                isomorphism_classes[i].append(G)
                break
        else:
            isomorphism_classes.append([G])
    return [i[0] for i in isomorphism_classes]

def enumerate_group(order: int, method="ladr") -> List[Group]:
    if method == "brute":
        raise NotImplementedError()
    elif method == "ladr":
        return enumerate_group_ladr(order) 

def enumerate_group_ladr(order: int) -> List[Group]:
    tmp_filename = str(Path("./models.tmp").absolute())
    proc = subprocess.Popen(
        [str(Path("./gen_tables.sh").absolute()), str(order), tmp_filename],
        stdout=sys.stdout,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )
    proc.wait()
    models = open(tmp_filename, "r").read()
    models = literal_eval(models)
    os.remove(tmp_filename)
    group_data = [
        (re.match("=\(number,(\d+)\)", model[1][0]).group(1), model[2][0][3])
        for model in models
    ]
    return [
        Group(cayley_table=cayley_table, group_name=f"G_{number}")
        for number, cayley_table in group_data
    ]
