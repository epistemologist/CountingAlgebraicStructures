# Counting Algebraic Structures
Various notes/programs on counting different types of algebraic strucutres

## Definitions

For a set $S$ and a binary operation $\cdot: S \times S \to S $, we have the following inclusions of classes of algebraic structures:
$$\begin{gather*}
\text{magma} & & &\\
\cup & & & \\
\text{semigroup} &\supset &\text{commutative semigroup} \\
\cup & & & \\
\text{monoid} &\supset &\text{commutative monoid}\\
\cup & & & \\
\text{group} &\supset &\text{abelian/commutative group}
\end{gather*}$$

 - a **magma** is a set $S$ with a *closed* binary operation (i.e. $\forall a,b \in S \; . \; a \cdot b \in S $)
 - a **semigroup** is a magma with an *associative* operation (i.e. $\forall a,b,c \in S  \; . \;  (a \cdot b ) \cdot c = a \cdot (b \cdot c)  $ )
 - a **monoid** is a semigroup with an *identity* element (i.e. $\exists e \in S \;  \forall a \in S \; . \; (e \cdot a = a \cdot e = a )$)
 - a **group** is a monoid with *inverses* (i.e. $\forall  a \in S \; \exists a^{-1} \in S \; . \; (a \cdot a^{-1} = a^{-1} \cdot a = e )  $)


Given a set $R$ with two binary operations $+: R \times R \to R $ and $\cdot : R \times R \to R $, $R$ is a **ring** if:
 - $(R, +)$ is an abelian group
 - $(R, \cdot)$ is a semigroup
 - distributivity of $\cdot$ over $+\;$: i.e.  $\forall a,b,c \in R$ 
 $$a \cdot (b+c) = a \cdot b + a \cdot c \\ (a+b) \cdot c = a \cdot c + b \cdot c $$ 


We also have the following inclusions of classes of algebraic structures:

$$\begin{gather*}
\text{ring} & \supset & \text{commutative ring} \\
\cup&  & \\
\text{ring with 1} &\supset & \text{commutative ring with 1} \\
\cup & & \cup \\
\text{division ring} &\supset & \text{integral domain} \\
\cup \\
\text{field}
\end{gather*}
$$

We have that:
 - a **ring with 1** is a ring with a *multiplicative identity* (i.e. $\exists 1 \in R \; \forall a \in R (1 \cdot a = a \cdot 1 = a)$)
 - a **division ring** is a ring with 1 with *multiplicative inverses* for all non-zero elements (i.e. $\forall a\in R \; \exists a^{-1} \in R \;(a \cdot a^{-1} = a^{-1} \cdot a = 1)$)
 - a **field** is a division ring with *commutative multiplication*

### Magmas / Semigroups
Note that for any set $S$ with $|S| = n$, a closed operation $\cdot: S^2 \to S$ is essentially a function from the set 
$\underbrace{ \{ (1, 1), \cdots (1, n), \cdots (n,1), \cdots, (n,n)\} }_{n^2 \text{ elements}} \mapsto \{ 1 \cdots n \}\;\;$ - there are $n^{n^2}$ such functions.

A subset of these multiplications are associative. We use a similar approach to the [DPLL algorithm](https://en.wikipedia.org/wiki/DPLL_algorithm) to [count](./count_semigroups.py) all non-isomorphic semigroups of small orders:


```txt
Counted 1 semigroups of order 1 in 0:00:00.007976
Counted 5 semigroups of order 2 in 0:00:00.030633
Counted 24 semigroups of order 3 in 0:00:00.114370
Counted 188 semigroups of order 4 in 0:00:01
[+] Generating possible Cayley tables...
                             [+] Filtering out some isomorphic models
319484it [02:01, 2633.90it/s]                                                                                                         | 8692/115552 [00:02<00:32, 3282.46it/s]
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 115552/115552 [00:07<00:00, 16426.16it/s]
[+] Final isomorphism check
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1914/1914 [00:07<00:00, 251.59it/s]
Counted 1915 semigroups of order 5 in 0:02:13
[+] Generating possible Cayley tables...
29451749it [6:16:25, 274980.90it/s][+] Filtering out some isomorphic models
29539010it [6:18:27, 1300.83it/s]  
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 9267678/9267678 [24:55<00:00, 6198.24it/s]
[+] Final isomorphism check███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▉| 9267122/9267678 [24:55<00:00, 45100.98it/s]
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 28633/28633 [37:23<00:00, 12.76it/s]
Counted 28634 semigroups of order 6 in 7:18:51
```

We have the following values of a(n) = the number of semigroups of order n up to isomorphism:
| n    | a(n) | time | number of canidates |
|-|-|-|-|
|1|1|0.007s|n/a
|2|5|0.03s|n/a
|3|24|0.11s|172
|4|188|1s|5559
|5|1915|2m13s|115552
|6|28634|7:18:51s|29451749

We can also enumerate isomorphic semigroups with the more general tool [mace](http://google.com):

```sh
#!/bin/bash

LADR_PATH="./LADR-2009-11A"

check() {
    order=$1;
    echo "
assign(max_models, -1).
assign(domain_size, $order).

set(verbose).
set(trace).

formulas(assumptions).
    (x*y)*z = x*(y*z).
end_of_list.

formulas(goals).
end_of_list.
    " | tail -c +2 | \
       $LADR_PATH/bin/mace4 | \
       $LADR_PATH/bin/interpformat standard | \
       $LADR_PATH/bin/isofilter --ignore-constants
}

for n in $(seq 2 5); do
    echo "%", $n
    check $n;
done

```
```txt
$ ./gen_semigroup.sh |& grep "%"
%, 2
% isofilter --ignore-constants: input=8, kept=5, checks=8, erms=14, 0.00 seconds.
%, 3
% isofilter --ignore-constants: input=96, kept=24, checks=155, perms=230, 0.01 seconds.
%, 4
% isofilter --ignore-constants: input=2331, kept=188, checks=7217, perms=18071, 0.07 seconds.
%, 5
% isofilter --ignore-constants: input=90536, kept=1915, checks=556359, perms=1793809, 6.30 seconds.
```

We will use this program to investigate other kinds of algebraic structures,

### Small Groups
Using the code in the `./groups` folder of this directory (essentially a wrapper around LADR with isomorphism checking), we can enumerate all possible groups of order $\le 24$ in a reasonable amount of time

```txt
# time python3 example.py
# ...
Groups of order 2: [GroupInfo(id='[ 2, 1 ]', desc='C2')], in time 7.832343101501465 s
Groups of order 3: [GroupInfo(id='[ 3, 1 ]', desc='C3')], in time 0.7034687995910645 s
Groups of order 4: [GroupInfo(id='[ 4, 2 ]', desc='C2 x C2'), GroupInfo(id='[ 4, 1 ]', desc='C4')], in time 1.5505971908569336 s
Groups of order 5: [GroupInfo(id='[ 5, 1 ]', desc='C5')], in time 0.7036712169647217 s
Groups of order 6: [GroupInfo(id='[ 6, 1 ]', desc='S3'), GroupInfo(id='[ 6, 2 ]', desc='C6')], in time 1.39094877243042 s
Groups of order 7: [GroupInfo(id='[ 7, 1 ]', desc='C7')], in time 0.7122411727905273 s
Groups of order 8: [GroupInfo(id='[ 8, 5 ]', desc='C2 x C2 x C2'), GroupInfo(id='[ 8, 3 ]', desc='D8'), GroupInfo(id='[ 8, 2 ]', desc='C4 x C2'), GroupInfo(id='[ 8, 4 ]', desc='Q8'), GroupInfo(id='[ 8, 1 ]', desc='C8')], in time 3.3063130378723145 s
Groups of order 9: [GroupInfo(id='[ 9, 2 ]', desc='C3 x C3'), GroupInfo(id='[ 9, 1 ]', desc='C9')], in time 1.3442790508270264 s
Groups of order 10: [GroupInfo(id='[ 10, 1 ]', desc='D10'), GroupInfo(id='[ 10, 2 ]', desc='C10')], in time 1.421013593673706 s
Groups of order 11: [GroupInfo(id='[ 11, 1 ]', desc='C11')], in time 0.7484531402587891 s
Groups of order 12: [GroupInfo(id='[ 12, 4 ]', desc='D12'), GroupInfo(id='[ 12, 5 ]', desc='C6 x C2'), GroupInfo(id='[ 12, 3 ]', desc='A4'), GroupInfo(id='[ 12, 1 ]', desc='C3 : C4'), GroupInfo(id='[ 12, 2 ]', desc='C12')], in time 5.609140634536743 s
Groups of order 13: [GroupInfo(id='[ 13, 1 ]', desc='C13')], in time 0.8768317699432373 s
Groups of order 14: [GroupInfo(id='[ 14, 1 ]', desc='D14'), GroupInfo(id='[ 14, 2 ]', desc='C14')], in time 3.549271821975708 s
Groups of order 15: [GroupInfo(id='[ 15, 1 ]', desc='C15')], in time 42.58747839927673 s
Groups of order 16: [GroupInfo(id='[ 16, 14 ]', desc='C2 x C2 x C2 x C2'), GroupInfo(id='[ 16, 11 ]', desc='C2 x D8'), GroupInfo(id='[ 16, 10 ]', desc='C4 x C2 x C2'), GroupInfo(id='[ 16, 3 ]', desc='(C4 x C2) : C2'), GroupInfo(id='[ 16, 7 ]', desc='D16'), GroupInfo(id='[ 16, 8 ]', desc='QD16'), GroupInfo(id='[ 16, 12 ]', desc='C2 x Q8'), GroupInfo(id='[ 16, 2 ]', desc='C4 x C4'), GroupInfo(id='[ 16, 5 ]', desc='C8 x C2'), GroupInfo(id='[ 16, 6 ]', desc='C8 : C2'), GroupInfo(id='[ 16, 9 ]', desc='Q16'), GroupInfo(id='[ 16, 1 ]', desc='C16')], in time 520.2422976493835 s
Groups of order 17: [GroupInfo(id='[ 17, 1 ]', desc='C17')], in time 2.514155387878418 s
Groups of order 18: [GroupInfo(id='[ 18, 4 ]', desc='(C3 x C3) : C2'), GroupInfo(id='[ 18, 1 ]', desc='D18'), GroupInfo(id='[ 18, 3 ]', desc='C3 x S3'), GroupInfo(id='[ 18, 5 ]', desc='C6 x C3'), GroupInfo(id='[ 18, 2 ]', desc='C18')], in time 172.24005222320557 s
Groups of order 19: [GroupInfo(id='[ 19, 1 ]', desc='C19')], in time 7.11696195602417 s
Groups of order 20: [GroupInfo(id='[ 20, 4 ]', desc='D20'), GroupInfo(id='[ 20, 5 ]', desc='C10 x C2'), GroupInfo(id='[ 20, 3 ]', desc='C5 : C4'), GroupInfo(id='[ 20, 1 ]', desc='C5 : C4'), GroupInfo(id='[ 20, 2 ]', desc='C20')], in time 192.39055252075195 s
Groups of order 21: [GroupInfo(id='[ 21, 1 ]', desc='C7 : C3'), GroupInfo(id='[ 21, 2 ]', desc='C21')], in time 29.25878596305847 s
Groups of order 22: [GroupInfo(id='[ 22, 1 ]', desc='D22'), GroupInfo(id='[ 22, 2 ]', desc='C22')], in time 33.13249969482422 s
Groups of order 23: [GroupInfo(id='[ 23, 1 ]', desc='C23')], in time 31.336970806121826 s
Groups of order 24: [GroupInfo(id='[ 24, 14 ]', desc='C2 x C2 x S3'), GroupInfo(id='[ 24, 15 ]', desc='C6 x C2 x C2'), GroupInfo(id='[ 24, 13 ]', desc='C2 x A4'), GroupInfo(id='[ 24, 8 ]', desc='(C6 x C2) : C2'), GroupInfo(id='[ 24, 6 ]', desc='D24'), GroupInfo(id='[ 24, 12 ]', desc='S4'), GroupInfo(id='[ 24, 10 ]', desc='C3 x D8'), GroupInfo(id='[ 24, 5 ]', desc='C4 x S3'), GroupInfo(id='[ 24, 7 ]', desc='C2 x (C3 : C4)'), GroupInfo(id='[ 24, 9 ]', desc='C12 x C2'), GroupInfo(id='[ 24, 4 ]', desc='C3 : Q8'), GroupInfo(id='[ 24, 11 ]', desc='C3 x Q8'), GroupInfo(id='[ 24, 3 ]', desc='SL(2,3)'), GroupInfo(id='[ 24, 1 ]', desc='C3 : C8'), GroupInfo(id='[ 24, 2 ]', desc='C24')], in time 5111.373787164688 s

real    102m52.736s
user    4m8.469s
sys     0m14.156s
```

#### Note on Asymptotics

Cayley tables of higher order groups can be calculated but isomorphism checking becomes prohibitively costly - as an example, suppose we wanted to calculate all groups of order $2^n$ via this kind of brute force isomorphism checking. We would need to check $\text{gnu}(2^n)^2 \sim 2^{4n^3/27}$ pairs of groups for isomorphism - therefore, we have that the total computation would take 

$$\begin{align*}O( 2^{4n^3/27}  \cdot (2^n)!) &= O\left(2^{4n^3/27} \cdot \left( 2^{n/2} \cdot 2^{n 2^n} \cdot e^{-2^n} \right) \right) \\ &= \cdots = O(2^{n 2^n})\end{align*}$$

or superexponential in $n$. Therefore, this approach only works for very small $n$ (in my testing, I was able to only get this to work for $2^n = 32$).