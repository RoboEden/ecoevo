# An IP Model for automated trade matching

## parameters

| parameter | meaning |
| -- | -- |
| $N$ | the set of all offers |
| $a_{i, j}$ | if offer $i$ can match offer $j$ |
| $b_{i, j}$ | the trading volume between offer $i$ and offer $j$ |

## decision variables

| variable | type | meaning |
| -- | -- | -- |
| $x_{i, j}$ | bool | if choose offer $i$ to match offer $j$ |

## constraints

(1) validation:
$$ x_{i, j} \leq a_{i, j} \quad \forall i, j \in N $$

(2) symmetry:
$$ x_{i, j} = x_{j, i} \quad \forall i, j \in N $$

(3) match only once:
$$ \sum_{j \in N} x_{i, j} \leq 1 \quad \forall i \in N $$

## objective function

$$ \max \ \ \sum_{i \in N} \sum_{j \in N} \frac{1}{2} b_{i, j} x_{i, j} $$
