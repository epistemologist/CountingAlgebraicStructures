# Counting Algebraic Structures
Various notes/programs on counting different types of algebraic strucutres

## Definitions

For a set $S$ and a binary operation $ \cdot: S \times S \to S $, we have the following inclusions of classes of algebraic structures:
$$
\begin{gather*}
\text{magma} & & &\\
\cup & & & \\
\text{semigroup} &\supset &\text{commutative semigroup} \\
\cup & & & \\
\text{monoid} &\supset &\text{commutative monoid}\\
\cup & & & \\
\text{group} &\supset &\text{abelian/commutative group}
\end{gather*}
$$

 - a **magma** is a set $S$ with a *closed* binary operation (i.e. $\forall a,b \in S \; . \; a \cdot b \in S $)
 - a **semigroup** is a magma with an *associative* operation (i.e. $\forall a,b,c \in S  \; . \;  (a \cdot b ) \cdot c = a \cdot (b \cdot c)  $ )
 - a **monoid** is a semigroup with an *identity* element (i.e. $\exists e \in S \;  \forall a \in S \; . \; (e \cdot a = a \cdot e = a )$)
 - a **group** is a monoid with *inverses* (i.e. $ \forall  a \in S \; \exists a^{-1} \in S \; . \; (a \cdot a^{-1} = a^{-1} \cdot a = e )  $)


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

A subset of these multiplications are associative.  
