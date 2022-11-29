# An IP Model for automated mixed trades

## parameters

| parameter | meaning |
| -- | -- |
| $M$ | the set of offers |
| $N$ | the set of items |
| $a_{i, j}$ | the number of item $j$ to buy in offer $i$ |
| $b_{i, j}$ | the number of item $j$ to sell in offer $i$ |
| $j^{in}_i$ | the item to buy in offer $i$ |
| $j^{out}_i$ | the item to sell in offer $i$ |

## decision variables

| variable | type | meaning |
| -- | -- | -- |
| $x_{i, j}$ | $Z^0_+$ | the number of item $j$ to buy assigned to offer $i$ |
| $y_{i, j}$ | $Z^0_+$ | the number of item $j$ to sell assigned to offer $i$ |

## constraints

(1) no more than demands:
$$ x_{i, j} \leq a_{i, j} \quad \forall i \in M \quad \forall j \in N 
\\ y_{i, j} \leq b_{i, j} \quad \forall i \in M \quad \forall j \in N $$

(2) balance:
$$ \sum_{i \in M} x_{i, j} = \sum_{i \in M} y_{i, j} \quad \forall j \in N $$

(3) proportion:
$$ \frac {x_{i, j^{in}_i}} {a_{i, j^{in}_i}} = \frac {y_{i, j^{out}_i}} {b_{i, j^{out}_i}} \quad \forall i \in M $$

## objective function
$$ \max \ \ \sum_{i \in M} \sum_{j \in N} x_{i, j} $$
