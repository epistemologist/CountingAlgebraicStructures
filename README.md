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
 - a **division ring** is a ring with 1 with *multiplicative inverses* for all non-zero elements (i.e. $\forall  a\in R \exists a^{-1} \in R \; (a \cdot a^{-1} = a^{-1} \cdot a = 1 )$)
 - a **field** is a division ring with *commutative multiplication*

### Magmas
Note that for any set $S$ with $|S| = n$, a closed operation $\cdot: S^2 \to S $ is essentially a function from the set $\underbrace{ \{ (1, 1), \cdots (1, n), \cdots (n,1), \cdots, (n,n)\} }_{n^2 \text{ elements}} \mapsto \{ 1 \cdots n \}$ - there are $n^{n^2}$ such functions.

A subset of these multiplications are associative. We use a similar approach to the [DPLL algorithm](https://en.wikipedia.org/wiki/DPLL_algorithm) to [count](./count_semigroups.py) all non-isomorphic semigroups of small orders:

```python
   ...: for n in range(1, 7):                                                                                                                 
   ...:     X = number_of_semigroups(n,  suppress_output=(n<5))                                                                               
   ...:                                                      
Counted 1 of order 1 in 0:00:00.001019                                 
Counted 5 of order 2 in 0:00:00.001440                                 
Counted 24 of order 3 in 0:00:00.024050                                                                                                       
Counted 188 of order 4 in 0:00:02                                      
[+] Generating possible Cayley tables...                               
319484it [03:44, 1422.24it/s]                                                                                                                 
[+] Filtering out some isomorphic models                               
100%|██████████████████████████████████████████████████████████████████████████████████████████████| 115552/115552 [00:05<00:00, 22491.26it/s]
[+] Final isomorphism check                                                                                                                   
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████| 1914/1914 [06:13<00:00,  5.13it/s]
Counted 1915 of order 5 in 0:10:05
```

```
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